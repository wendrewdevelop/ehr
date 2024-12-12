import asyncio
from sockets import WebSocketManager


async def test_websocket():
    uri = "wss://echo.websocket.events"
    request = WebSocketManager(uri)
    ws = request.websocket_connect(uri)

    await ws.connect()
    await ws.send_message("Hello WebSocket!")
    response = await ws.receive_message()
    print(f"Response: {response}")
    await ws.close()

asyncio.run(test_websocket())
