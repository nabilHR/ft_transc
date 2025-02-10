import json
import redis.asyncio as redis
from channels.generic.websocket import AsyncConsumer

class OnlineStatusConsumer(AsyncConsumer):
    async def connect(self):
        self.user = self.scope['user']  # Get authenticated user
        print("im here ")
        return

        await self.redis.set(f"user:{self.user.id}:status", "online")  # Directly set status
        await self.broadcast_status()  # Broadcast status (simplified)
        await self.accept()
        print(f"WebSocket connected for user {self.user.id}")

    async def disconnect(self, close_code):
        await self.redis.set(f"user:{self.user.id}:status", "offline")
        await self.broadcast_status()  # Broadcast status
        await self.redis.close()
        print(f"WebSocket disconnected for user {self.user.id}")

    async def broadcast_status(self):
        status = await self.redis.get(f"user:{self.user.id}:status")
        message = {
            "user_id": self.user.id,
            "username": self.user.username,
            "online": status.decode() == "online" if status else False,  # Handle potential None
        }
        # Broadcast to *all* connected users (you might want to refine this)
        await self.channel_layer.group_send(
            "online_status",  # Group name
            {"type": "user_status_update", "message": json.dumps(message)},
        )

    async def receive(self, text_data):  # Handle other actions if needed
        pass

    async def user_status_update(self, event):  # Group message handler
        await self.send(text_data=event["message"])

    async def websocket_connect(self, event):
        await self.connect()

    async def websocket_disconnect(self, event):
        await self.disconnect(event['code'])