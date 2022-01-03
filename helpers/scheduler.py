from apscheduler.schedulers.background import BackgroundScheduler

from apps.product.views import compare_price_with_old_price_async, get_html_content_from_hepsiburada, get_html_content_from_trendyol


def start(givenTime):
    scheduler = BackgroundScheduler(
        {'apscheduler.timezone': 'Europe/Istanbul'})
    scheduler.add_job(lambda: compare_price_with_old_price_async(get_html_content_from_hepsiburada),
                      'interval', seconds=givenTime, id='schedule-hepsi-burada', replace_existing=True)
    scheduler.add_job(lambda: compare_price_with_old_price_async(get_html_content_from_trendyol),
                      'interval', seconds=givenTime, id='schedule-trendyol', replace_existing=True)
    # scheduler.start()
