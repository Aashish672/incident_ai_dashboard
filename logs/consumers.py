import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join group
        await self.channel_layer.group_add("logs", self.channel_name)
        await self.accept()
        print("✅ WebSocket connected and joined group 'logs'")

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard("logs", self.channel_name)
        print("❌ WebSocket disconnected")

    async def receive(self, text_data):
        # Echo received message (raw testing)
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({
            'message': f"Received: {data}"
        }))

    async def send_alert(self, event):
        # Event handler to send alert → Must match group_send "type"
        print("📡 Sending alert to frontend via WebSocket:", event["message"])
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'level': event.get('level', 'INFO'),
            'timestamp': event.get('timestamp', ''),
        }))
