from django.db.models.signals import post_save

from helpers.decorators import prevent_recursion
from helpers.utils import BSScraper, change_url_to_company_name

from .models import Product


@prevent_recursion
def wishlist_product(sender, instance, created, **kwargs):
    scraper = BSScraper()
    if created or instance.will_be_scraped:
        scraped_result = dynamic_function_executor_for_scraping(
            scraper, instance.product_link)
        instance.product_description = scraped_result[0]
        instance.product_original_price = scraped_result[1]['original_price']['text']
        instance.product_discounted_price = scraped_result[1]['discounted_price']['text']
        instance.product_picture_source = scraped_result[2]
        instance.product_review_count = scraped_result[3]
        instance.product_mean_rating = scraped_result[4]

    instance.will_be_scraped = False

    if instance.updated_by is not None:
        user = instance.updated_by
        user.products_added_to_wishlist.add(instance)


post_save.connect(wishlist_product, sender=Product)


def dynamic_function_executor_for_scraping(scraper_instance, url):
    domain = change_url_to_company_name(url)

    parse = getattr(
        BSScraper, f'parse_product_from_{domain}')
    parse(scraper_instance, url=url)

    description = getattr(
        BSScraper, f'get_product_description_from_{domain}')(scraper_instance)
    price = getattr(
        BSScraper, f'get_product_price_from_{domain}')(scraper_instance)
    image = getattr(
        BSScraper, f'get_product_image_source_from_{domain}')(scraper_instance)
    review_count = getattr(
        BSScraper, f'get_product_review_count_from_{domain}')(scraper_instance)
    rating_score = getattr(
        BSScraper, f'get_product_rating_score_from_{domain}')(scraper_instance)

    return description, price, image, review_count, rating_score
