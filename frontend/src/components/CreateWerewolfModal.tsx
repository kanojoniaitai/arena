import { useState } from 'react'
import { X } from 'lucide-react'
import type { ModelInfo } from '../types'

interface CreateWerewolfModalProps {
  models: ModelInfo[]
  open: boolean
  onClose: () => void
  onCreate: (name: string, members: string[]) => void
}

const ROLE_ICONS: Record<string, string> = {
  werewolf: '🐺',
  villager: '👨‍🌾',
  seer: '🔮',
  witch: '🧙‍♀️',
  hunter: '🏹',
}

const ROLE_NAMES: Record<string, string> = {
  werewolf: '狼人',
  villager: '村民',
  seer: '预言家',
  witch: '女巫',
  hunter: '猎人',
}

export default function CreateWerewolfModal({ models, open, onClose, onCreate }: CreateWerewolfModalProps) {
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  if (!open) return null

  const toggleMember = (modelName: string) => {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(modelName)) {
        next.delete(modelName)
      } else {
        next.add(modelName)
      }
      return next
    })
  }

  const handleCreate = () => {
    if (!name.trim() || selected.size < 4) return
    onCreate(name.trim(), Array.from(selected))
    setName('')
    setSelected(new Set())
  }

  const canCreate = name.trim().length > 0 && selected.size >= 4

  const n = selected.size
  const numWolves = n < 7 ? 1 : 2
  const remaining = n - numWolves
  const specialRoles = ['seer', 'witch']
  if (remaining >= 3) specialRoles.push('hunter')
  const numVillagers = n - numWolves - Math.min(specialRoles.length, remaining)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl w-[440px] max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-wechat-border">
          <span className="text-sm font-medium text-wechat-text">🐺 创建狼人杀</span>
          <button onClick={onClose} className="p-1 rounded hover:bg-wechat-hover text-wechat-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">游戏名称</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="例如：月圆之夜"
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-werewolf-bg"
            />
          </div>

          {n >= 4 && (
            <div className="px-3 py-2 rounded-md bg-wechat-bg text-xs text-wechat-text-secondary">
              <div className="font-medium text-wechat-text mb-1">角色分配预览：</div>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-0.5 rounded bg-werewolf-wolf/10 text-werewolf-wolf">
                  🐺 狼人 ×{numWolves}
                </span>
                {specialRoles.map(r => (
                  <span key={r} className="px-2 py-0.5 rounded bg-werewolf-good/10 text-werewolf-good">
                    {ROLE_ICONS[r]} {ROLE_NAMES[r]} ×1
                  </span>
                ))}
                {numVillagers > 0 && (
                  <span className="px-2 py-0.5 rounded bg-werewolf-good/10 text-werewolf-good">
                    👨‍🌾 村民 ×{numVillagers}
                  </span>
                )}
              </div>
              <div className="mt-1">角色将随机分配，你作为上帝可以看到所有角色</div>
            </div>
          )}

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">选择玩家（至少4人）</label>
            <div className="flex flex-col gap-1 max-h-[200px] overflow-y-auto">
              {models.map(model => (
                <label
                  key={model.name}
                  className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-wechat-bg cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(model.name)}
                    onChange={() => toggleMember(model.name)}
                    className="accent-werewolf-bg"
                  />
                  <span className="text-lg">{model.avatar || '🤖'}</span>
                  <span className="text-sm text-wechat-text">{model.display_name}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-2 p-4 border-t border-wechat-border">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-md border border-wechat-border text-sm text-wechat-text hover:bg-wechat-bg transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleCreate}
            disabled={!canCreate}
            className="flex-1 py-2 rounded-md bg-werewolf-bg text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          >
            开始游戏
          </button>
        </div>
      </div>
    </div>
  )
}
