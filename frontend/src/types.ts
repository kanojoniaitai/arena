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

export interface WSStreamTokenMessage {
  type: 'ai_stream_token' | 'group_stream_token' | 'story_stream_token' | 'undercover_stream_token' | 'werewolf_stream_token' | 'debate_stream_token';
  model_name: string;
  token: string;
  display_name?: string;
}

export interface WSCompleteMessage {
  type: 'ai_complete' | 'group_complete' | 'story_complete' | 'undercover_complete' | 'werewolf_complete' | 'debate_complete';
  model_name?: string;
}

export interface WSErrorMessage {
  type: 'error';
  message: string;
}

export interface WSChatMessage {
  type: 'chat';
  chat_type: ChatType;
  model_name?: string;
  group_id?: string;
  message: string;
  history: { role: string; content: string; sender?: string; display_name?: string }[];
}

export interface WSGroupReplyMessage {
  type: 'group_reply';
  model_name: string;
  display_name?: string;
  content: string;
}

export type WSMessage =
  | WSChatMessage
  | WSStreamTokenMessage
  | WSCompleteMessage
  | WSGroupReplyMessage
  | WSErrorMessage
