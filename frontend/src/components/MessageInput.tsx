import { Send } from 'lucide-react'
import { useState, type KeyboardEvent } from 'react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled: boolean
  placeholder?: string
}

export default function MessageInput({ onSend, disabled, placeholder }: MessageInputProps) {
  const [text, setText] = useState('')

  const handleSend = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex items-end gap-2 p-3 bg-wechat-sidebar border-t border-wechat-border">
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || '输入消息...'}
        rows={2}
        disabled={disabled}
        className="flex-1 resize-none rounded-md px-3 py-2 text-sm text-wechat-text bg-white outline-none placeholder:text-wechat-text-secondary disabled:opacity-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        className="p-2 rounded-md bg-wechat-green text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-wechat-green-dark transition-colors shrink-0"
      >
        <Send size={18} />
      </button>
    </div>
  )
}
