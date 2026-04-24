import requests
import gradio as gr
import websockets


def check_backend_health():
    """Checking if backend is live.."""
    health_url = "https://e1250-tracking-system-backend.hf.space/health/live"
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return '<b style="color: green"> Backend Server Online </b>'
        else:
            return '<b style="color: red"> Backend Server Offline </b>'
    except Exception:
        return gr.Warning("Backend Server Error, {e}")


async def send_frame_to_websocket(image_path: str | None, camera_id: str | None):
    if image_path is None:
        raise gr.Error("No Image provided")
    if camera_id == "":
        raise gr.Error("Camera ID is requried")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # uri = f"ws://127.0.0.1:8000/detectors/stream/{camera_id}"
    uri = f"wss://e1250-tracking-system-backend.hf.space/detectors/stream/{camera_id}"

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(image_bytes)
            gr.Info("Great, now go to the Dashboard to check the updates")
            return f"Frame was sent to {camera_id}.."

    except Exception as e:
        gr.Error("Error while connecting and sending the frame..")
        return f"Error: {e}"
