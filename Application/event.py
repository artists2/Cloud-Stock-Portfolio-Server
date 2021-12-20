import asyncio
from typing import Dict, List

from fastapi import WebSocket


class PushEventManager:
    connections: Dict[str, List[WebSocket]]

    def __init__(self):
        self.connections = dict()

    async def add_watcher(self, event, websocket: WebSocket):
        if event not in self.connections:
            self.connections[event] = list()

        self.connections[event].append(websocket)

    async def push(self, event, **kwargs):
        if event not in self.connections:
            return
        await asyncio.gather(*[conn.send_json({"event": event, **kwargs}) for conn in self.connections.get(event)])

    def remove_watcher(self, event, websocket: WebSocket):
        if event not in self.connections:
            return

        self.connections[event].remove(websocket)
