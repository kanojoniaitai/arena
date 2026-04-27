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

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sender?: string
  display_name?: string
  avatar?: string
  timestamp: number
}

export type ChatType = 'private' | 'group'

export interface Conversation {
  id: string
  type: ChatType
  name: string
  model_name?: string
  group_id?: string
  messages: ChatMessage[]
  isStreaming: boolean
}

export type WSMessage =
  | { type: 'chat'; chat_type: ChatType; model_name?: string; group_id?: string; message: string; history: { role: string; content: string; sender?: string; display_name?: string }[] }
  | { type: 'ai_stream_token'; model_name: string; token: string }
  | { type: string; model_name?: string; token?: string; display_name?: string; [key: string]: any }
  | { type: 'ai_complete'; model_name: string }
  | { type: 'group_reply'; model_name: string; display_name?: string; content: string }
  | { type: 'group_complete' }
  | { type: 'error'; message: string }
