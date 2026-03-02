# D&D 剧情顾问 (DM Agent) 升级技术方案

## 1. 设计哲学：提案-仲裁机制 (Proposal-Arbitration Pattern)

在复杂的规则系统（如 D&D 5E）中，AI 直接修改底层数据往往会因为理解偏差导致“坏档”。本方案引入**提案-仲裁机制**，将规则解释与状态变更解耦。

### 核心原则
- **DM Agent 仅读权限**：Agent 可以读取人物卡和历史日志，但严禁通过工具直接修改数据库。
- **结构化提案 (Proposal)**：Agent 的输出不再仅仅是文本，而是在回复中包含一个结构化的 `Proposal JSON`。
- **颗粒度仲裁 (Granular Arbitration)**：提案中的变更项必须是**独立的**。用户有权选择性接受部分项（例如：接受 HP 变动，但拒绝 道具 变动）。
- **用户仲裁 (Arbitration)**：前端负责解析 JSON 并渲染为“变更确认卡片”。只有当用户（玩家/DM）点击确认后，数据变更才会通过 API 写入。

---

## 2. 交互协议定义

### 2.1 提案数据格式 (Proposal JSON)
为了确保 Agent 输出的结构可预测且符合逻辑，系统采用 **Pydantic 模型** 定义 Schema。Agent 的响应被约束为以下结构：

```json
{
  "thought": "对当前局势的逻辑分析...",
  "response": "直接回复给用户的自然语言文本...",
  "proposals": [
    {
      "id": "uuid-1",
      "type": "STAT_CHANGE", 
      "target": "hp",
      "value": -5,
      "reason": "受到火球术伤害",
      "metadata": { "damage_type": "fire" }
    },
    {
      "id": "uuid-2",
      "type": "LOG_ENTRY",
      "content": "在耐色瑞尔遗迹中触发了陷阱，失去 5 点生命值。"
    }
  ]
}
```

### 2.2 流程说明 (含部分接受逻辑)
1. **推理与生成**：Agent 基于当前状态生成 `proposals` 列表。
2. **前端渲染**：UI 将每个提案项渲染为带有**复选框**的列表。
3. **选择性应用**：
   - 用户勾选想要应用的变更项。
   - 前端调用 API 仅发送已勾选的 `id` 对应的提案。
4. **状态反馈同步**：
   - 应用成功后，前端自动向 Agent 发送一条隐藏指令（如：`[System] 用户接受了变更 A，但拒绝了变更 B`）。
   - Agent 更新其短期记忆，确保后续推理基于真实的数据库状态。

### 2.3 提案校验机制 (Proposal Validation)
为防止 AI 幻觉导致的格式错误或逻辑异常，引入以下四层防线：

1. **结构化输出 (Structured Output)**：利用 Gemini 的 `.with_structured_output()` 特性，在模型层强制要求输出符合 JSON Schema。
2. **静态校验 (Pydantic Check)**：后端接收到 Agent 输出后，立即通过 Pydantic 模型进行类型检查（如：`value` 是否为数字，`type` 是否在允许的枚举值内）。
3. **逻辑闭环 (Self-Correction Loop)**：在 LangGraph 中增加 `validator` 节点。若校验失败，将错误信息（如 `Field 'target' is missing`）作为反馈喂回给 Agent，触发自动重试（上限 2 次）。
4. **受限词表 (Allowed Vocabulary)**：定义严格的 `target` 映射表（例如：属性缩写必须为 `str`, `dex`, `con` 等），超出范围的提案将被拦截。

---

## 3. 记忆管理方案

### 3.1 短期记忆 (Short-term)
- **载体**：LangGraph `State` + `MemorySaver` (Checkpointer)。
- **内容**：当前会话的消息流、最近的推理链。
- **作用**：确保对话的连贯性，避免复读。

### 3.2 长期记忆 (Long-term: Campaign Logs)
- **载体**：ChromaDB 新集合 `campaign_logs`。
- **技术实现**：
  - 每当发生重大事件（用户确认提案后），将事件描述、时间戳、游戏内天数存入向量库。
  - **检索增强 (RAG)**：Agent 在思考前，先检索最近或相关的日志片段，了解“之前发生了什么”。
- **元数据**：`{"session_id": "...", "importance": 1-5, "type": "combat/rp/loot"}`。

---

## 4. 后端架构调整

### 4.1 LangGraph 状态升级
```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    selected_books: list[str]
    character_data: Dict[str, Any]
    relevant_logs: list[str]  # 从 ChromaDB 检索出的历史背景
```

### 4.2 工具集扩展
- `search_rules`: (现有) 语义检索。增加 `is_index: false` 默认过滤，防止模型陷入目录页。
- `fetch_rule_content`: (新增) 精确提取。支持通过 `title`、`chapter` 或 `id` 直接定位正文，完全跳过向量搜索。
- `search_logs`: (新增) 检索战役历史日志，提供上下文背景。

### 4.3 Prompt 策略
... (此处略)

### 4.4 检索质量保障：规避“索引陷阱”
针对向量数据库中目录页（ToC）干扰正文检索及 HTML 链接丢失的问题，采取以下措施：

1. **结构化导航恢复 (Link-to-Metadata)**：
   - 在 ETL 阶段，解析 HTML 中的 `<a>` 标签，提取其 `href`（锚点）或 `title`。
   - 将提取出的目标标识符存入元数据 `points_to` 字段。
   - **效果**：即使文本中没有链接，Agent 也能通过元数据感知“火球术”这一行指向的是哪个具体的规则条目。

2. **元数据隔离**：
   - 在入库环节对目录页标注 `is_index: true`。`search_rules` 工具默认屏蔽此类片段，除非 Agent 明确要求检索索引。

3. **多级检索 (Reranking)**：
   - ... (保持不变)

4. **Agent 导航模式 (Jump-to-Content)**：
   - 训练 Agent 识别“检索到目录”的状态。
   - **逻辑执行**：若返回结果命中目录且包含 `points_to` 元数据，Agent 必须自动利用该标识符发起 `fetch_rule_content` 调用，实现从“索引”到“正文”的无缝跳转。

---

## 5. 路线图 (Roadmap)

1. **Phase 1: 协议标准化**
   - 修改 `src/agent/graph.py` 的 System Prompt，训练其输出 Proposal JSON。
   - 前端增加确认卡片组件（Vue）。
2. **Phase 2: 长期记忆接入**
   - 在 `src/db/` 下增加日志存储脚本。
   - 为 Agent 增加 `search_logs` 工具。
3. **Phase 3: 闭环验证**
   - 测试“受到伤害 -> 生成提案 -> 点击确认 -> 属性变动 -> 日志存档”的全链路。

---

**备注**：本设计确保了规则执行的严肃性，同时保留了 DM 的最终决定权，防止 AI 幻觉破坏游戏平衡。
