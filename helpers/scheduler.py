from apscheduler.schedulers.background import BackgroundScheduler

from apps.product.views import schedule_api



def start(givenTime):
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_api, 'interval', seconds = givenTime, id='Schedule Deneme', replace_existing=True)
    scheduler.start()