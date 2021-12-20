from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from .event import PushEventManager
from .route.auth import AuthRoute
from .route.stock import StockRoute
from .route.websocket import WebSocketRoute
from .schedule.crawler import CrawlingJob
from .scheduler import Scheduler
from .session import SessionManager

App = FastAPI()

session_manager = SessionManager()
push_event_manager = PushEventManager()
scheduler = Scheduler(AsyncIOScheduler(), push_event_manager)

WebSocketRoute().attach(App, push_event_manager, session_manager)
AuthRoute().attach(App, push_event_manager, session_manager)
StockRoute().attach(App, push_event_manager, session_manager)

scheduler.register_job(CrawlingJob())
scheduler.start()
