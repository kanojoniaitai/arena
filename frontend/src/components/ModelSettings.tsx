import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import type { ModelInfo } from '../types'

interface ModelSettingsProps {
  model: ModelInfo | null
  open: boolean
  onClose: () => void
  onSave: (name: string, avatar: string, systemPrompt: string, displayName: string, params: {
    temperature: number
    max_tokens: number
    top_p: number
    repeat_penalty: number
  }) => void
}

export default function ModelSettings({ model, open, onClose, onSave }: ModelSettingsProps) {
  const [avatar, setAvatar] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(2048)
  const [topP, setTopP] = useState(0.95)
  const [repeatPenalty, setRepeatPenalty] = useState(1.05)

  useEffect(() => {
    if (model) {
      setAvatar(model.avatar)
      setSystemPrompt(model.system_prompt)
      setDisplayName(model.display_name || model.name)
      setTemperature(model.temperature ?? 0.7)
      setMaxTokens(model.max_tokens ?? 2048)
      setTopP(model.top_p ?? 0.95)
      setRepeatPenalty(model.repeat_penalty ?? 1.05)
    }
  }, [model])

  if (!model || !open) return null

  const handleSave = () => {
    onSave(model.name, avatar, systemPrompt, displayName, {
      temperature,
      max_tokens: maxTokens,
      top_p: topP,
      repeat_penalty: repeatPenalty
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative w-[320px] bg-white h-full shadow-lg flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-wechat-border">
          <span className="text-sm font-medium text-wechat-text">{model.name}</span>
          <button onClick={onClose} className="p-1 rounded hover:bg-wechat-hover text-wechat-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-full bg-wechat-bg flex items-center justify-center text-3xl">
              {avatar || '🤖'}
            </div>
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">显示名称</label>
            <input
              type="text"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              placeholder={model.name}
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green"
            />
          </div>

          <div>
            <label className="block text-xs text-wechat-text-secondary mb-1">头像 (Emoji 或 URL)</label>
            <input
              type="text"
              value={avatar}
              onChange={e => setAvatar(e.target.value)}
              className="w-full px-3 py-1.5 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green"
            />
          </div>

          <div className="border-t border-wechat-border pt-3">
            <div className="text-xs font-medium text-wechat-text mb-2">生成参数</div>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-wechat-text-secondary mb-1">
                  <label>Temperature (随机性)</label>
                  <span>{temperature.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={e => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-wechat-green"
                />
                <div className="flex justify-between text-[10px] text-wechat-text-secondary">
                  <span>精确</span>
                  <span>平衡</span>
                  <span>创意</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-wechat-text-secondary mb-1">
                  <label>Max Tokens (最大长度)</label>
                  <span>{maxTokens}</span>
                </div>
                <input
                  type="range"
                  min="256"
                  max="8192"
                  step="256"
                  value={maxTokens}
                  onChange={e => setMaxTokens(parseInt(e.target.value))}
                  className="w-full accent-wechat-green"
                />
                <div className="flex justify-between text-[10px] text-wechat-text-secondary">
                  <span>256</span>
                  <span>4096</span>
                  <span>8192</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-wechat-text-secondary mb-1">
                  <label>Top P (多样性)</label>
                  <span>{topP.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.05"
                  value={topP}
                  onChange={e => setTopP(parseFloat(e.target.value))}
                  className="w-full accent-wechat-green"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs text-wechat-text-secondary mb-1">
                  <label>Repeat Penalty (重复惩罚)</label>
                  <span>{repeatPenalty.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="2"
                  step="0.05"
                  value={repeatPenalty}
                  onChange={e => setRepeatPenalty(parseFloat(e.target.value))}
                  className="w-full accent-wechat-green"
                />
              </div>
            </div>
          </div>

          <div className="border-t border-wechat-border pt-3">
            <label className="block text-xs text-wechat-text-secondary mb-1">系统提示词</label>
            <textarea
              value={systemPrompt}
              onChange={e => setSystemPrompt(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 rounded-md border border-wechat-border text-sm text-wechat-text outline-none focus:border-wechat-green resize-none"
            />
          </div>
        </div>

        <div className="p-4 border-t border-wechat-border">
          <button
            onClick={handleSave}
            className="w-full py-2 rounded-md bg-wechat-green text-white text-sm font-medium hover:bg-wechat-green-dark transition-colors"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  )
}
