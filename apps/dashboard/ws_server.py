from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({
            "speed": 72,
            "geofence_status": "SAFE",
            "fatigue_alert": False
        })
        await asyncio.sleep(1)
