import { useState } from 'react'
import { X } from 'lucide-react'
import type { ModelInfo } from '../types'

interface CreateStoryModalProps {
  models: ModelInfo[]
  open: boolean
  onClose: () => void
  onCreate: (name: string, members: string[], opening: string) => void
}

export default function CreateStoryModal({ models, open, onClose, onCreate }: CreateStoryModalProps) {
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [opening, setOpening] = useState('')

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
    if (!name.trim() || selected.size === 0 || !opening.trim()) return
    onCreate(name.trim(), Array.from(selected), opening.trim())
    setName('')
    setSelected(new Set())
    setOpening('')
  }

  const canCreate = name.trim().length > 0 && selected.size > 0 && opening.trim().length > 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl w-[440px] max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-wechat-border">
          <span className="text-sm font-medium text-wechat-text">📖 创建故事接龙</span>
          <button onClick={onClose} className="p-1 rounded hover:bg-wechat-hover text-wechat-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">故事名称</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="例如：奇幻冒险"
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green"
            />
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">故事开头</label>
            <textarea
              value={opening}
              onChange={e => setOpening(e.target.value)}
              placeholder="写下故事的开头，模型们将轮流续写..."
              rows={3}
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green resize-none"
            />
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">选择叙述者（按选择顺序接龙）</label>
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
                    className="accent-wechat-green"
                  />
                  <span className="text-lg">{model.avatar || '🤖'}</span>
                  <span className="text-sm text-wechat-text">{model.display_name}</span>
                  {selected.has(model.name) && (
                    <span className="text-xs text-wechat-text-secondary ml-auto">
                      第{Array.from(selected).indexOf(model.name) + 1}位
                    </span>
                  )}
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
            className="flex-1 py-2 rounded-md bg-story-accent text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          >
            开始接龙
          </button>
        </div>
      </div>
    </div>
  )
}
