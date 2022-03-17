from apscheduler.schedulers.background import BackgroundScheduler

from apps.product.views import check_all_product_prices


def start(givenTime):
    scheduler = BackgroundScheduler(
        {'apscheduler.timezone': 'Europe/Istanbul'})
    scheduler.add_job(check_all_product_prices,
                      'interval', seconds=givenTime, id='compare_prices', replace_existing=True)
    scheduler.start()
