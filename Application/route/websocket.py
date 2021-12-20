from fastapi import WebSocket, WebSocketDisconnect

from ..container import RouteContainer


class WebSocketRoute(RouteContainer):
    def route(self):
        @self.app.websocket("/ws/add_watcher/{event}")
        async def websocket_endpoint(websocket: WebSocket, event: str):
            await websocket.accept()
            await self.push_event_manager.add_watcher(event, websocket)
            try:
                await websocket.receive()

            except WebSocketDisconnect:
                print(event + " disconnect")

            finally:
                self.push_event_manager.remove_watcher(event, websocket)
