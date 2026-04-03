import asyncio
from test_dashboard_client import test_dashboard_client
from test_websockets import test_websocket

async def test_server(number_of_cameras:int=1):
    camera_tasks = [test_websocket(camera_id=f"camera_{i}") for i in range(number_of_cameras)]
    dashboard_task= test_dashboard_client()

    # Running tasks together. 
    await asyncio.gather(
        *camera_tasks,
        dashboard_task,
        return_exceptions=True
        )

# Make sure you use __name__ to avoid unexpected output while testing. 
# I noticed unexpected lines to be working from the file here not expected without the  __name__ line. 
if __name__ == "__main__": 
    asyncio.run(test_server(1), debug=True)