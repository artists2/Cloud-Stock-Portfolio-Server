from __future__ import annotations

from typing import List

from apscheduler.schedulers.base import BaseScheduler

from .container import JobContainer
from .event import PushEventManager


class Scheduler:
    scheduler: BaseScheduler
    push_event_manager: PushEventManager
    jobs: List[JobContainer]

    def __init__(self, scheduler, push_event_manager):
        self.scheduler = scheduler
        self.push_event_manager = push_event_manager
        self.jobs = list()

    def register_job(self, job: JobContainer):
        job.attach(scheduler=self.scheduler, listener=self.push_event_manager)
        self.jobs.append(job)

    def start(self):
        self.scheduler.start()
