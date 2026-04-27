import { useEffect, useRef } from 'react'
import { Settings, Trash2, ChevronRight, ThumbsUp, Skull, Moon, Sun } from 'lucide-react'
import type { Conversation, ModelInfo, ChatMessage } from '../types'
import MessageInput from './MessageInput'

interface ChatWindowProps {
  conversation: Conversation | null
  models: ModelInfo[]
  onSendMessage: (message: string) => void
  onOpenSettings: () => void
  onClearHistory?: () => void
  onNextDebateRound?: () => void
  onVoteDebate?: (winner: 'pro' | 'con') => void
  onEliminateUndercover?: (modelName: string) => void
  onNextUndercoverRound?: () => void
  onSetUndercoverPhase?: (phase: 'describe' | 'vote') => void
  onSetWerewolfPhase?: (phase: 'night' | 'day', subPhase: string) => void
  onEliminateWerewolf?: (modelName: string) => void
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

const WEREWOLF_ROLE_NAMES: Record<string, string> = {
  werewolf: '狼人',
  villager: '村民',
  seer: '预言家',
  witch: '女巫',
  hunter: '猎人',
}

const WEREWOLF_ROLE_ICONS: Record<string, string> = {
  werewolf: '🐺',
  villager: '👨‍🌾',
  seer: '🔮',
  witch: '🧙‍♀️',
  hunter: '🏹',
}

export default function ChatWindow({ conversation, models, onSendMessage, onOpenSettings, onClearHistory, onNextDebateRound, onVoteDebate, onEliminateUndercover, onNextUndercoverRound, onSetUndercoverPhase, onSetWerewolfPhase, onEliminateWerewolf }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation?.messages, conversation?.isStreaming])

  if (!conversation) {
    return (
      <div className="flex-1 bg-wechat-chat-bg flex items-center justify-center">
        <p className="text-wechat-text-secondary text-sm">选择一个联系人开始聊天</p>
      </div>
    )
  }

  const activeModel = conversation.type === 'private'
    ? models.find(m => m.name === conversation.model_name)
    : null

  const renderHeader = () => {
    let title = conversation.name
    let subtitle = ''

    if (conversation.type === 'debate') {
      subtitle = `第 ${conversation.current_round || 1} 轮 · 正方 ${conversation.pro_score || 0} : ${conversation.con_score || 0} 反方`
    } else if (conversation.type === 'story') {
      subtitle = '故事接龙模式'
    } else if (conversation.type === 'group') {
      subtitle = '群聊 · 角色间可互相回应'
    } else if (conversation.type === 'undercover') {
      const phase = conversation.undercover_phase || 'describe'
      subtitle = `谁是卧底 · 第${conversation.current_round || 1}轮 · ${phase === 'describe' ? '📝 描述' : '🗳️ 投票'}`
      if (conversation.game_over) subtitle = `谁是卧底 · ${conversation.winner === 'civilian' ? '🎉 平民胜利' : '🕵️ 卧底胜利'}`
    } else if (conversation.type === 'werewolf') {
      const phase = conversation.werewolf_phase || 'night'
      const sub = conversation.werewolf_sub_phase || 'werewolf'
      const phaseText = phase === 'night' ? '🌙 夜晚' : '☀️ 白天'
      const subText = sub === 'werewolf' ? '狼人行动' : sub === 'seer' ? '预言家查验' : sub === 'witch' ? '女巫用药' : sub === 'discuss' ? '讨论' : sub === 'vote' ? '投票' : ''
      subtitle = `狼人杀 · 第${conversation.current_round || 1}轮 · ${phaseText} · ${subText}`
      if (conversation.game_over) subtitle = `狼人杀 · ${conversation.winner === 'good' ? '🎉 好人胜利' : '🐺 狼人胜利'}`
    }

    return (
      <div className="flex items-center justify-between px-4 py-3 bg-wechat-sidebar border-b border-wechat-border">
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-wechat-text">{title}</span>
          {subtitle && <span className="text-xs text-wechat-text-secondary ml-2">{subtitle}</span>}
        </div>
        <div className="flex items-center gap-1">
          {activeModel && (
            <button
              onClick={onOpenSettings}
              className="p-1.5 rounded hover:bg-wechat-hover text-wechat-text-secondary transition-colors"
              title="模型设置"
            >
              <Settings size={16} />
            </button>
          )}
          {onClearHistory && (
            <button
              onClick={onClearHistory}
              className="p-1.5 rounded hover:bg-wechat-hover text-wechat-text-secondary transition-colors"
              title="清空聊天记录"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>
    )
  }

  const renderDebateActions = () => {
    if (conversation.type !== 'debate' || conversation.isStreaming) return null
    const currentRound = conversation.current_round || 1
    const maxRounds = conversation.max_rounds || 5

    return (
      <div className="px-4 py-2 bg-wechat-sidebar border-t border-wechat-border flex items-center gap-2 flex-wrap">
        {currentRound < maxRounds && (
          <button
            onClick={onNextDebateRound}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-debate-pro text-white text-xs font-medium hover:opacity-90 transition-opacity"
          >
            <ChevronRight size={14} />
            下一轮
          </button>
        )}
        <button
          onClick={() => onVoteDebate?.('pro')}
          className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-debate-pro text-white text-xs font-medium hover:opacity-90 transition-opacity"
        >
          <ThumbsUp size={14} />
          正方胜
        </button>
        <button
          onClick={() => onVoteDebate?.('con')}
          className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-debate-con text-white text-xs font-medium hover:opacity-90 transition-opacity"
        >
          <ThumbsUp size={14} />
          反方胜
        </button>
        <span className="text-xs text-wechat-text-secondary ml-auto">
          第 {currentRound}/{maxRounds} 轮
        </span>
      </div>
    )
  }

  const renderUndercoverActions = () => {
    if (conversation.type !== 'undercover' || conversation.isStreaming) return null
    if (conversation.game_over) return null
    const phase = conversation.undercover_phase || 'describe'
    const eliminated = conversation.eliminated || []

    return (
      <div className="px-4 py-2 bg-wechat-sidebar border-t border-wechat-border flex items-center gap-2 flex-wrap">
        {phase === 'describe' && (
          <button
            onClick={() => onSetUndercoverPhase?.('vote')}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-undercover-undercover text-white text-xs font-medium hover:opacity-90 transition-opacity"
          >
            🗳️ 进入投票
          </button>
        )}
        {phase === 'vote' && (
          <button
            onClick={() => onSetUndercoverPhase?.('describe')}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-undercover-civilian text-white text-xs font-medium hover:opacity-90 transition-opacity"
          >
            📝 返回描述
          </button>
        )}
        <button
          onClick={onNextUndercoverRound}
          className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-undercover-bg text-white text-xs font-medium hover:opacity-90 transition-opacity"
        >
          <ChevronRight size={14} />
          下一轮
        </button>
        <span className="text-xs text-wechat-text-secondary">
          第 {conversation.current_round || 1} 轮 · {phase === 'describe' ? '描述' : '投票'} · 已淘汰 {eliminated.length} 人
        </span>
      </div>
    )
  }

  const renderWerewolfActions = () => {
    if (conversation.type !== 'werewolf' || conversation.isStreaming) return null
    if (conversation.game_over) return null
    const phase = conversation.werewolf_phase || 'night'
    const sub = conversation.werewolf_sub_phase || 'werewolf'
    const eliminated = conversation.eliminated || []

    return (
      <div className="px-4 py-2 bg-wechat-sidebar border-t border-wechat-border flex items-center gap-2 flex-wrap">
        {phase === 'night' && (
          <>
            <button
              onClick={() => onSetWerewolfPhase?.('night', 'werewolf')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-white text-xs font-medium hover:opacity-90 transition-opacity ${sub === 'werewolf' ? 'bg-werewolf-wolf' : 'bg-werewolf-wolf/60'}`}
            >
              🐺 狼人
            </button>
            <button
              onClick={() => onSetWerewolfPhase?.('night', 'seer')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-white text-xs font-medium hover:opacity-90 transition-opacity ${sub === 'seer' ? 'bg-werewolf-good' : 'bg-werewolf-good/60'}`}
            >
              🔮 预言家
            </button>
            <button
              onClick={() => onSetWerewolfPhase?.('night', 'witch')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-white text-xs font-medium hover:opacity-90 transition-opacity ${sub === 'witch' ? 'bg-purple-600' : 'bg-purple-600/60'}`}
            >
              🧙‍♀️ 女巫
            </button>
            <button
              onClick={() => onSetWerewolfPhase?.('day', 'discuss')}
              className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-yellow-500 text-white text-xs font-medium hover:opacity-90 transition-opacity"
            >
              <Sun size={14} />
              天亮了
            </button>
          </>
        )}
        {phase === 'day' && (
          <>
            <button
              onClick={() => onSetWerewolfPhase?.('day', 'discuss')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-white text-xs font-medium hover:opacity-90 transition-opacity ${sub === 'discuss' ? 'bg-yellow-500' : 'bg-yellow-500/60'}`}
            >
              💬 讨论
            </button>
            <button
              onClick={() => onSetWerewolfPhase?.('day', 'vote')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-white text-xs font-medium hover:opacity-90 transition-opacity ${sub === 'vote' ? 'bg-werewolf-good' : 'bg-werewolf-good/60'}`}
            >
              🗳️ 投票
            </button>
            <button
              onClick={() => onSetWerewolfPhase?.('night', 'werewolf')}
              className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-werewolf-night text-white text-xs font-medium hover:opacity-90 transition-opacity"
            >
              <Moon size={14} />
              天黑了
            </button>
          </>
        )}
        <span className="text-xs text-wechat-text-secondary ml-auto">
          第 {conversation.current_round || 1} 轮 · 已淘汰 {eliminated.length} 人
        </span>
      </div>
    )
  }

  const renderMessage = (msg: ChatMessage, idx: number) => {
    const prev = idx > 0 ? conversation.messages[idx - 1] : undefined
    const showTime = shouldShowTime(msg, prev)
    const isUser = msg.role === 'user'

    if (conversation.type === 'debate' && !isUser && msg.side) {
      const isPro = msg.side === 'pro'
      const displayName = msg.display_name || getModelDisplayName(models, msg.sender || '')
      const avatar = msg.avatar || getModelAvatar(models, msg.sender || '')

      return (
        <div key={msg.id}>
          {showTime && (
            <div className="text-center text-xs text-wechat-text-secondary my-3">
              {formatTime(msg.timestamp)}
            </div>
          )}
          <div className={`flex items-start gap-2 mb-3 ${isPro ? 'flex-row' : 'flex-row-reverse'}`}>
            <div className={`w-9 h-9 rounded-md flex items-center justify-center text-base shrink-0 ${isPro ? 'bg-debate-pro' : 'bg-debate-con'}`}>
              {avatar}
            </div>
            <div className={`max-w-[70%] flex flex-col ${isPro ? 'items-start' : 'items-end'}`}>
              <div className="flex items-center gap-1 mb-0.5">
                <span className={`text-xs px-1.5 py-0.5 rounded ${isPro ? 'bg-debate-pro/10 text-debate-pro' : 'bg-debate-con/10 text-debate-con'}`}>
                  {isPro ? '正方' : '反方'}
                </span>
                <span className="text-xs text-wechat-text-secondary">{displayName}</span>
                {msg.round && <span className="text-xs text-wechat-text-secondary">· R{msg.round}</span>}
              </div>
              <div className={`px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words rounded-2xl shadow-sm ${
                isPro
                  ? 'bg-debate-pro/5 text-black rounded-bl-sm border-l-2 border-debate-pro'
                  : 'bg-debate-con/5 text-black rounded-br-sm border-r-2 border-debate-con'
              }`}>
                {msg.content}
              </div>
            </div>
          </div>
        </div>
      )
    }

    if (conversation.type === 'story' && !isUser) {
      const displayName = msg.display_name || getModelDisplayName(models, msg.sender || '')
      const avatar = msg.avatar || getModelAvatar(models, msg.sender || '')

      return (
        <div key={msg.id}>
          {showTime && (
            <div className="text-center text-xs text-wechat-text-secondary my-3">
              {formatTime(msg.timestamp)}
            </div>
          )}
          <div className="flex items-start gap-2 mb-3">
            <div className="w-9 h-9 rounded-md bg-story-bg flex items-center justify-center text-base shrink-0">
              {avatar}
            </div>
            <div className="max-w-[85%] flex flex-col items-start">
              <div className="flex items-center gap-1 mb-0.5">
                <span className="text-xs text-wechat-text-secondary">{displayName}</span>
                {msg.turn && <span className="text-xs text-wechat-text-secondary">· 第{msg.turn}段</span>}
              </div>
              <div className="px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words bg-white text-black rounded-2xl rounded-bl-sm shadow-sm border-l-2 border-story-accent">
                {msg.content}
              </div>
            </div>
          </div>
        </div>
      )
    }

    if (conversation.type === 'undercover' && !isUser) {
      const displayName = msg.display_name || getModelDisplayName(models, msg.sender || '')
      const avatar = msg.avatar || getModelAvatar(models, msg.sender || '')
      const isUC = msg.is_undercover
      const eliminated = conversation.eliminated || []
      const isEliminated = eliminated.includes(msg.sender || '')

      return (
        <div key={msg.id} className={isEliminated ? 'opacity-50' : ''}>
          {showTime && (
            <div className="text-center text-xs text-wechat-text-secondary my-3">
              {formatTime(msg.timestamp)}
            </div>
          )}
          <div className="flex items-start gap-2 mb-3">
            <div className={`w-9 h-9 rounded-md flex items-center justify-center text-base shrink-0 ${isEliminated ? 'bg-gray-400' : isUC ? 'bg-undercover-undercover' : 'bg-undercover-civilian'}`}>
              {isEliminated ? '💀' : avatar}
            </div>
            <div className="max-w-[85%] flex flex-col items-start">
              <div className="flex items-center gap-1 mb-0.5">
                <span className="text-xs text-wechat-text-secondary">{displayName}</span>
                {isUC && <span className="text-xs px-1.5 py-0.5 rounded bg-undercover-undercover/10 text-undercover-undercover">卧底</span>}
                {!isUC && <span className="text-xs px-1.5 py-0.5 rounded bg-undercover-civilian/10 text-undercover-civilian">平民</span>}
                {msg.round && <span className="text-xs text-wechat-text-secondary">· R{msg.round}</span>}
                {msg.phase && <span className="text-xs text-wechat-text-secondary">· {msg.phase === 'describe' ? '描述' : '投票'}</span>}
                {isEliminated && <span className="text-xs text-undercover-undercover">· 已淘汰</span>}
              </div>
              <div className="px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words bg-white text-black rounded-2xl rounded-bl-sm shadow-sm border-l-2 border-undercover-bg">
                {msg.content}
              </div>
              {!isEliminated && onEliminateUndercover && (
                <button
                  onClick={() => onEliminateUndercover(msg.sender || '')}
                  className="mt-1 flex items-center gap-1 px-2 py-0.5 rounded text-xs text-undercover-undercover hover:bg-undercover-undercover/10 transition-colors"
                >
                  <Skull size={12} />
                  淘汰
                </button>
              )}
            </div>
          </div>
        </div>
      )
    }

    if (conversation.type === 'werewolf' && !isUser) {
      const displayName = msg.display_name || getModelDisplayName(models, msg.sender || '')
      const avatar = msg.avatar || getModelAvatar(models, msg.sender || '')
      const role = msg.werewolf_role || 'villager'
      const roleName = WEREWOLF_ROLE_NAMES[role] || role
      const roleIcon = WEREWOLF_ROLE_ICONS[role] || '🤖'
      const eliminated = conversation.eliminated || []
      const isEliminated = eliminated.includes(msg.sender || '')
      const isWolf = role === 'werewolf'
      const phase = conversation.werewolf_phase || 'night'

      return (
        <div key={msg.id} className={isEliminated ? 'opacity-50' : ''}>
          {showTime && (
            <div className="text-center text-xs text-wechat-text-secondary my-3">
              {formatTime(msg.timestamp)}
            </div>
          )}
          <div className="flex items-start gap-2 mb-3">
            <div className={`w-9 h-9 rounded-md flex items-center justify-center text-base shrink-0 ${isEliminated ? 'bg-gray-400' : isWolf ? 'bg-werewolf-wolf' : 'bg-werewolf-good'}`}>
              {isEliminated ? '💀' : avatar}
            </div>
            <div className="max-w-[85%] flex flex-col items-start">
              <div className="flex items-center gap-1 mb-0.5">
                <span className="text-xs text-wechat-text-secondary">{displayName}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${isWolf ? 'bg-werewolf-wolf/10 text-werewolf-wolf' : 'bg-werewolf-good/10 text-werewolf-good'}`}>
                  {roleIcon} {roleName}
                </span>
                {msg.round && <span className="text-xs text-wechat-text-secondary">· R{msg.round}</span>}
                {msg.phase && <span className="text-xs text-wechat-text-secondary">· {msg.phase === 'night' ? '🌙' : '☀️'}</span>}
                {msg.sub_phase && <span className="text-xs text-wechat-text-secondary">{msg.sub_phase}</span>}
                {isEliminated && <span className="text-xs text-werewolf-wolf">· 已淘汰</span>}
              </div>
              <div className={`px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words rounded-2xl rounded-bl-sm shadow-sm ${
                phase === 'night'
                  ? 'bg-werewolf-night/5 text-black border-l-2 border-werewolf-night'
                  : 'bg-werewolf-day/50 text-black border-l-2 border-werewolf-bg'
              }`}>
                {msg.content}
              </div>
              {!isEliminated && onEliminateWerewolf && phase === 'day' && (
                <button
                  onClick={() => onEliminateWerewolf(msg.sender || '')}
                  className="mt-1 flex items-center gap-1 px-2 py-0.5 rounded text-xs text-werewolf-wolf hover:bg-werewolf-wolf/10 transition-colors"
                >
                  <Skull size={12} />
                  淘汰
                </button>
              )}
            </div>
          </div>
        </div>
      )
    }

    const avatar = isUser ? '👤' : (msg.avatar || getModelAvatar(models, msg.sender || ''))
    const displayName = !isUser && msg.sender ? (msg.display_name || getModelDisplayName(models, msg.sender)) : ''

    return (
      <div key={msg.id}>
        {showTime && (
          <div className="text-center text-xs text-wechat-text-secondary my-3">
            {formatTime(msg.timestamp)}
          </div>
        )}
        <div className={`flex items-start gap-2 mb-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className="w-9 h-9 rounded-md bg-wechat-green flex items-center justify-center text-base shrink-0">
            {avatar}
          </div>
          <div className={`max-w-[70%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
            {(conversation.type === 'group') && !isUser && displayName && (
              <span className="text-xs text-wechat-text-secondary mb-0.5 ml-1">{displayName}</span>
            )}
            <div
              className={`px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words ${
                isUser
                  ? 'bg-wechat-user-bubble text-black rounded-2xl rounded-br-sm'
                  : 'bg-white text-black rounded-2xl rounded-bl-sm shadow-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const getPlaceholder = () => {
    switch (conversation.type) {
      case 'debate': return '输入消息插话...'
      case 'story': return '输入指示改变故事走向...'
      case 'undercover': return conversation.undercover_phase === 'vote' ? '输入消息触发投票...' : '输入消息触发描述...'
      case 'werewolf': return conversation.werewolf_phase === 'night' ? '输入夜晚指令（如：狼人请睁眼）...' : '输入白天指令...'
      default: return '输入消息...'
    }
  }

  return (
    <div className="flex-1 bg-wechat-chat-bg flex flex-col h-full">
      {renderHeader()}

      <div className="flex-1 overflow-y-auto px-4 py-3">
        {conversation.type === 'undercover' && conversation.civilian_word && (
          <div className="mb-3 px-3 py-2 rounded-md bg-undercover-bg/10 border border-undercover-bg/20 text-xs">
            <span className="text-undercover-civilian font-medium">平民词：{conversation.civilian_word}</span>
            <span className="mx-2">|</span>
            <span className="text-undercover-undercover font-medium">卧底词：{conversation.undercover_word}</span>
          </div>
        )}
        {conversation.type === 'werewolf' && conversation.werewolf_roles && (
          <div className="mb-3 px-3 py-2 rounded-md bg-werewolf-bg/10 border border-werewolf-bg/20 text-xs">
            <span className="font-medium text-wechat-text">角色分配：</span>
            {Object.entries(conversation.werewolf_roles).map(([name, role]) => {
              const spec = models.find(m => m.name === name)
              const displayName = spec?.display_name || name
              const isWolf = role === 'werewolf'
              const eliminated = conversation.eliminated || []
              const isEliminated = eliminated.includes(name)
              return (
                <span key={name} className={`inline-flex items-center gap-0.5 mr-2 ${isEliminated ? 'line-through opacity-50' : ''}`}>
                  <span className={isWolf ? 'text-werewolf-wolf' : 'text-werewolf-good'}>
                    {WEREWOLF_ROLE_ICONS[role] || '🤖'} {displayName}({WEREWOLF_ROLE_NAMES[role]})
                  </span>
                </span>
              )
            })}
          </div>
        )}
        {conversation.messages.map((msg, idx) => renderMessage(msg, idx))}

        {conversation.isStreaming && (
          <div className="flex items-start gap-2 mb-3">
            <div className="w-9 h-9 rounded-md bg-wechat-green flex items-center justify-center text-base shrink-0 animate-pulse">
              {activeModel?.avatar || '🤖'}
            </div>
            <div className="bg-white text-black rounded-2xl rounded-bl-sm shadow-sm px-3 py-2 text-sm text-wechat-text-secondary">
              思考中...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {renderDebateActions()}
      {renderUndercoverActions()}
      {renderWerewolfActions()}

      <MessageInput
        onSend={onSendMessage}
        disabled={conversation.isStreaming || conversation.game_over === true}
        placeholder={getPlaceholder()}
      />
    </div>
  )
}
