import { useState } from 'react'
import { Search, Plus } from 'lucide-react'
import type { ModelInfo, GroupInfo, DebateInfo, StoryInfo, UndercoverInfo, WerewolfInfo, Conversation } from '../types'

interface ContactListProps {
  models: ModelInfo[]
  groups: GroupInfo[]
  debates: DebateInfo[]
  stories: StoryInfo[]
  undercovers: UndercoverInfo[]
  werewolves: WerewolfInfo[]
  activeId: string | null
  onSelect: (conv: Conversation) => void
  onCreateGroup: () => void
  onCreateDebate: () => void
  onCreateStory: () => void
  onCreateUndercover: () => void
  onCreateWerewolf: () => void
}

export default function ContactList({ models, groups, debates, stories, undercovers, werewolves, activeId, onSelect, onCreateGroup, onCreateDebate, onCreateStory, onCreateUndercover, onCreateWerewolf }: ContactListProps) {
  const [filter, setFilter] = useState('')

  const lc = filter.toLowerCase()
  const filteredModels = models.filter(m =>
    m.name.toLowerCase().includes(lc) || m.display_name.toLowerCase().includes(lc)
  )
  const filteredGroups = groups.filter(g =>
    g.name.toLowerCase().includes(lc)
  )
  const filteredDebates = debates.filter(d =>
    d.topic.toLowerCase().includes(lc)
  )
  const filteredStories = stories.filter(s =>
    s.name.toLowerCase().includes(lc)
  )
  const filteredUndercovers = undercovers.filter(u =>
    u.name.toLowerCase().includes(lc)
  )
  const filteredWerewolves = werewolves.filter(w =>
    w.name.toLowerCase().includes(lc)
  )

  return (
    <div className="w-[280px] bg-wechat-sidebar border-r border-wechat-border flex flex-col h-full">
      <div className="p-3 flex items-center gap-2">
        <h1 className="text-lg font-bold text-wechat-text flex-1">AI 聊天</h1>
      </div>

      <div className="px-3 pb-2">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-wechat-text-secondary" />
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="搜索"
            className="w-full pl-8 pr-3 py-1.5 rounded-sm bg-wechat-bg text-sm text-wechat-text placeholder:text-wechat-text-secondary outline-none"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium">模型</div>
        {filteredModels.map(model => {
          const convId = `private-${model.name}`
          const isActive = activeId === convId
          const displayName = model.display_name || model.name
          return (
            <div
              key={model.name}
              onClick={() => onSelect({
                id: convId,
                type: 'private',
                name: displayName,
                model_name: model.name,
                messages: [],
                isStreaming: false,
              })}
              className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-md bg-wechat-green flex items-center justify-center text-lg shrink-0">
                {model.avatar || '🤖'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-wechat-text truncate">{displayName}</div>
                <div className="text-xs text-wechat-text-secondary truncate">
                  {model.params && <span className="inline-block bg-wechat-bg rounded px-1 mr-1">{model.params}</span>}
                  {model.quant && <span>{model.quant}</span>}
                </div>
              </div>
            </div>
          )
        })}

        {filteredGroups.length > 0 && (
          <>
            <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
              <span>群聊</span>
              <button onClick={onCreateGroup} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
            </div>
            {filteredGroups.map(group => {
              const convId = `group-${group.id}`
              const isActive = activeId === convId
              return (
                <div
                  key={group.id}
                  onClick={() => onSelect({
                    id: convId,
                    type: 'group',
                    name: group.name,
                    group_id: group.id,
                    messages: [],
                    isStreaming: false,
                  })}
                  className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                    isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
                  }`}
                >
                  <div className="w-10 h-10 rounded-md bg-wechat-green-dark flex items-center justify-center text-lg shrink-0">
                    👥
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-wechat-text truncate">{group.name}</div>
                    <div className="text-xs text-wechat-text-secondary truncate">{group.members.length} 个成员</div>
                  </div>
                </div>
              )
            })}
          </>
        )}

        {filteredGroups.length === 0 && (
          <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
            <span>群聊</span>
            <button onClick={onCreateGroup} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
          </div>
        )}

        <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
          <span>辩论擂台</span>
          <button onClick={onCreateDebate} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
        </div>
        {filteredDebates.map(debate => {
          const convId = `debate-${debate.id}`
          const isActive = activeId === convId
          const proModel = models.find(m => m.name === debate.pro_model)
          const conModel = models.find(m => m.name === debate.con_model)
          return (
            <div
              key={debate.id}
              onClick={() => onSelect({
                id: convId,
                type: 'debate',
                name: `辩论: ${debate.topic}`,
                debate_id: debate.id,
                pro_model: debate.pro_model,
                con_model: debate.con_model,
                topic: debate.topic,
                current_round: debate.current_round,
                max_rounds: debate.max_rounds,
                pro_score: debate.pro_score,
                con_score: debate.con_score,
                messages: [],
                isStreaming: false,
              })}
              className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-md bg-debate-bg flex items-center justify-center text-lg shrink-0">
                ⚔️
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-wechat-text truncate">{debate.topic}</div>
                <div className="text-xs text-wechat-text-secondary truncate">
                  {proModel?.display_name || debate.pro_model} vs {conModel?.display_name || debate.con_model}
                </div>
              </div>
            </div>
          )
        })}

        <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
          <span>故事接龙</span>
          <button onClick={onCreateStory} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
        </div>
        {filteredStories.map(story => {
          const convId = `story-${story.id}`
          const isActive = activeId === convId
          return (
            <div
              key={story.id}
              onClick={() => onSelect({
                id: convId,
                type: 'story',
                name: story.name,
                story_id: story.id,
                messages: [],
                isStreaming: false,
              })}
              className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-md bg-story-bg flex items-center justify-center text-lg shrink-0">
                📖
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-wechat-text truncate">{story.name}</div>
                <div className="text-xs text-wechat-text-secondary truncate">{story.members.length} 位叙述者</div>
              </div>
            </div>
          )
        })}

        <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
          <span>谁是卧底</span>
          <button onClick={onCreateUndercover} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
        </div>
        {filteredUndercovers.map(uc => {
          const convId = `undercover-${uc.id}`
          const isActive = activeId === convId
          return (
            <div
              key={uc.id}
              onClick={() => onSelect({
                id: convId,
                type: 'undercover',
                name: uc.name,
                undercover_id: uc.id,
                civilian_word: uc.civilian_word,
                undercover_word: uc.undercover_word,
                undercover_indices: uc.undercover_indices,
                current_round: uc.current_round,
                undercover_phase: uc.phase,
                eliminated: uc.eliminated,
                game_over: uc.game_over,
                winner: uc.winner,
                messages: [],
                isStreaming: false,
              })}
              className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-md bg-undercover-bg flex items-center justify-center text-lg shrink-0">
                🕵️
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-wechat-text truncate">{uc.name}</div>
                <div className="text-xs text-wechat-text-secondary truncate">
                  {uc.civilian_word} vs {uc.undercover_word}
                  {uc.game_over && <span className="ml-1 text-undercover-undercover">已结束</span>}
                </div>
              </div>
            </div>
          )
        })}

        <div className="px-3 py-1.5 text-xs text-wechat-text-secondary font-medium mt-1 flex items-center justify-between">
          <span>狼人杀</span>
          <button onClick={onCreateWerewolf} className="p-0.5 rounded hover:bg-wechat-hover"><Plus size={14} /></button>
        </div>
        {filteredWerewolves.map(wf => {
          const convId = `werewolf-${wf.id}`
          const isActive = activeId === convId
          return (
            <div
              key={wf.id}
              onClick={() => onSelect({
                id: convId,
                type: 'werewolf',
                name: wf.name,
                werewolf_id: wf.id,
                werewolf_roles: wf.roles,
                current_round: wf.current_round,
                werewolf_phase: wf.phase,
                werewolf_sub_phase: wf.sub_phase,
                eliminated: wf.eliminated,
                game_over: wf.game_over,
                winner: wf.winner,
                messages: [],
                isStreaming: false,
              })}
              className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer transition-colors ${
                isActive ? 'bg-wechat-active' : 'hover:bg-wechat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-md bg-werewolf-bg flex items-center justify-center text-lg shrink-0">
                🐺
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-wechat-text truncate">{wf.name}</div>
                <div className="text-xs text-wechat-text-secondary truncate">
                  {wf.members.length} 人 · {wf.phase === 'night' ? '🌙 夜晚' : '☀️ 白天'}
                  {wf.game_over && <span className="ml-1 text-werewolf-wolf">已结束</span>}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
