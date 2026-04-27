export interface ModelInfo {
  name: string
  display_name: string
  avatar: string
  system_prompt: string
  params: string
  quant: string
  size_gb: number
  temperature: number
  max_tokens: number
  top_p: number
  repeat_penalty: number
}

export interface GroupInfo {
  id: string
  name: string
  members: string[]
}

export interface DebateInfo {
  id: string
  topic: string
  pro_model: string
  con_model: string
  max_rounds: number
  current_round: number
  pro_score: number
  con_score: number
}

export interface StoryInfo {
  id: string
  name: string
  members: string[]
}

export interface UndercoverInfo {
  id: string
  name: string
  members: string[]
  civilian_word: string
  undercover_word: string
  undercover_indices: number[]
  current_round: number
  phase: 'describe' | 'vote'
  eliminated: string[]
  game_over: boolean
  winner: string | null
}

export interface WerewolfInfo {
  id: string
  name: string
  members: string[]
  roles: Record<string, string>
  current_round: number
  phase: 'night' | 'day'
  sub_phase: string
  eliminated: string[]
  witch_save_used: boolean
  witch_poison_used: boolean
  game_over: boolean
  winner: string | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sender?: string
  display_name?: string
  avatar?: string
  timestamp: number
  side?: 'pro' | 'con'
  round?: number
  turn?: number
  phase?: string
  sub_phase?: string
  is_undercover?: boolean
  werewolf_role?: string
}

export type ChatType = 'private' | 'group' | 'debate' | 'story' | 'undercover' | 'werewolf'

export interface Conversation {
  id: string
  type: ChatType
  name: string
  model_name?: string
  group_id?: string
  debate_id?: string
  story_id?: string
  undercover_id?: string
  werewolf_id?: string
  pro_model?: string
  con_model?: string
  topic?: string
  current_round?: number
  max_rounds?: number
  pro_score?: number
  con_score?: number
  civilian_word?: string
  undercover_word?: string
  undercover_indices?: number[]
  undercover_phase?: 'describe' | 'vote'
  eliminated?: string[]
  game_over?: boolean
  winner?: string | null
  werewolf_phase?: 'night' | 'day'
  werewolf_sub_phase?: string
  werewolf_roles?: Record<string, string>
  messages: ChatMessage[]
  isStreaming: boolean
}

export type WSMessage =
  | { type: 'chat'; chat_type: ChatType; model_name?: string; group_id?: string; debate_id?: string; story_id?: string; undercover_id?: string; werewolf_id?: string; message: string; history: { role: string; content: string; sender?: string; display_name?: string; side?: string }[] }
  | { type: 'ai_stream_token'; model_name: string; token: string }
  | { type: 'ai_complete'; model_name: string }
  | { type: 'group_reply'; model_name: string; display_name?: string; content: string }
  | { type: 'group_complete' }
  | { type: 'debate_reply'; model_name: string; display_name?: string; content: string; side: 'pro' | 'con'; round: number }
  | { type: 'debate_round_complete'; round: number }
  | { type: 'story_reply'; model_name: string; display_name?: string; content: string; turn: number }
  | { type: 'story_cycle_complete' }
  | { type: 'undercover_reply'; model_name: string; display_name?: string; content: string; round: number; phase: string; is_undercover: boolean }
  | { type: 'undercover_phase_complete'; round: number; phase: string }
  | { type: 'werewolf_reply'; model_name: string; display_name?: string; content: string; role: string; phase: string; sub_phase: string; round: number }
  | { type: 'werewolf_phase_complete'; phase: string; sub_phase: string; round: number }
  | { type: 'error'; message: string }
