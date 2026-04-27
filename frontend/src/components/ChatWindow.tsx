import { useEffect, useRef } from 'react'
import { Settings, Trash2 } from 'lucide-react'
import type { Conversation, ModelInfo, ChatMessage } from '../types'
import MessageInput from './MessageInput'

interface ChatWindowProps {
  conversation: Conversation | null
  models: ModelInfo[]
  onSendMessage: (message: string) => void
  onOpenSettings: () => void
  onClearHistory?: () => void
}

function formatTime(ts: number): string {
  const d = new Date(ts)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function shouldShowTime(msg: ChatMessage, prev: ChatMessage | undefined): boolean {
  if (!prev) return true
  return msg.timestamp - prev.timestamp > 5 * 60 * 1000
}

function getModelDisplayName(models: ModelInfo[], modelName: string): string {
  return models.find(m => m.name === modelName)?.display_name || modelName
}

function getModelAvatar(models: ModelInfo[], modelName: string): string {
  return models.find(m => m.name === modelName)?.avatar || '🤖'
}

export default function ChatWindow({ conversation, models, onSendMessage, onOpenSettings, onClearHistory }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages, conversation?.isStreaming])

  if (!conversation) {
    return (
      <div className="flex-1 bg-chat-bg flex items-center justify-center border-l border-chat-border">
        <div className="text-center">
          <div className="w-16 h-16 bg-chat-hover rounded-full flex items-center justify-center mx-auto mb-4 text-2xl shadow-sm border border-chat-border">
            ✨
          </div>
          <p className="text-chat-text-secondary font-medium tracking-wide">选择一个模型或群聊开始对话</p>
        </div>
      </div>
    )
  }

  const activeModel = conversation.type === 'private'
    ? models.find(m => m.name === conversation.model_name)
    : null

  const renderHeader = () => {
    let title = conversation.name
    let subtitle = ''

    if (conversation.type === 'group') {
      subtitle = '群聊 · 角色间可互相回应'
    }

    return (
      <div className="flex items-center justify-between px-6 py-4 bg-chat-bg border-b border-chat-border shadow-sm z-10 relative">
        <div className="flex-1 min-w-0">
          <span className="text-lg font-semibold tracking-tight text-chat-text">{title}</span>
          {subtitle && <span className="text-xs text-chat-text-secondary ml-3 font-medium bg-chat-hover px-2 py-1 rounded-full">{subtitle}</span>}
        </div>
        <div className="flex items-center gap-2">
          {activeModel && (
            <button
              onClick={onOpenSettings}
              className="p-2 rounded-lg hover:bg-chat-hover text-chat-text-secondary transition-colors"
              title="模型设置"
            >
              <Settings size={18} />
            </button>
          )}
          {onClearHistory && (
            <button
              onClick={onClearHistory}
              className="p-2 rounded-lg hover:bg-chat-hover text-chat-text-secondary transition-colors"
              title="清空聊天记录"
            >
              <Trash2 size={18} />
            </button>
          )}
        </div>
      </div>
    )
  }

  const renderMessage = (msg: ChatMessage, index: number) => {
    const isSelf = msg.role === 'user'
    const prevMsg = index > 0 ? conversation.messages[index - 1] : undefined
    const showTime = shouldShowTime(msg, prevMsg)
    const showAvatar = conversation.type !== 'private' || !isSelf

    return (
      <div key={msg.id} className="mb-6">
        {showTime && (
          <div className="flex justify-center mb-6 mt-2">
            <span className="text-[11px] font-medium tracking-widest uppercase text-chat-text-secondary bg-chat-hover px-3 py-1 rounded-full">{formatTime(msg.timestamp)}</span>
          </div>
        )}
        <div className={`flex items-end gap-3 ${isSelf ? 'flex-row-reverse' : ''}`}>
          {showAvatar && (
            <div className={`w-9 h-9 rounded-full flex items-center justify-center text-lg shrink-0 shadow-sm border ${isSelf ? 'bg-chat-accent text-white border-chat-accent' : 'bg-chat-bg border-chat-border'}`}>
              {isSelf ? '👤' : (msg.avatar || (msg.sender ? getModelAvatar(models, msg.sender) : '🤖'))}
            </div>
          )}
          <div className={`flex flex-col ${isSelf ? 'items-end' : 'items-start'} max-w-[75%]`}>
            {conversation.type !== 'private' && !isSelf && (
              <span className="text-[11px] font-medium text-chat-text-secondary mb-1.5 ml-1 uppercase tracking-wider">
                {msg.display_name || (msg.sender ? getModelDisplayName(models, msg.sender) : 'AI')}
              </span>
            )}
            <div className={`px-5 py-3.5 rounded-2xl whitespace-pre-wrap break-words text-[15px] leading-relaxed shadow-sm transition-all hover:shadow-md ${
              isSelf 
                ? 'bg-chat-bubble-user text-chat-bubble-user-text rounded-br-sm' 
                : 'bg-chat-bubble-bot text-chat-bubble-bot-text rounded-bl-sm border border-chat-border'
            }`}>
              {msg.content}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-chat-bg border-l border-chat-border relative">
      {renderHeader()}
      <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
        {conversation.messages.map((msg, index) => renderMessage(msg, index))}
        {conversation.isStreaming && (
          <div className="flex items-end gap-3 mt-6 mb-2">
            <div className="w-9 h-9 rounded-full bg-chat-bg flex items-center justify-center text-lg shrink-0 shadow-sm border border-chat-border">
              🤖
            </div>
            <div className="px-5 py-4 rounded-2xl bg-chat-bubble-bot shadow-sm rounded-bl-sm border border-chat-border">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-chat-text-secondary rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-chat-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-2 h-2 bg-chat-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-4" />
      </div>
      <MessageInput 
        onSend={onSendMessage} 
        disabled={conversation.isStreaming}
        placeholder={conversation.isStreaming ? "AI 正在回复..." : "输入消息，Enter 发送，Shift+Enter 换行..."}
      />
    </div>
  )
}