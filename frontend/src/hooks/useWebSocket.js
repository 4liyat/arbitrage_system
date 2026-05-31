import { useEffect, useRef, useCallback } from "react"

export function useWebSocket(url, onMessage) {
  const ws = useRef(null)
  const reconnectTimer = useRef(null)

  const connect = useCallback(() => {
    // Determine protocol: use wss if the current page is secure (https)
    const protocol = window.location.protocol === "https:" ? "wss" : "ws"
    
    // Clean URL: remove any existing protocol and ensure it starts with //
    const cleanUrl = url.replace(/^wss?:\/\//, '')
    const fullUrl = `${protocol}://${cleanUrl}`

    console.log(`Connecting to WebSocket: ${fullUrl}`)
    ws.current = new WebSocket(fullUrl)
    ws.current.onmessage = (e) => {
      try { onMessage(JSON.parse(e.data)) }
      catch (_) {}
    }
    ws.current.onclose = () => {
      console.warn("WebSocket disconnected. Attempting to reconnect in 3 seconds...");
      reconnectTimer.current = setTimeout(connect, 3000)
    }
  }, [url, onMessage])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])
}
