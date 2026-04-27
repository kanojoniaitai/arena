import { useState } from 'react'
import { Search, Plus } from 'lucide-react'
import type { ModelInfo, GroupInfo, Conversation } from '../types'

interface ContactListProps {
  models: ModelInfo[]
  groups: GroupInfo[]
  activeId: string | null
  onSelect: (conv: Conversation) => void
  onCreateGroup: () => void
}

export default function ContactList({ models, groups, activeId, onSelect, onCreateGroup }: ContactListProps) {
  const [filter, setFilter] = useState('')

  const lc = filter.toLowerCase()
  const filteredModels = models.filter(m =>
    m.name.toLowerCase().includes(lc) || m.display_name.toLowerCase().includes(lc)
  )
  const filteredGroups = groups.filter(g =>
    g.name.toLowerCase().includes(lc)
  )

  return (
    <div className="w-[280px] bg-chat-sidebar border-r border-chat-border flex flex-col h-full">
      <div className="p-4 flex items-center gap-2">
        <h1 className="text-xl font-semibold tracking-tight text-chat-text flex-1">Llama.cpp Arena</h1>
      </div>

      <div className="px-4 pb-3">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-chat-text-secondary" />
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="搜索模型 / 群聊"
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-chat-hover text-sm text-chat-text placeholder:text-chat-text-secondary outline-none transition-colors focus:bg-white focus:ring-2 focus:ring-chat-accent focus:ring-opacity-20"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pt-2">
        <div className="px-4 py-2 text-xs uppercase tracking-wider text-chat-text-secondary font-semibold">模型</div>
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
              className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors ${
                isActive ? 'bg-chat-active' : 'hover:bg-chat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-full bg-chat-bg shadow-sm flex items-center justify-center text-lg shrink-0 border border-chat-border">
                {model.avatar || '🤖'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[15px] font-medium text-chat-text truncate">{displayName}</div>
                <div className="text-xs text-chat-text-secondary truncate mt-0.5 flex gap-1 items-center">
                  {model.params && <span className="inline-block bg-chat-border rounded px-1.5 py-0.5">{model.params}</span>}
                  {model.quant && <span className="inline-block bg-chat-border rounded px-1.5 py-0.5">{model.quant}</span>}
                </div>
              </div>
            </div>
          )
        })}

        <div className="px-4 py-2 text-xs uppercase tracking-wider text-chat-text-secondary font-semibold mt-4 flex items-center justify-between">
          <span>群聊</span>
          <button onClick={onCreateGroup} className="p-1 rounded-md hover:bg-chat-hover transition-colors text-chat-text"><Plus size={14} /></button>
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
              className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors ${
                isActive ? 'bg-chat-active' : 'hover:bg-chat-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-full bg-chat-accent text-white flex items-center justify-center text-lg shrink-0 shadow-sm">
                👥
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[15px] font-medium text-chat-text truncate">{group.name}</div>
                <div className="text-xs text-chat-text-secondary truncate mt-0.5">{group.members.length} 个成员</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}