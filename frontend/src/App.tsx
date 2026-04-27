import { useState, useEffect, useCallback } from 'react'
import type { ModelInfo, GroupInfo, Conversation, ChatMessage } from './types'
import { useChatSocket } from './hooks/useChatSocket'
import ContactList from './components/ContactList'
import ChatWindow from './components/ChatWindow'
import ModelSettings from './components/ModelSettings'
import CreateGroupModal from './components/CreateGroupModal'

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

function generateId(): string {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36)
}

export default function App() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [groups, setGroups] = useState<GroupInfo[]>([])
  const [conversations, setConversations] = useState<Map<string, Conversation>>(new Map())
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [settingsModel, setSettingsModel] = useState<ModelInfo | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [createGroupOpen, setCreateGroupOpen] = useState(false)

  const { lastMessage, sendMessage, isConnected } = useChatSocket()

  const fetchModels = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/models`)
      const data = await res.json()
      setModels(data)
    } catch {
    }
  }, [])

  const fetchGroups = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/groups`)
      const data = await res.json()
      setGroups(data)
    } catch {
    }
  }, [])

  useEffect(() => {
    fetchModels()
    fetchGroups()
  }, [fetchModels, fetchGroups])

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/history`)
        const history = await res.json()
        const convs = new Map<string, Conversation>()
        for (const [convId, messages] of Object.entries(history)) {
          const isPrivate = convId.startsWith('private-')
          const isGroup = convId.startsWith('group-')
          if (isPrivate) {
            const modelName = convId.replace('private-', '')
            const model = models.find(m => m.name === modelName)
            convs.set(convId, {
              id: convId,
              type: 'private',
              name: model?.display_name || modelName,
              model_name: modelName,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          } else if (isGroup) {
            const groupId = convId.replace('group-', '')
            const group = groups.find(g => g.id === groupId)
            convs.set(convId, {
              id: convId,
              type: 'group',
              name: group?.name || '群聊',
              group_id: groupId,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          }
        }
        setConversations(convs)
      } catch {
      }
    }
    loadHistory()
  }, [models, groups])

  useEffect(() => {
    const saveHistory = async () => {
      const history: Record<string, ChatMessage[]> = {}
      conversations.forEach((conv, id) => {
        if (conv.messages.length > 0) {
          history[id] = conv.messages
        }
      })
      try {
        await fetch(`${API_BASE}/api/history/batch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ history }),
        })
      } catch {
      }
    }
    
    const timeoutId = setTimeout(saveHistory, 2000)
    return () => clearTimeout(timeoutId)
  }, [conversations])

  useEffect(() => {
    if (!lastMessage || !activeConvId) return

    const activeConv = conversations.get(activeConvId)
    if (!activeConv) return

    // 处理流式 token 消息
    if (lastMessage.type === 'ai_stream_token' || lastMessage.type.endsWith('_stream_token')) {
      const msg = lastMessage as { type: string; model_name: string; token: string; display_name?: string }
      const isPrivateStream = lastMessage.type === 'ai_stream_token' && activeConv.type === 'private' && activeConv.model_name === msg.model_name
      const isGroupStream = lastMessage.type === 'group_stream_token' && activeConv.type === 'group'
      
      if (isPrivateStream || isGroupStream) {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          const msgs = [...conv.messages]
          const lastMsg = msgs[msgs.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && lastMsg.sender === msg.model_name) {
            msgs[msgs.length - 1] = { ...lastMsg, content: lastMsg.content + msg.token }
          } else {
            const model = models.find(m => m.name === msg.model_name)
            msgs.push({
              id: generateId(),
              role: 'assistant',
              content: msg.token,
              sender: msg.model_name,
              display_name: msg.display_name || model?.display_name,
              avatar: model?.avatar || '🤖',
              timestamp: Date.now(),
            })
          }
          next.set(activeConvId!, { ...conv, messages: msgs, isStreaming: true })
          return next
        })
      }
    } else if (lastMessage.type === 'ai_complete') {
      const msg = lastMessage as { type: 'ai_complete'; model_name: string }
      if (activeConv.type === 'private' && activeConv.model_name === msg.model_name) {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'group_complete') {
      if (activeConv.type === 'group') {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'error') {
      const msg = lastMessage as { type: 'error'; message: string }
      const errorMsg: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `⚠️ 错误: ${msg.message}`,
        timestamp: Date.now(),
      }
      setConversations(prev => {
        const next = new Map(prev)
        const conv = next.get(activeConvId!)
        if (!conv) return prev
        next.set(activeConvId!, { ...conv, messages: [...conv.messages, errorMsg], isStreaming: false })
        return next
      })
    }
  }, [lastMessage, activeConvId, models])

  const handleSelectContact = useCallback((conv: Conversation) => {
    setConversations(prev => {
      const next = new Map(prev)
      if (!next.has(conv.id)) {
        next.set(conv.id, conv)
      }
      return next
    })
    setActiveConvId(conv.id)
  }, [])

  const handleSendMessage = useCallback((message: string) => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv) return

    const userMsg: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: message,
      timestamp: Date.now(),
    }

    const updatedMessages = [...conv.messages, userMsg]

    setConversations(prev => {
      const next = new Map(prev)
      next.set(activeConvId, { ...conv, messages: updatedMessages, isStreaming: true })
      return next
    })

    const history = conv.messages.map(m => ({
      role: m.role,
      content: m.content,
      sender: m.sender,
      display_name: m.display_name,
    }))

    sendMessage(conv.type, conv.model_name, conv.group_id, message, history)
  }, [activeConvId, conversations, sendMessage])

  const handleOpenSettings = useCallback(() => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'private') return
    const model = models.find(m => m.name === conv.model_name)
    if (model) {
      setSettingsModel(model)
      setSettingsOpen(true)
    }
  }, [activeConvId, conversations, models])

  const handleSaveSettings = useCallback(async (name: string, avatar: string, systemPrompt: string, displayName: string, params: {
    temperature: number
    max_tokens: number
    top_p: number
    repeat_penalty: number
  }) => {
    try {
      await fetch(`${API_BASE}/api/models/${encodeURIComponent(name)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          avatar, 
          system_prompt: systemPrompt, 
          display_name: displayName,
          temperature: params.temperature,
          max_tokens: params.max_tokens,
          top_p: params.top_p,
          repeat_penalty: params.repeat_penalty,
        }),
      })
      await fetchModels()
      setSettingsOpen(false)
    } catch {
    }
  }, [fetchModels])

  const handleClearHistory = useCallback(() => {
    if (!activeConvId) return
    setConversations(prev => {
      const next = new Map(prev)
      const conv = next.get(activeConvId)
      if (conv) {
        next.set(activeConvId, { ...conv, messages: [] })
      }
      return next
    })
  }, [activeConvId])

  const handleCreateGroup = useCallback(async (name: string, members: string[]) => {
    try {
      await fetch(`${API_BASE}/api/groups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, members }),
      })
      await fetchGroups()
      setCreateGroupOpen(false)
    } catch {
    }
  }, [fetchGroups])

  const activeConv = activeConvId ? conversations.get(activeConvId) ?? null : null

  return (
    <div className="h-screen flex bg-chat-bg">
      <ContactList
        models={models}
        groups={groups}
        activeId={activeConvId}
        onSelect={handleSelectContact}
        onCreateGroup={() => setCreateGroupOpen(true)}
      />
      <ChatWindow
        conversation={activeConv}
        models={models}
        onSendMessage={handleSendMessage}
        onOpenSettings={handleOpenSettings}
        onClearHistory={handleClearHistory}
      />
      <ModelSettings
        model={settingsModel}
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSave={handleSaveSettings}
      />
      <CreateGroupModal
        models={models}
        open={createGroupOpen}
        onClose={() => setCreateGroupOpen(false)}
        onCreate={handleCreateGroup}
      />
      {!isConnected && (
        <div className="fixed top-2 left-1/2 -translate-x-1/2 bg-red-500 text-white text-xs px-3 py-1 rounded-full z-50">
          连接断开，正在重连...
        </div>
      )}
    </div>
  )
}