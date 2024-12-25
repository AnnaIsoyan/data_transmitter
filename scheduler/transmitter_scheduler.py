from apscheduler.schedulers.background import BackgroundScheduler
from sources import SchedulerWorker

class SendDataScheduler:
    def __init__(self):
        self.__scheduler = BackgroundScheduler(daemon=True)
        self.__schedular_worker = SchedulerWorker()

    def start_interval_scheduler(self, minutes):
        self.__scheduler.add_job(self.__schedular_worker.do_work, 'interval', minutes=minutes)
        self.__scheduler.start()
