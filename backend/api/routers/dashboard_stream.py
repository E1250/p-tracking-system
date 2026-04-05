from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.routers.metrics import active_dashboards 
import asyncio
import traceback
import redis.asyncio as aioredis

router = APIRouter()

@router.websocket("/stream")
async def dashboard_websocket(websocket: WebSocket):
    """
    WebScoket sending updates to the dashboard. 

    url: ws://127.0.0.1:8000/dashboard/stream
    """
    state = websocket.app.state
    logger = state.logger
    redis = state.redis

    # Accept the client connection. 
    await websocket.accept()

    # Logging and tracking 
    active_dashboards.inc()
    logger.info("Dashboard Connected...")

    pubsub = redis.pubsub()
    await pubsub.subscribe("dashboard_stream")

    try:

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)

            if message:
                logger.debug("Sending updates to Dashboard...")
                await websocket.send_text(message["data"])

            await asyncio.sleep(0.01)  # giving time to detect server disconnection. 
                

    except WebSocketDisconnect:
        logger.warn("Dashboard Disconnected Normally...")

    except Exception as e:
        logger.error(f"Dashboard Error: {e}")
        traceback.print_exc()

    finally:
        active_dashboards.dec()
        await pubsub.unsubscribe("dashboard_stream")
        await pubsub.close()