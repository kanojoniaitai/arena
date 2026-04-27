import { useState, useEffect, useCallback } from 'react'
import type { ModelInfo, GroupInfo, DebateInfo, StoryInfo, UndercoverInfo, WerewolfInfo, Conversation, ChatMessage } from './types'
import { useChatSocket } from './hooks/useChatSocket'
import ContactList from './components/ContactList'
import ChatWindow from './components/ChatWindow'
import ModelSettings from './components/ModelSettings'
import CreateGroupModal from './components/CreateGroupModal'
import CreateDebateModal from './components/CreateDebateModal'
import CreateStoryModal from './components/CreateStoryModal'
import CreateUndercoverModal from './components/CreateUndercoverModal'
import CreateWerewolfModal from './components/CreateWerewolfModal'

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

function generateId(): string {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36)
}

export default function App() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [groups, setGroups] = useState<GroupInfo[]>([])
  const [debates, setDebates] = useState<DebateInfo[]>([])
  const [stories, setStories] = useState<StoryInfo[]>([])
  const [undercovers, setUndercovers] = useState<UndercoverInfo[]>([])
  const [werewolves, setWerewolves] = useState<WerewolfInfo[]>([])
  const [conversations, setConversations] = useState<Map<string, Conversation>>(new Map())
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [settingsModel, setSettingsModel] = useState<ModelInfo | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [createGroupOpen, setCreateGroupOpen] = useState(false)
  const [createDebateOpen, setCreateDebateOpen] = useState(false)
  const [createStoryOpen, setCreateStoryOpen] = useState(false)
  const [createUndercoverOpen, setCreateUndercoverOpen] = useState(false)
  const [createWerewolfOpen, setCreateWerewolfOpen] = useState(false)

  const { lastMessage, sendMessage, isConnected } = useChatSocket()

  const fetchModels = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/models`)
      const data = await res.json()
      setModels(data)
    } catch {
      // ignore
    }
  }, [])

  const fetchGroups = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/groups`)
      const data = await res.json()
      setGroups(data)
    } catch {
      // ignore
    }
  }, [])

  const fetchDebates = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/debates`)
      const data = await res.json()
      setDebates(data)
    } catch {
      // ignore
    }
  }, [])

  const fetchStories = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/stories`)
      const data = await res.json()
      setStories(data)
    } catch {
      // ignore
    }
  }, [])

  const fetchUndercovers = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/undercovers`)
      const data = await res.json()
      setUndercovers(data)
    } catch {
      // ignore
    }
  }, [])

  const fetchWerewolves = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/werewolves`)
      const data = await res.json()
      setWerewolves(data)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => {
    fetchModels()
    fetchGroups()
    fetchDebates()
    fetchStories()
    fetchUndercovers()
    fetchWerewolves()
  }, [fetchModels, fetchGroups, fetchDebates, fetchStories, fetchUndercovers, fetchWerewolves])

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/history`)
        const history = await res.json()
        const convs = new Map<string, Conversation>()
        for (const [convId, messages] of Object.entries(history)) {
          const isPrivate = convId.startsWith('private-')
          const isGroup = convId.startsWith('group-')
          const isDebate = convId.startsWith('debate-')
          const isStory = convId.startsWith('story-')
          const isUndercover = convId.startsWith('undercover-')
          const isWerewolf = convId.startsWith('werewolf-')
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
          } else if (isDebate) {
            const debateId = convId.replace('debate-', '')
            const debate = debates.find(d => d.id === debateId)
            convs.set(convId, {
              id: convId,
              type: 'debate',
              name: debate ? `辩论: ${debate.topic}` : '辩论',
              debate_id: debateId,
              pro_model: debate?.pro_model,
              con_model: debate?.con_model,
              topic: debate?.topic,
              current_round: debate?.current_round || 1,
              max_rounds: debate?.max_rounds || 5,
              pro_score: debate?.pro_score || 0,
              con_score: debate?.con_score || 0,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          } else if (isStory) {
            const storyId = convId.replace('story-', '')
            const story = stories.find(s => s.id === storyId)
            convs.set(convId, {
              id: convId,
              type: 'story',
              name: story?.name || '故事接龙',
              story_id: storyId,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          } else if (isUndercover) {
            const ucId = convId.replace('undercover-', '')
            const uc = undercovers.find(u => u.id === ucId)
            convs.set(convId, {
              id: convId,
              type: 'undercover',
              name: uc?.name || '谁是卧底',
              undercover_id: ucId,
              civilian_word: uc?.civilian_word,
              undercover_word: uc?.undercover_word,
              undercover_indices: uc?.undercover_indices,
              current_round: uc?.current_round || 1,
              undercover_phase: uc?.phase || 'describe',
              eliminated: uc?.eliminated || [],
              game_over: uc?.game_over || false,
              winner: uc?.winner || null,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          } else if (isWerewolf) {
            const wfId = convId.replace('werewolf-', '')
            const wf = werewolves.find(w => w.id === wfId)
            convs.set(convId, {
              id: convId,
              type: 'werewolf',
              name: wf?.name || '狼人杀',
              werewolf_id: wfId,
              werewolf_roles: wf?.roles,
              current_round: wf?.current_round || 1,
              werewolf_phase: wf?.phase || 'night',
              werewolf_sub_phase: wf?.sub_phase || 'werewolf',
              eliminated: wf?.eliminated || [],
              game_over: wf?.game_over || false,
              winner: wf?.winner || null,
              messages: (messages as ChatMessage[]).map(m => ({...m, timestamp: m.timestamp || Date.now()})),
              isStreaming: false,
            })
          }
        }
        setConversations(convs)
      } catch {
        // ignore
      }
    }
    loadHistory()
  }, [models, groups, debates, stories, undercovers, werewolves])

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
        // ignore
      }
    }
    
    const timeoutId = setTimeout(saveHistory, 2000)
    return () => clearTimeout(timeoutId)
  }, [conversations])

  useEffect(() => {
    if (!lastMessage || !activeConvId) return

    const activeConv = conversations.get(activeConvId)
    if (!activeConv) return

    if (lastMessage.type === 'ai_stream_token') {
      if (activeConv.type === 'private' && activeConv.model_name === lastMessage.model_name) {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          const msgs = [...conv.messages]
          const lastMsg = msgs[msgs.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && lastMsg.sender === lastMessage.model_name) {
            msgs[msgs.length - 1] = { ...lastMsg, content: lastMsg.content + lastMessage.token }
          } else {
            const model = models.find(m => m.name === lastMessage.model_name)
            msgs.push({
              id: generateId(),
              role: 'assistant',
              content: lastMessage.token,
              sender: lastMessage.model_name,
              display_name: model?.display_name,
              avatar: model?.avatar || '🤖',
              timestamp: Date.now(),
            })
          }
          next.set(activeConvId!, { ...conv, messages: msgs, isStreaming: true })
          return next
        })
      }
    } else if (lastMessage.type.endsWith('_stream_token')) {
      const typePrefix = lastMessage.type.replace('_stream_token', '')
      if (activeConv.type === typePrefix) {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          const msgs = [...conv.messages]
          const lastMsg = msgs[msgs.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && lastMsg.sender === lastMessage.model_name) {
            msgs[msgs.length - 1] = { ...lastMsg, content: lastMsg.content + lastMessage.token }
          } else {
            const model = models.find(m => m.name === lastMessage.model_name)
            const newMsg: ChatMessage = {
              id: generateId(),
              role: 'assistant',
              content: lastMessage.token,
              sender: lastMessage.model_name,
              display_name: lastMessage.display_name || model?.display_name,
              avatar: model?.avatar || '🤖',
              timestamp: Date.now(),
            }
            if (typePrefix === 'debate') {
              newMsg.side = lastMessage.side
              newMsg.round = lastMessage.round
              conv.current_round = lastMessage.round
            } else if (typePrefix === 'story') {
              newMsg.turn = lastMessage.turn
            } else if (typePrefix === 'undercover') {
              newMsg.round = lastMessage.round
              newMsg.phase = lastMessage.phase
              newMsg.is_undercover = lastMessage.is_undercover
            } else if (typePrefix === 'werewolf') {
              newMsg.round = lastMessage.round
              newMsg.phase = lastMessage.phase
              newMsg.sub_phase = lastMessage.sub_phase
              newMsg.werewolf_role = lastMessage.role
            }
            msgs.push(newMsg)
          }
          next.set(activeConvId!, { ...conv, messages: msgs, isStreaming: true })
          return next
        })
      }
    } else if (lastMessage.type === 'ai_complete') {
      if (activeConv.type === 'private' && activeConv.model_name === lastMessage.model_name) {
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
    } else if (lastMessage.type === 'debate_round_complete') {
      if (activeConv.type === 'debate') {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'story_cycle_complete') {
      if (activeConv.type === 'story') {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'undercover_phase_complete') {
      if (activeConv.type === 'undercover') {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'werewolf_phase_complete') {
      if (activeConv.type === 'werewolf') {
        setConversations(prev => {
          const next = new Map(prev)
          const conv = next.get(activeConvId!)
          if (!conv) return prev
          next.set(activeConvId!, { ...conv, isStreaming: false })
          return next
        })
      }
    } else if (lastMessage.type === 'error') {
      const errorMsg: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `⚠️ 错误: ${lastMessage.message}`,
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
      side: m.side,
    }))

    if (conv.type === 'debate') {
      sendMessage('debate', undefined, undefined, message, history, { debate_id: conv.debate_id })
    } else if (conv.type === 'story') {
      sendMessage('story', undefined, undefined, message, history, { story_id: conv.story_id })
    } else if (conv.type === 'undercover') {
      sendMessage('undercover', undefined, undefined, message, history, { undercover_id: conv.undercover_id })
    } else if (conv.type === 'werewolf') {
      sendMessage('werewolf', undefined, undefined, message, history, { werewolf_id: conv.werewolf_id })
    } else {
      sendMessage(conv.type, conv.model_name, conv.group_id, message, history)
    }
  }, [activeConvId, conversations, sendMessage])

  const handleNextDebateRound = useCallback(async () => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'debate' || !conv.debate_id) return

    try {
      const res = await fetch(`${API_BASE}/api/debates/${conv.debate_id}/next-round`, { method: 'PUT' })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          current_round: updated.current_round,
          isStreaming: true,
        })
        return next
      })
      await fetchDebates()

      const history = conv.messages.map(m => ({
        role: m.role,
        content: m.content,
        sender: m.sender,
        display_name: m.display_name,
        side: m.side,
      }))
      sendMessage('debate', undefined, undefined, '继续辩论', history, { debate_id: conv.debate_id })
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, sendMessage, fetchDebates])

  const handleVoteDebate = useCallback(async (winner: 'pro' | 'con') => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'debate' || !conv.debate_id) return

    try {
      const res = await fetch(`${API_BASE}/api/debates/${conv.debate_id}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ winner }),
      })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          pro_score: updated.pro_score,
          con_score: updated.con_score,
        })
        return next
      })
      await fetchDebates()
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, fetchDebates])

  const handleEliminateUndercover = useCallback(async (modelName: string) => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'undercover' || !conv.undercover_id) return

    try {
      const res = await fetch(`${API_BASE}/api/undercovers/${conv.undercover_id}/eliminate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: modelName }),
      })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          eliminated: updated.eliminated,
          game_over: updated.game_over,
          winner: updated.winner,
        })
        return next
      })
      await fetchUndercovers()
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, fetchUndercovers])

  const handleNextUndercoverRound = useCallback(async () => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'undercover' || !conv.undercover_id) return

    try {
      const res = await fetch(`${API_BASE}/api/undercovers/${conv.undercover_id}/next-round`, { method: 'PUT' })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          current_round: updated.current_round,
          undercover_phase: updated.phase,
          isStreaming: true,
        })
        return next
      })
      await fetchUndercovers()

      const history = conv.messages.map(m => ({
        role: m.role,
        content: m.content,
        sender: m.sender,
        display_name: m.display_name,
        side: m.side,
      }))
      sendMessage('undercover', undefined, undefined, '开始新一轮', history, { undercover_id: conv.undercover_id })
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, sendMessage, fetchUndercovers])

  const handleSetUndercoverPhase = useCallback(async (phase: 'describe' | 'vote') => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'undercover' || !conv.undercover_id) return

    setConversations(prev => {
      const next = new Map(prev)
      next.set(activeConvId, { ...conv, undercover_phase: phase, isStreaming: true })
      return next
    })

    const history = conv.messages.map(m => ({
      role: m.role,
      content: m.content,
      sender: m.sender,
      display_name: m.display_name,
      side: m.side,
    }))
    sendMessage('undercover', undefined, undefined, phase === 'vote' ? '请投票' : '请描述', history, { undercover_id: conv.undercover_id })
  }, [activeConvId, conversations, sendMessage])

  const handleSetWerewolfPhase = useCallback(async (phase: 'night' | 'day', subPhase: string) => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'werewolf' || !conv.werewolf_id) return

    try {
      const res = await fetch(`${API_BASE}/api/werewolves/${conv.werewolf_id}/phase`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phase, sub_phase: subPhase }),
      })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          werewolf_phase: updated.phase,
          werewolf_sub_phase: updated.sub_phase,
          current_round: updated.current_round,
          isStreaming: true,
        })
        return next
      })
      await fetchWerewolves()

      const history = conv.messages.map(m => ({
        role: m.role,
        content: m.content,
        sender: m.sender,
        display_name: m.display_name,
        side: m.side,
      }))
      const phaseMsg = phase === 'night'
        ? (subPhase === 'werewolf' ? '天黑请闭眼，狼人请睁眼' : subPhase === 'seer' ? '预言家请睁眼' : '女巫请睁眼')
        : (subPhase === 'discuss' ? '天亮了，请讨论' : '请投票')
      sendMessage('werewolf', undefined, undefined, phaseMsg, history, { werewolf_id: conv.werewolf_id })
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, sendMessage, fetchWerewolves])

  const handleEliminateWerewolf = useCallback(async (modelName: string) => {
    if (!activeConvId) return
    const conv = conversations.get(activeConvId)
    if (!conv || conv.type !== 'werewolf' || !conv.werewolf_id) return

    try {
      const res = await fetch(`${API_BASE}/api/werewolves/${conv.werewolf_id}/eliminate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: modelName }),
      })
      const updated = await res.json()
      setConversations(prev => {
        const next = new Map(prev)
        next.set(activeConvId, {
          ...conv,
          eliminated: updated.eliminated,
          game_over: updated.game_over,
          winner: updated.winner,
        })
        return next
      })
      await fetchWerewolves()
    } catch {
      // ignore
    }
  }, [activeConvId, conversations, fetchWerewolves])

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
      // ignore
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
      // ignore
    }
  }, [fetchGroups])

  const handleCreateDebate = useCallback(async (topic: string, proModel: string, conModel: string, maxRounds: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/debates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, pro_model: proModel, con_model: conModel, max_rounds: maxRounds }),
      })
      const debate = await res.json()
      await fetchDebates()
      setCreateDebateOpen(false)

      const convId = `debate-${debate.id}`
      const proSpec = models.find(m => m.name === proModel)
      const conSpec = models.find(m => m.name === conModel)
      handleSelectContact({
        id: convId,
        type: 'debate',
        name: `辩论: ${topic}`,
        debate_id: debate.id,
        pro_model: proModel,
        con_model: conModel,
        topic,
        current_round: 1,
        max_rounds: maxRounds,
        pro_score: 0,
        con_score: 0,
        messages: [{
          id: generateId(),
          role: 'user',
          content: `辩论话题：${topic}\n正方：${proSpec?.display_name || proModel}\n反方：${conSpec?.display_name || conModel}`,
          timestamp: Date.now(),
        }],
        isStreaming: false,
      })
    } catch {
      // ignore
    }
  }, [fetchDebates, models, handleSelectContact])

  const handleCreateStory = useCallback(async (name: string, members: string[], opening: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/stories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, members }),
      })
      const story = await res.json()
      await fetchStories()
      setCreateStoryOpen(false)

      const convId = `story-${story.id}`
      handleSelectContact({
        id: convId,
        type: 'story',
        name,
        story_id: story.id,
        messages: [{
          id: generateId(),
          role: 'user',
          content: opening,
          timestamp: Date.now(),
        }],
        isStreaming: false,
      })

      const history: { role: string; content: string }[] = []
      sendMessage('story', undefined, undefined, opening, history, { story_id: story.id })
    } catch {
      // ignore
    }
  }, [fetchStories, handleSelectContact, sendMessage])

  const handleCreateUndercover = useCallback(async (name: string, members: string[], civilianWord: string, undercoverWord: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/undercovers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, members, civilian_word: civilianWord, undercover_word: undercoverWord }),
      })
      const uc = await res.json()
      await fetchUndercovers()
      setCreateUndercoverOpen(false)

      const convId = `undercover-${uc.id}`
      handleSelectContact({
        id: convId,
        type: 'undercover',
        name,
        undercover_id: uc.id,
        civilian_word: civilianWord,
        undercover_word: undercoverWord,
        undercover_indices: uc.undercover_indices,
        current_round: 1,
        undercover_phase: 'describe',
        eliminated: [],
        game_over: false,
        winner: null,
        messages: [{
          id: generateId(),
          role: 'user',
          content: `谁是卧底游戏开始！平民词：${civilianWord}，卧底词：${undercoverWord}`,
          timestamp: Date.now(),
        }],
        isStreaming: false,
      })

      const history: { role: string; content: string }[] = []
      sendMessage('undercover', undefined, undefined, '游戏开始，请描述你的词语', history, { undercover_id: uc.id })
    } catch {
      // ignore
    }
  }, [fetchUndercovers, handleSelectContact, sendMessage])

  const handleCreateWerewolf = useCallback(async (name: string, members: string[]) => {
    try {
      const res = await fetch(`${API_BASE}/api/werewolves`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, members }),
      })
      const wf = await res.json()
      await fetchWerewolves()
      setCreateWerewolfOpen(false)

      const convId = `werewolf-${wf.id}`
      const roleEntries = Object.entries(wf.roles as Record<string, string>)
      const roleNames: Record<string, string> = { werewolf: '狼人', villager: '村民', seer: '预言家', witch: '女巫', hunter: '猎人' }
      const roleIcons: Record<string, string> = { werewolf: '🐺', villager: '👨‍🌾', seer: '🔮', witch: '🧙‍♀️', hunter: '🏹' }
      const roleSummary = roleEntries.map(([m, r]) => {
        const spec = models.find(mod => mod.name === m)
        return `${roleIcons[r] || ''} ${spec?.display_name || m}: ${roleNames[r] || r}`
      }).join('、')

      handleSelectContact({
        id: convId,
        type: 'werewolf',
        name,
        werewolf_id: wf.id,
        werewolf_roles: wf.roles,
        current_round: 1,
        werewolf_phase: 'night',
        werewolf_sub_phase: 'werewolf',
        eliminated: [],
        game_over: false,
        winner: null,
        messages: [{
          id: generateId(),
          role: 'user',
          content: `狼人杀游戏开始！角色分配：${roleSummary}\n你是上帝，掌控游戏流程。`,
          timestamp: Date.now(),
        }],
        isStreaming: false,
      })

      const history: { role: string; content: string }[] = []
      sendMessage('werewolf', undefined, undefined, '天黑请闭眼，狼人请睁眼', history, { werewolf_id: wf.id })
    } catch {
      // ignore
    }
  }, [fetchWerewolves, models, handleSelectContact, sendMessage])

  const activeConv = activeConvId ? conversations.get(activeConvId) ?? null : null

  return (
    <div className="h-screen flex bg-wechat-bg">
      <ContactList
        models={models}
        groups={groups}
        debates={debates}
        stories={stories}
        undercovers={undercovers}
        werewolves={werewolves}
        activeId={activeConvId}
        onSelect={handleSelectContact}
        onCreateGroup={() => setCreateGroupOpen(true)}
        onCreateDebate={() => setCreateDebateOpen(true)}
        onCreateStory={() => setCreateStoryOpen(true)}
        onCreateUndercover={() => setCreateUndercoverOpen(true)}
        onCreateWerewolf={() => setCreateWerewolfOpen(true)}
      />
      <ChatWindow
        conversation={activeConv}
        models={models}
        onSendMessage={handleSendMessage}
        onOpenSettings={handleOpenSettings}
        onClearHistory={handleClearHistory}
        onNextDebateRound={handleNextDebateRound}
        onVoteDebate={handleVoteDebate}
        onEliminateUndercover={handleEliminateUndercover}
        onNextUndercoverRound={handleNextUndercoverRound}
        onSetUndercoverPhase={handleSetUndercoverPhase}
        onSetWerewolfPhase={handleSetWerewolfPhase}
        onEliminateWerewolf={handleEliminateWerewolf}
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
      <CreateDebateModal
        models={models}
        open={createDebateOpen}
        onClose={() => setCreateDebateOpen(false)}
        onCreate={handleCreateDebate}
      />
      <CreateStoryModal
        models={models}
        open={createStoryOpen}
        onClose={() => setCreateStoryOpen(false)}
        onCreate={handleCreateStory}
      />
      <CreateUndercoverModal
        models={models}
        open={createUndercoverOpen}
        onClose={() => setCreateUndercoverOpen(false)}
        onCreate={handleCreateUndercover}
      />
      <CreateWerewolfModal
        models={models}
        open={createWerewolfOpen}
        onClose={() => setCreateWerewolfOpen(false)}
        onCreate={handleCreateWerewolf}
      />
      {!isConnected && (
        <div className="fixed top-2 left-1/2 -translate-x-1/2 bg-red-500 text-white text-xs px-3 py-1 rounded-full z-50">
          连接断开，正在重连...
        </div>
      )}
    </div>
  )
}
