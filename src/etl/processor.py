import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置路径
BASE_DIR = Path(__file__).resolve().parents[2]  # 回退两级到项目根目录
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = PROCESSED_DATA_DIR / "dnd_knowledge_base.jsonl"


def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "meta", "link", "noscript", "iframe"]):
        tag.decompose()
    for div in soup.find_all("div", class_="footer"):
        div.decompose()
    return soup


def post_process_markdown(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("if !supportLists·endif", "").replace("if !supportLists", "")
    if text.strip().startswith("coding:"):
        text = "\n".join(text.split("\n")[1:])
    if text.strip().endswith("EndFragment"):
        text = text[: text.rfind("EndFragment")]
    text = text.replace("’", "'")
    return text.strip()


def convert_to_markdown(soup):
    markdown_text = md(str(soup), strip=["a", "img"], heading_style="ATX")
    return post_process_markdown(markdown_text)


def split_markdown_by_headers(markdown_text, metadata):
    chunks = []
    lines = markdown_text.split("\n")
    current_chunk = []
    current_header = metadata.get("chapter", "Unknown")

    for line in lines:
        if line.strip().startswith(("# ", "## ", "### ")):
            if current_chunk:
                text_content = "\n".join(current_chunk).strip()
                if len(text_content) > 50:
                    chunks.append(
                        {
                            "page_content": text_content,
                            "metadata": {**metadata, "sub_topic": current_header},
                        }
                    )
            current_header = line.strip().lstrip("#").strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        text_content = "\n".join(current_chunk).strip()
        if len(text_content) > 50:
            chunks.append(
                {
                    "page_content": text_content,
                    "metadata": {**metadata, "sub_topic": current_header},
                }
            )
    return chunks


def read_file_content(file_path):
    encodings = ["utf-8", "gb18030", "gbk", "latin-1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    print(f"⚠️ 警告: 无法识别文件编码 {file_path.name}，尝试忽略错误读取。")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def process_all_files():
    if not RAW_DATA_DIR.exists():
        print(f"错误: 找不到原始数据目录 {RAW_DATA_DIR}")
        return

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    total_chunks = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        # 递归遍历 raw 下的所有 htm 文件
        for file_path in RAW_DATA_DIR.rglob("**/*.htm*"):
            if file_path.is_dir():
                continue

            try:
                # 获取相对于 raw 的完整路径，例如 "核心规则/玩家手册2024/03_职业/野蛮人.htm"
                relative_file_path = file_path.relative_to(RAW_DATA_DIR)
                full_parts = relative_file_path.parts

                # 分离目录部分
                dir_parts = full_parts[:-1]

                # 1. 计算 source_book (前两级目录)
                if len(dir_parts) >= 2:
                    source_book = f"{dir_parts[0]}/{dir_parts[1]}"
                    book_depth = 2
                elif len(dir_parts) == 1:
                    source_book = dir_parts[0]
                    book_depth = 1
                else:
                    source_book = "Uncategorized"
                    book_depth = 0

                # 2. 计算 chapter (剩余路径 + 文件名Stem)
                # [核心修改] 逻辑：full_parts[book_depth:] 就是被 source_book 截断剩下的部分
                # 例如：full_parts = ("核心规则", "玩家手册2024", "03_职业", "野蛮人.htm")
                # source_book 占了前2个
                # chapter_parts = ("03_职业", "野蛮人.htm")

                chapter_parts = list(full_parts[book_depth:])

                if chapter_parts:
                    # 将最后一部分 (文件名) 替换为不带后缀的 Stem，如 "野蛮人.htm" -> "野蛮人"
                    chapter_parts[-1] = file_path.stem
                    # 用 "/" 拼接，变成 "03_职业/野蛮人"
                    chapter = "/".join(chapter_parts)
                else:
                    chapter = file_path.stem

            except ValueError:
                source_book = "Unknown"
                chapter = file_path.stem

            # 调试打印 (可选)
            print(f"Book: {source_book} | Chapter: {chapter}")

            try:
                content = read_file_content(file_path)
                if not content:
                    continue

                base_metadata = {
                    "source_book": source_book,
                    "chapter": chapter,  # [修改点] 这里现在包含了完整的子路径信息
                    "filename": file_path.name,
                }

                soup = clean_html(content)
                md_text = convert_to_markdown(soup)
                chunks = split_markdown_by_headers(md_text, base_metadata)

                for chunk in chunks:
                    f_out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    total_chunks += 1

            except Exception as e:
                print(f"处理文件 {file_path.name} 失败: {str(e)}")

    print(f"\n处理完成! 共生成 {total_chunks} 个数据块。")
    print(f"输出文件: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_all_files()
