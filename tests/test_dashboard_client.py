import asyncio
from fastapi import WebSocketDisconnect
import websockets
import traceback

async def test_dashboard_client():
    # Don't forget to make sure the camera is streaming, or it will broke, as it is a realtime. 
    uri = "ws://127.0.0.1:8000/dashboard/stream"
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                response = await websocket.recv()
                print(response)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        traceback.print_exc()
        print(e)


if __name__ == "__main__":
    asyncio.run(test_dashboard_client())