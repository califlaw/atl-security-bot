from typing import Any, Dict, List

from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from src.scheduler_jobs.referrals import top_referrals_callback

# rules see on page of `apscheduler`, similar like crontab tasks
# https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
queue: List[Dict[str, Any]] = [
    {
        "name": "top_referrals",
        "func": top_referrals_callback,
        "rule": CronTrigger.from_crontab("0 9,14,21 * * *"),
        "periodic_data": {},
        "job_kwargs": {},
    }
]


def registration_queue(application: Application) -> None:
    for job in queue:
        if isinstance(job.get("rule", None), CronTrigger):
            application.job_queue.run_custom(
                callback=job["func"],
                name=job["name"],
                job_kwargs={
                    "trigger": job["rule"],
                    **job.get("job_kwargs", {}),
                },
            )
        else:
            application.job_queue.run_custom(
                callback=job["func"],
                name=job["name"],
                data=job.get("job_kwargs", {}),
                **job.get("periodic_data", {}),
            )
