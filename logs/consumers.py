"""WebSocket consumer for real-time log alerts."""

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class LogConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer that broadcasts anomaly alerts to all connected clients."""

    async def connect(self):
        await self.channel_layer.group_add("logs", self.channel_name)
        await self.accept()
        logger.info("WebSocket client connected: %s", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("logs", self.channel_name)
        logger.info("WebSocket client disconnected: %s (code=%s)", self.channel_name, close_code)

    async def receive(self, text_data):
        """Echo received messages (for testing / heartbeat)."""
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({"message": f"Received: {data}"}))

    async def send_alert(self, event):
        """
        Handle anomaly alert broadcast.

        Expects event with keys: message, level, timestamp.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message": event.get("message", ""),
                    "level": event.get("level", "INFO"),
                    "timestamp": event.get("timestamp", ""),
                }
            )
        )
