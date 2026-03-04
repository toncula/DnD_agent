export interface BookNode {
  label: string;
  value: string;
  children?: BookNode[];
}

export interface BookTreeResponse {
  nodes: BookNode[];
  valid_paths: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ToolLog {
  type: string;
  content: string;
}

export interface ChatResponse {
  response: string;
  logs: ToolLog[];
}

export interface ItemAction {
  name: string;
  activation: string;
  description: string;
}

export interface InventoryItem {
  name: string;
  quantity: number;
  weight: number;
  category: '装备' | '消耗品' | '杂物';
  item_type: string;
  slot_type: string;
  is_equipped: boolean;
  is_proficient: boolean;
  description: string;
  rarity: string;
  requires_attunement: boolean;
  is_attuned: boolean;
  properties: string[];
  damage_dice: string;
  damage_type: string;
  attack_bonus: number;
  damage_bonus: number;
  weapon_mastery?: string;
  special_actions?: ItemAction[];
  ac_base?: number;
  ac_bonus: number;
  dex_cap?: number;
  strength_req: number;
  stealth_disadv: boolean;
  derived_attack_roll: string;
  derived_damage_roll: string;
}

export interface CharacterSheetData {
  bio: any;
  prog: any;
  combat: any;
  inventory: InventoryItem[];
  total_weight: number;
  carrying_capacity: number;
  features: any[];
  spells: any[];
  spellcasting: any;
  [key: string]: any;
}
