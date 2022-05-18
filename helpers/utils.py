from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string
import time

headers_list_trendyol = [
    {'authority': 'www.trendyol.com',
     'cache-control': 'max-age=0',
     'sec-ch-ua': '"Opera GX";v="83", "Chromium";v="97", ";Not A Brand";v="99"',
     'sec-ch-ua-mobile': '?0',
     'sec-ch-ua-platform': '"Windows"',
     'upgrade-insecure-requests': '1',
     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
     'sec-fetch-site': 'none',
     'sec-fetch-mode': 'navigate',
     'sec-fetch-user': '?1',
     'sec-fetch-dest': 'document',
     'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7', },
    {
        'authority': 'www.trendyol.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Opera GX";v="83", "Chromium";v="97", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
]

headers_list_hepsiburada = [{
    'authority': 'www.hepsiburada.com',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Opera GX";v="83", "Chromium";v="97", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.hepsiburada.com/samsung-galaxy-m21-64-gb-samsung-turkiye-garantili-p-HBV00000VSEEF?magaza=Teknopa%20Gsm',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}, ]


class SScraper:

    def __init__(self):
        self.driver_path = "/usr/local/bin/chromedriver"
        self.options = webdriver.ChromeOptions()
        self.set_chrome_options()
        self.delay = 5

    def set_chrome_options(self):
        self.options.add_argument(" - incognito")
        self.options.add_argument("--headless")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')

    def get_reviews_from_hepsiburada(self, url):
        url = url.split("?")[0]
        url = f'{url}-yorumlari'
        browser = webdriver.Chrome(
            executable_path=self.driver_path, chrome_options=self.options)
        browser.set_window_size(340, 695)
        browser.get(url)
        reviews = list()
        while True:
            WebDriverWait(browser, self.delay).until(EC.invisibility_of_element_located((By.XPATH,'//div[@class="hermes-Loading-module-TjXG2"]')))

            try:
                WebDriverWait(browser, self.delay*3).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@itemprop="description"]')))
            except:
                browser.save_screenshot('deneme.png')
                print("DENEME: ",browser.get_window_size())
            if len(results := browser.find_elements(By.XPATH, '//span[@itemprop="description"]')) > 0:
                print("seleniumcu: girdi")
                for review in results:
                    reviews.append(review.text)
            else:
                print("seleniumcu: girmedi")
                break

            if len(next_p := browser.find_elements(By.XPATH, "//div[@class='hermes-MobilePageHolder-module-tOBj6' and text()='Sonraki']")) > 0:
                browser.execute_script("arguments[0].click();",next_p[0])
            else:
                break
        print(f'seleniumcu {len(reviews)}')
        return reviews

    def get_reviews_from_trendyol(self, url):
        reviews = list()
        try:
            browser = webdriver.Chrome(
                executable_path=self.driver_path, chrome_options=self.options)
            browser.get(url)
            browser.find_element(By.CSS_SELECTOR, 'a.rvw-cnt-tx').click()
            WebDriverWait(browser, self.delay).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.rnr-com-w')))
            css_selector = '.rnr-com-w .rnr-com-tx'
            last_element_in_page = ''
            while True:
                find_current_last_element = "let reviewList = document.querySelectorAll(\'" + css_selector + \
                    "\'); reviewList[reviewList.length - 1].scrollIntoView(); return reviewList[reviewList.length - 1];"
                current_last_element = browser.execute_script(
                    find_current_last_element)

                if (last_element_in_page != current_last_element):
                    last_element_in_page = current_last_element
                    time.sleep(self.delay)
                else:
                    break
            reviewWrapperDiv = browser.find_element(
                By.CSS_SELECTOR, '.pr-rnr-com')

            allReviewWrappers = reviewWrapperDiv.find_elements(
                By.CSS_SELECTOR, css_selector)

            reviews = [review.text for review in allReviewWrappers]
        finally:
            browser.quit()
            return reviews


class BSScraper:

    not_on_sale = "Ürün satışta değil."
    not_discounted = "Ürün indirimde değil."
    has_no_rating = "Ürünün değerlendirmesi bulunmuyor."
    cant_scrape_data = "Ürün kazınamadı."

    def __init__(self):
        self.session = requests.Session()
        self.data = dict()

    def get_link(self, url, header_list):
        self.session.headers = random.choice(header_list)
        # w.sleep(random.random()*3)
        html_content = self.session.get(url).text
        return html_content

    def parse_product_from_trendyol(self, url=None, soup=None):
        if url:
            data = self.get_link(url, headers_list_trendyol)
            soup = BeautifulSoup(data, "html.parser")

        script_tag = soup.select_one(
            selector="script:-soup-contains('window.__PRODUCT_DETAIL_APP_INITIAL_STATE__')")

        if script_tag is None:
            return self.cant_scrape_data

        pattern = "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__=(.+?});"
        raw_data = re.findall(pattern, script_tag.string, re.S)

        if raw_data:
            self.data = json.loads(raw_data[0])['product']

            self.data.pop("otherMerchants")
            self.data.pop('otherMerchantVariants')

        return self.data

    def get_product_description_from_trendyol(self, soup=None, url=None):
        if url:
            data = self.get_link(url, headers_list_trendyol)
            soup = BeautifulSoup(data, 'html.parser')

            try:
                description = soup.find(
                    "h1", attrs={"class": "pr-new-br"}).get_text()
            except:
                description = self.cant_scrape_data
            finally:
                return description
        else:
            if self.data:
                return " ".join([self.data['metaBrand']['name'], self.data['nameWithProductCode']])
            else:
                return self.cant_scrape_data

    def get_product_price_from_trendyol(self, soup=None, url=None):
        product = dict()
        if url:
            data = self.get_link(url, headers_list_trendyol)
            soup = BeautifulSoup(data, "html.parser")

            product['original_price'] = dict()
            product['discounted_price'] = dict()

            product['original_price']['text'] = self.not_on_sale
            product['original_price']['value'] = 0.0
            product['discounted_price']['text'] = self.not_on_sale
            product['discounted_price']['value'] = 0.0

            price_container = soup.find(
                "div", attrs={"class": "product-price-container"})

            if price_container is None:
                product['original_price']['text'] = self.cant_scrape_data
                product['discounted_price']['text'] = self.cant_scrape_data

            else:
                original_price = price_container.find(
                    "span", attrs={"class": "prc-org"})

                discounted_price = price_container.find(
                    "span", attrs={"class": "prc-dsc"})

                if original_price and discounted_price:
                    product['original_price']['text'] = original_price.get_text()
                    product['original_price']['value'] = convert_comma_price_to_float(
                        product['original_price']['text'])
                    product['discounted_price']['text'] = discounted_price.get_text()
                    product['discounted_price']['value'] = convert_comma_price_to_float(
                        product['discounted_price']['text'])

                elif discounted_price:
                    product['original_price']['text'] = discounted_price.get_text()
                    product['original_price']['value'] = convert_comma_price_to_float(
                        product['original_price']['text'])
                    product['discounted_price']['text'] = product['original_price']['text']
                    product['discounted_price']['value'] = product['original_price']['value']

            return product

        else:
            if self.data:
                original_price = self.data['price']['originalPrice']
                discounted_price = self.data['price']['discountedPrice']

                product['original_price'] = original_price
                product['discounted_price'] = discounted_price

                if original_price['value'] == discounted_price['value']:
                    product['discounted_price']['text'] = product['original_price']['text']

            else:
                product['original_price']['value'] = 0.0
                product['original_price']['text'] = self.cant_scrape_data
                product['discounted_price']['value'] = 0.0
                product['discounted_price']['text'] = self.cant_scrape_data

            return product

    def get_product_image_source_from_trendyol(self, soup=None, url=None):

        if url:
            data = self.get_link(url, headers_list_trendyol)
            soup = BeautifulSoup(data, "html.parser")
            try:
                image_source = soup.find(
                    "div", attrs={"class": "gallery-modal-content"}).find("img").get("src")
            except:
                image_source = self.cant_scrape_data
            finally:
                return image_source

        else:
            if self.data:
                image_source = "".join(
                    ["https://cdn.dsmcdn.com", self.data['images'][0]])
            else:
                image_source = self.cant_scrape_data
            return image_source

    def get_product_review_count_from_trendyol(self, soup=None, url=None):
        if url:
            data = self.get_link(url, headers_list_trendyol)
            soup = BeautifulSoup(data, 'html.parser')

            try:
                review_count = soup.find(
                    "a", attrs={"class": "rvw-cnt-tx"}).get_text()
            except:
                if soup.find("div", attrs={"class": "pr-in-ratings"}) is not None:
                    review_count = self.has_no_rating
                else:
                    review_count = self.cant_scrape_data
            finally:
                return review_count
        else:
            if self.data:
                review_count = self.data['ratingScore']['totalRatingCount']
                if review_count == 0:
                    review_count = self.has_no_rating

                return review_count
            else:
                return self.cant_scrape_data

    def get_product_rating_score_from_trendyol(self):
        if self.data:
            average_rating = self.data['ratingScore']['averageRating']
            if average_rating == 0:
                average_rating = self.has_no_rating

            return average_rating
        else:
            return self.cant_scrape_data

    def parse_product_from_hepsiburada(self, url=None, soup=None):
        if url:
            data = self.get_link(url, headers_list_hepsiburada)
            soup = BeautifulSoup(data, "html.parser")

        script_tag = soup.select_one(
            selector="script:-soup-contains('var productModel')")

        if script_tag is None:
            return self.cant_scrape_data

        # TODO: Bu kısımdaki pattern değişecektir.
        pattern = 'var productModel = (.+?,"suspensionDetail":.+}),"campaignDetail"'
        raw_data = re.findall(pattern, script_tag.string, re.S)

        if raw_data:
            raw_data[0] += '}'
            # dosya = open('bilgiler.txt', 'w')
            # dosya.write(raw_data[0])
            # dosya.close()
            self.data = json.loads(raw_data[0])['product']

        return self.data

    def get_product_description_from_hepsiburada(self, soup=None, url=None):
        if url:
            data = self.get_link(url, headers_list_hepsiburada)
            soup = BeautifulSoup(data, 'html.parser')

            try:
                description = soup.find(
                    "span", attrs={"class": "product-name"}).get_text()
            except:
                description = self.cant_scrape_data
            finally:
                return description
        else:
            if self.data:
                return self.data['name']
            else:
                return self.cant_scrape_data

    def get_product_price_from_hepsiburada(self, soup=None, url=None):
        product = dict()
        product['original_price'] = dict()
        product['discounted_price'] = dict()

        if url:
            data = self.get_link(url, headers_list_hepsiburada)
            soup = BeautifulSoup(data, "html.parser")

            product['original_price']['text'] = self.not_on_sale
            product['original_price']['value'] = 0.0
            product['discounted_price']['text'] = self.not_on_sale
            product['discounted_price']['value'] = 0.0

            price_container = soup.find(
                "div", attrs={"itemprop": "offers"})

            if price_container is None:
                product['original_price']['text'] = self.cant_scrape_data
                product['discounted_price']['text'] = self.cant_scrape_data

            else:
                original_price = price_container.find(
                    "del", attrs={"id": "originalPrice"})

                discounted_price = price_container.find(
                    "span", attrs={"id": "offering-price"})

                if discounted_price:
                    discounted_price = discounted_price.get_text().replace(
                        '(Adet )', '').replace('\n', ' ').replace('\r', '').strip()

                if original_price and discounted_price:
                    product['original_price']['text'] = original_price.get_text()
                    product['original_price']['value'] = convert_comma_price_to_float(
                        product['original_price']['text'])
                    product['discounted_price']['text'] = discounted_price
                    product['discounted_price']['value'] = convert_comma_price_to_float(
                        product['discounted_price']['text'])

                elif discounted_price:
                    product['original_price']['text'] = discounted_price
                    product['original_price']['value'] = convert_comma_price_to_float(
                        product['original_price']['text'])
                    product['discounted_price']['text'] = product['original_price']['text']
                    product['discounted_price']['value'] = product['original_price']['value']

            return product

        else:
            if self.data:

                if len(self.data['listings']) == 0:
                    product['original_price']['text'] = self.not_on_sale
                    product['original_price']['value'] = 0.0
                    product['discounted_price']['text'] = self.not_on_sale
                    product['discounted_price']['value'] = 0.0
                    return product

                original_price = self.data['listings'][0]['originalPriceText']
                discounted_price = self.data['listings'][0]['priceText']

                product['original_price']['text'] = original_price
                product['original_price']['value'] = convert_comma_price_to_float(
                    original_price)
                product['discounted_price']['text'] = discounted_price
                product['discounted_price']['value'] = convert_comma_price_to_float(
                    discounted_price)

                if product['original_price']['value'] == product['discounted_price']['value']:
                    product['discounted_price']['text'] = product['original_price']['text']

            else:
                product['original_price']['text'] = self.cant_scrape_data
                product['original_price']['value'] = 0.0
                product['discounted_price']['text'] = self.cant_scrape_data
                product['discounted_price']['value'] = 0.0

            return product

    def get_product_image_source_from_hepsiburada(self, soup=None, url=None):
        if url:
            data = self.get_link(url, headers_list_hepsiburada)
            soup = BeautifulSoup(data, "html.parser")
            try:
                image_source = soup.find(
                    "img", attrs={"class": "product-image"}).get("src")
            except:
                image_source = self.cant_scrape_data
            finally:
                return image_source

        else:
            if self.data:
                image_source = self.data['allImages'][0]['thumbnailUrl']
            else:
                image_source = self.cant_scrape_data
            return image_source

    def get_product_review_count_from_hepsiburada(self, soup=None, url=None):
        if url:
            data = self.get_link(url, headers_list_hepsiburada)
            soup = BeautifulSoup(data, 'html.parser')

            try:
                review_count = soup.find(
                    "a", attrs={"class": "product-comments"}).get_text()
            except:
                if soup.find("div", attrs={"class": "comments-container"}) is not None:
                    review_count = self.has_no_rating
                else:
                    review_count = self.cant_scrape_data
            finally:
                return review_count
        else:
            if self.data:
                review_count = self.data['totalReviewsCount']
                if review_count == 0:
                    review_count = self.has_no_rating

                return review_count
            else:
                return self.cant_scrape_data

    def get_product_rating_score_from_hepsiburada(self):
        if self.data:
            average_rating = self.data['ratingStar']
            if average_rating == 0:
                average_rating = self.has_no_rating

            return average_rating
        else:
            return self.cant_scrape_data


def convert_comma_price_to_float(price):
    price = price.replace('.', '').replace(',', '.').split(' ')[:-1][0]
    return float(price)


def change_url_to_company_name(url):
    return urlparse(url).netloc.split(".")[1]


# tüm harfleri küçük yap
def text_lowercase(text):
    return text.lower()


# numaraları kaldır
def remove_numbers(text):
    result = re.sub(r'\d+', '', text)
    return result


# noktalama işaretlerini kaldır
def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)


# boşlukları kaldır
def remove_whitespace(text):
    return " ".join(text.split())


# belirteç içine alma
def stem_words(text):
    stemmer = PorterStemmer()
    word_tokens = word_tokenize(text)
    stems = [stemmer.stem(word) for word in word_tokens]
    return stems


# gereksiz kelimeleri çıkarmak
def remove_stopwords(text):
    stop_words = set(stopwords.words('turkish'))
    metin = ""
    for kelime in text:
        metin = metin+" "+kelime
    word_tokens = word_tokenize(metin)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    return filtered_sentence


def text_preprocessing(text):
    text = text_lowercase(text)
    text = remove_numbers(text)
    text = remove_punctuation(text)
    text = remove_whitespace(text)
    text = stem_words(text)
    words = remove_stopwords(text)
    return words


bs = BSScraper()

# Trendyolda ürün eklerken fotoğraf eklemek zorunlu olduğundan eğer data varsa resim olmama olasılığı yoktur.
# Products - Trendyol
non_discounted_trendyol = "https://www.trendyol.com/minigimin-dolabi/sari-cicekli-elbise-p-124405018?boutiqueId=61&merchantId=272473"
discounted_trendyol = "https://www.trendyol.com/viscofoam/aloe-vera-yuksek-boyun-destekli-visco-ortopedik-yastik-p-2973463"
non_priced_trendyol = "https://www.trendyol.com/asus/gl553-gl553v-gl553vd-gl553ve-gl553vw-gl553vd-ds71-p-33623321"
non_commented_trendyol = "https://www.trendyol.com/zalman/cnps7000c-alcu-92mm-cpu-fani-p-2825652"
wierd_link_trendyol = "https://www.trendyol.com/safsafdfsf"

# Testing - Trendyol

# bs.parse_product_from_trendyol(url=discounted_trendyol)
# print(bs.get_product_rating_score_from_trendyol())
# print(bs.get_product_review_count_from_trendyol())
# print(bs.get_product_description_from_trendyol())
# print(bs.get_product_image_source_from_trendyol())
# x = time.time()
# print(bs.get_product_price_from_trendyol(
#     url=non_discounted_trendyol)['original_price'])
# print(bs.get_product_price_from_trendyol(
#     url=non_discounted_trendyol)['discounted_price'])
# print(time.time() - x)


# Products - Hepsiburada
discounted_hepsiburada = "https://www.hepsiburada.com/alcatel-1t-10-1-16-gb-klavyeli-siyah-p-HBV00000P0RHB?magaza=Leadtech"
non_discounted_hepsiburada = "https://www.hepsiburada.com/egindra-dekoratif-dogal-hasir-jut-ip-dokuma-sepet-kapakli-hasir-sepet-ozel-tasarim-p-HBCV00001MK436"
commented_hepsiburada = "https://www.hepsiburada.com/sever-29088-dekoratif-hasir-saksi-sepeti-p-HBV00000Y9P0C"
non_priced_hepsiburada = "https://www.hepsiburada.com/asus-rog-gl553ve-dm233t-intel-core-i7-7700hq-16gb-1tb-128gb-ssd-gtx1050ti-windows-10-home-15-6-fhd-tasinabilir-bilgisayar-pm-HB000007MFJ0"
wierd_link_hepsiburada = "https://www.hepsiburada.com/asdhkjsad"

# Testing - Hepsiburada

# x = time.time()
# bs.parse_product_from_hepsiburada(url=commented_hepsiburada)
# print(bs.get_product_rating_score_from_hepsiburada())
# print(bs.get_product_review_count_from_hepsiburada())
# print(time.time() - x)
# print(bs.get_product_description_from_hepsiburada())
# print(bs.get_product_image_source_from_hepsiburada())
# print(bs.get_product_price_from_hepsiburada(url=commented_hepsiburada)['original_price'])
# print(bs.get_product_price_from_hepsiburada(url=commented_hepsiburada)['discounted_price'])
