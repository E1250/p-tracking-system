import gradio as gr
import asyncio

from backend_client import check_backend_health, send_frame_to_websocket


def wrapper(image, camera_id):
    return asyncio.run(send_frame_to_websocket(image, camera_id))


with gr.Blocks() as demo:
    # On load - Refresh every 60 Seconds
    status_indicator = gr.Markdown("Checking Server Status")
    demo.load(fn=check_backend_health, outputs=status_indicator)
    gr.Timer(60).tick(
        fn=check_backend_health, outputs=status_indicator
    )  # Also check backend connectivity every 60 seconds

    gr.Markdown(
        """
        # Tracking System demo  
        A fast way to test the system just by uploading an image, Please make sure you check the guide to be able to use it.
        """
    )

    with gr.Accordion("How to use this system", open=False):
        gr.Markdown(
            """
            1. Make sure first backend is opened [HF Backend](https://huggingface.co/spaces/e1250/tracking_system_backend).
                * If it is inactive, activate it or reach out to me.
                * There is an indicator at the top of the page showing if the server is online or offline
            2. Open Vercel Dashboard and make sure you create a line and place a camera with an id. [Dashboard Vercel](https://p-tracking-system.vercel.app/)
            3. Open Gradio, Make sure you add the same `camera_id`, upload an image, then click send
            4. Go back into the dashboard, Give it couple of seconds (Due to HF env limitation - CPU). then see the updates     
            5. Feel free also to take a look on Prometheus - [Prometheus Metrics](https://e1250-tracking-system-backend.hf.space/metrics/)  
            ---
            - [Github Repo](https://github.com/E1250/p-tracking_system)
            """
        )

    with gr.Row():
        with gr.Column():
            camera_id = gr.Textbox(
                label="Camera ID", placeholder="Enter Camera ID", value="from_gradio"
            )
            outputs = gr.Textbox(label="Results", value="None")
            send_btn = gr.Button("Send")

        image_input = gr.Image(type="filepath", label="Upload Image")

    gr.Examples(
        examples=[
            # Each list is just one example
            # TODO: Add values later
            [
                "https://www.tdi.texas.gov/tips/artwork/protecting-family-from-fire-danger-on-page.jpg"
            ]
        ],
        inputs=[image_input, camera_id],
        cache_examples=False,
    )

    send_btn.click(fn=wrapper, inputs=[image_input, camera_id], outputs=outputs)

demo.launch(share=True)
