import { useState } from 'react'
import { X } from 'lucide-react'
import type { ModelInfo } from '../types'

interface CreateDebateModalProps {
  models: ModelInfo[]
  open: boolean
  onClose: () => void
  onCreate: (topic: string, proModel: string, conModel: string, maxRounds: number) => void
}

export default function CreateDebateModal({ models, open, onClose, onCreate }: CreateDebateModalProps) {
  const [topic, setTopic] = useState('')
  const [proModel, setProModel] = useState('')
  const [conModel, setConModel] = useState('')
  const [maxRounds, setMaxRounds] = useState(3)

  if (!open) return null

  const handleCreate = () => {
    if (!topic.trim() || !proModel || !conModel) return
    onCreate(topic.trim(), proModel, conModel, maxRounds)
    setTopic('')
    setProModel('')
    setConModel('')
    setMaxRounds(3)
  }

  const canCreate = topic.trim().length > 0 && proModel && conModel

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl w-[440px] max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-wechat-border">
          <span className="text-sm font-medium text-wechat-text">⚔️ 创建辩论擂台</span>
          <button onClick={onClose} className="p-1 rounded hover:bg-wechat-hover text-wechat-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">辩论话题</label>
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="例如：咖啡好还是茶好"
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green"
            />
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">正方辩手</label>
            <select
              value={proModel}
              onChange={e => setProModel(e.target.value)}
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green bg-white"
            >
              <option value="">选择正方模型</option>
              {models.map(model => (
                <option key={model.name} value={model.name}>
                  {model.avatar} {model.display_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">反方辩手</label>
            <select
              value={conModel}
              onChange={e => setConModel(e.target.value)}
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green bg-white"
            >
              <option value="">选择反方模型</option>
              {models.map(model => (
                <option key={model.name} value={model.name}>
                  {model.avatar} {model.display_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">最大轮数</label>
            <div className="flex items-center gap-2">
              {[1, 3, 5, 7].map(n => (
                <button
                  key={n}
                  onClick={() => setMaxRounds(n)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    maxRounds === n
                      ? 'bg-debate-pro text-white'
                      : 'bg-wechat-bg text-wechat-text-secondary hover:bg-wechat-hover'
                  }`}
                >
                  {n} 轮
                </button>
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
            className="flex-1 py-2 rounded-md bg-debate-pro text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          >
            开始辩论
          </button>
        </div>
      </div>
    </div>
  )
}
