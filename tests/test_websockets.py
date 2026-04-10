import asyncio
import websockets
import cv2 as cv
import traceback


async def test_websocket(camera_id: str = "test_camera_id"):
    # Don't forget to add the camera id. or it will broke.
    uri = f"ws://127.0.0.1:8000/detectors/stream/{camera_id}"
    # uri = f"wss://e1250-tracking-system-backend.hf.space/detectors/stream/{camera_id}"

    loop = asyncio.get_running_loop()

    try:
        async with websockets.connect(
            uri,
            # additional_headers={'Origin': "https://e1250-tracking-system-backend.hf.space"}
        ) as websocket:
            while True:
                # Wrapping parts that might take abit long time to avoid parallel blocking.
                def load_encode():
                    # Loading the image.
                    image = cv.imread(
                        r"G:\MyComputer\Workspace\Projects\gp-tracking-dashboard\tracking_dashboard\dummy_data\home fire smoke.jpg"
                    )

                    # The best way to send the image to the backend, is by encoding and decoding it,
                    # As it will still contains its details like the shape,
                    # otherwide, you will always need the image shape to decode again, which is not good at all.
                    # Encode the image and send to socket
                    _, encoded_image = cv.imencode(".jpg", image)

                    return encoded_image

                encoded_image = await loop.run_in_executor(None, load_encode)
                await websocket.send(
                    encoded_image.tobytes()
                )  # Sending image as metadata bytes.

                # Waiting for the server socket response.
                response = (
                    await websocket.recv()
                )  # Note that this blocks the thread until receiving a value.
                print(response)

                # trying to test under small amount of frames.
                await asyncio.sleep(2)

    except Exception as e:
        traceback.print_exc()
        print(e)


if __name__ == "__main__":
    # We use this to enable async and await in our functions.
    asyncio.run(test_websocket(camera_id="test_camera_id"))
