import asyncio
import websockets


class WebSocketManager:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None

    async def connect(self):
        self.connection = await websockets.connect(self.uri)
        print(f"Connected to {self.uri}")

    async def send_message(self, message):
        if self.connection:
            await self.connection.send(message)
            print(f"Sent::: {message}")
        else:
            raise ConnectionError("WebSocket is not connected.")

    async def receive_message(self):
        if self.connection:
            message = await self.connection.recv()
            print(f"Received::: {message}")
            return message
        else:
            raise ConnectionError("WebSocket is not connected.")

    async def close(self):
        if self.connection:
            await self.connection.close()
            print(f"Connection to {self.uri} closed.")
        else:
            print("No connection to close.")

    def websocket_connect(self, uri):
        return WebSocketManager(uri)
