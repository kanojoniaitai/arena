import { useState, useEffect, useRef, useCallback } from 'react'
import type { WSMessage, ChatType } from '../types'

interface UseChatSocketReturn {
  lastMessage: WSMessage | null
  sendMessage: (
    chatType: ChatType,
    modelName: string | undefined,
    groupId: string | undefined,
    message: string,
    history: { role: string; content: string; sender?: string; display_name?: string; side?: string }[],
    extra?: { debate_id?: string; story_id?: string; undercover_id?: string; werewolf_id?: string }
  ) => void
  isConnected: boolean
}

export function useChatSocket(): UseChatSocketReturn {
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = import.meta.env.DEV ? '8000' : window.location.port
    const url = `${protocol}//${host}:${port}/ws/chat`

    const ws = new WebSocket(url)

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onclose = () => {
      setIsConnected(false)
      wsRef.current = null
      reconnectTimerRef.current = setTimeout(() => {
        connect()
      }, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }

    ws.onmessage = (event) => {
      try {
        const data: WSMessage = JSON.parse(event.data)
        setLastMessage(data)
      } catch {
        // ignore parse errors
      }
    }

    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((
    chatType: ChatType,
    modelName: string | undefined,
    groupId: string | undefined,
    message: string,
    history: { role: string; content: string; sender?: string; display_name?: string; side?: string }[],
    extra?: { debate_id?: string; story_id?: string; undercover_id?: string; werewolf_id?: string }
  ) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const msg: WSMessage = {
        type: 'chat',
        chat_type: chatType,
        model_name: modelName,
        group_id: groupId,
        debate_id: extra?.debate_id,
        story_id: extra?.story_id,
        undercover_id: extra?.undercover_id,
        werewolf_id: extra?.werewolf_id,
        message,
        history,
      }
      wsRef.current.send(JSON.stringify(msg))
    }
  }, [])

  return { lastMessage, sendMessage, isConnected }
}
