import { Send } from 'lucide-react'
import { useState, useRef, useEffect, type KeyboardEvent } from 'react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled: boolean
  placeholder?: string
}

export default function MessageInput({ onSend, disabled, placeholder }: MessageInputProps) {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }

  useEffect(() => {
    adjustHeight()
  }, [text])

  const handleSend = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="p-4 bg-chat-bg border-t border-chat-border shadow-[0_-4px_20px_rgba(0,0,0,0.02)] z-10 relative">
      <div className="flex items-end gap-3 max-w-5xl mx-auto">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || '输入消息...'}
          disabled={disabled}
          className="flex-1 max-h-48 min-h-[44px] p-3 rounded-xl bg-chat-hover text-[15px] text-chat-text placeholder:text-chat-text-secondary outline-none resize-none focus:bg-white focus:ring-2 focus:ring-chat-accent focus:ring-opacity-20 transition-all disabled:opacity-50"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="h-[44px] w-[44px] flex items-center justify-center rounded-full bg-chat-accent text-white shrink-0 hover:opacity-90 disabled:opacity-50 disabled:hover:opacity-50 transition-all shadow-md hover:shadow-lg transform active:scale-95"
        >
          <Send size={18} className="ml-0.5" />
        </button>
      </div>
    </div>
  )
}
