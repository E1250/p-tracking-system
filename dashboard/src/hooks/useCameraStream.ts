import {useEffect, useRef, useState} from "react"

export function useCameraStream(serverURL: string){
    
    // List of camera by their "camera_id": {...data}
    const [cameras, setCameras] = useState<Record<string, {}>>()
    // Contains websocket ref, it is not state as we don't want to re-render.
    const wsRef = useRef<WebSocket>(null)

    // After rendring, useEffect works
    useEffect(() => {
        // Start connection
        const ws = new WebSocket(serverURL)
        wsRef.current = ws

        // Fires everytime the backend sends a frame.
        ws.onmessage = (message) => {
            // Parsing the raw JSON
            const data = JSON.parse(message.data)
            setCameras(data)
        }
        // Clean and undo when the component unmounts.
        return () => ws.close()

    }, [serverURL])  // This means, re-run if the url changes. 

    return cameras
}