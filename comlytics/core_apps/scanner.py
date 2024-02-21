import requests
import csv
from bs4 import BeautifulSoup
import json
import re
import random
import time
from datetime import datetime
from decimal import Decimal
from django.db import models
from .models import SearchQuery, SearchResult




def search_conditions():
 #   condition = input('New? Y/N: ')
 #   if condition.lower() == 'y':
        return '&order=qd&stan=nowe'
 #   else:
  #      return ''

def get_url(search_conditions, keyword, i):
    user_keyword = keyword
    url_keyword = user_keyword.replace(' ', '%20')
    file_keyword = user_keyword.replace(' ', '_')
    if i == 1:
        url = f'https://allegro.pl/listing?string={url_keyword}' + search_conditions
    else:
        url = f'https://allegro.pl/listing?string={url_keyword}{search_conditions}&p={i}'
    return url, file_keyword


def get_page(url, headers, proxies, cookies):
    url, _ = url
    page = requests.get(url, headers=headers, cookies=cookies)
    return page.content

def get_json(page_content):
    soup_script = BeautifulSoup(page_content,
                                'html.parser')  # there is no need for the '.content' method becuase driver.page_                                       # source already returns a string
    div_list = soup_script.find_all('div')
    for div in div_list:
        if 'allegro.product.listing' in div.get('data-prototype-id', ''):
            listing_id = div.get('data-box-id', '')
            print(listing_id)

    extract_lisitng_json = soup_script.find('script', attrs={'data-serialize-box-id': listing_id})
    textified = extract_lisitng_json.get_text()
    return json.loads(textified)

def write_to_csv(json_object, file_keyword):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M")
    _, keyword = file_keyword
    with open(f'{keyword}_{formatted_datetime}.csv', 'w', newline='') as csv_file:
        fieldnames = ['Item_id', 'Item_title', 'Sponsored', 'Vendor', 'Alt_title', 'Promoted', 'Best Price',
                      'Parameters', 'General', 'EAN', 'Price', 'Currency', 'Has Variants', 'Variants', 'Rating',
                      'Count', 'Smart', 'Sellers Count', 'Total Units Sold', 'Total Sales Value', 'Item URL',
                      'Seller ID', 'Seller Name', 'Seller Url', 'Seller Rating', 'Super S']

        csv_write = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_write.writeheader()
        store_state = json_object['__listing_StoreState']
        for i in range(len(store_state['items']['elements'])):
            try:
                item = store_state['items']['elements'][i]
                item_id = item.get('offerId', '')
                item_isSponsored = item.get('isSponsored', '')
                item_vendor = item.get('vendor', '')
                item_title = item.get('title', {}).get('text', '')
                item_alt_title = item.get('alt', '')
                item_promoted = item.get('promoted', '')
                item_param_ = item.get('parameters', '')
                item__gen_param_ = item.get('generalParameters', '')

                ean = 'N/A'
                for photo in item.get('photos', []):
                    if 'EAN-GTIN' in photo.get('small', ''):
                        ean_match = re.search(r'\d{12,15}', photo['small'])
                        ean = ean_match.group() if ean_match else 'N/A'
                        break

                item_price = item['price']['mainPrice']['amount']
                item_currency = item['price']['mainPrice']['currency']

                seller_id = item['seller']['id']
                seller_name = item['seller']['login']
                seller_url = item['seller']['userListingUrl']
                seller_feedback = item['seller']['positiveFeedbackPercent']
                seller_supperSeller = item['title']['superSeller']

                item_best_price_guarantee = item.get('isBestPriceGuarantee', '')

                item_variants = item.get('productVariantDetails', {}).get('variantGroup', '')

                item_rating = item.get('productReview', {}).get('rating', {}).get('average', 'N/A')
                item_rating_count = item.get('productReview', {}).get('rating', {}).get('count', 0)
                item_isSmart = item['freebox']['labels'][0]['labelParts'][0]['text'] == 'Smart!'

                item_offers_count = item.get('productOffersCount', '')

                item_units_sold_match = re.search(r'\d+', item.get('productPopularity', {}).get('tooltip', ''))
                item_units_sold = item_units_sold_match.group() if item_units_sold_match else '0'

                item_sales_value = float(item_price) * int(item_units_sold)
                item_url = f'https://allegro.pl/oferta/{item_id}'

                csv_write.writerow(
                    {'Item_id': item_id, 'Item_title': item_title, 'Sponsored': item_isSponsored, 'Vendor': item_vendor,
                     'Alt_title': item_alt_title, 'Promoted': item_promoted, 'Best Price': item_best_price_guarantee,
                     'Parameters': item_param_, 'General': item__gen_param_, 'EAN': ean, 'Price': item_price,
                     'Currency': item_currency, 'Has Variants': 'x', 'Variants': item_variants,
                     'Rating': item_rating, 'Count': item_rating_count, 'Smart': item_isSmart,
                     'Sellers Count': item_offers_count,
                     'Total Units Sold': item_units_sold, 'Total Sales Value': item_sales_value, 'Item URL': item_url,
                     'Seller ID': seller_id, 'Seller Name': seller_name, 'Seller Url': seller_url,
                     'Seller Rating': seller_feedback,
                     'Super S': seller_supperSeller
                     })
            except Exception as e:
                print(f"Error processing item {i}: {e}")


def write_to_db(json_object, file_keyword):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M")
    _, keyword = file_keyword
    search_query = SearchQuery(keyword=keyword)
    search_query.save()

    for page in json_object:
        store_state = page['__listing_StoreState']

        for i in range(len(store_state['items']['elements'])):
            try:
                item = store_state['items']['elements'][i]
                item_id = item.get('offerId', '')
                item_isSponsored = item.get('isSponsored', '')
                item_vendor = item.get('vendor', '')
                item_title = item.get('title', {}).get('text', '')
                item_alt_title = item.get('alt', '')
                item_promoted = item.get('promoted', '')
                item_param_ = item.get('parameters', '')
                item__gen_param_ = item.get('generalParameters', '')

                ean = 'N/A'
                for photo in item.get('photos', []):
                    if 'EAN-GTIN' in photo.get('small', ''):
                        ean_match = re.search(r'\d{12,15}', photo['small'])
                        ean = ean_match.group() if ean_match else 'N/A'
                        break

                item_price = item['price']['mainPrice']['amount']
                item_currency = item['price']['mainPrice']['currency']

                seller_id = item['seller']['id']
                seller_name = item['seller']['login']
                seller_url = item['seller']['userListingUrl']
                seller_feedback = item['seller']['positiveFeedbackPercent']
                seller_supperSeller = item['title']['superSeller']

                item_best_price_guarantee = item.get('isBestPriceGuarantee', '')

                item_variants = item.get('productVariantDetails', {}).get('variantGroup', '')

                item_rating = item.get('productReview', {}).get('rating', {}).get('average', 'N/A')
                item_rating_count = item.get('productReview', {}).get('rating', {}).get('count', 0)
                item_isSmart = item['freebox']['labels'][0]['labelParts'][0]['text'] == 'Smart!'

                item_offers_count = item.get('productOffersCount', '')

                item_units_sold_match = re.search(r'\d+', item.get('productPopularity', {}).get('tooltip', ''))
                item_units_sold = item_units_sold_match.group() if item_units_sold_match else '0'

                item_sales_value = Decimal(item_price) * int(item_units_sold)
                item_url = f'https://allegro.pl/oferta/{item_id}'


                result = SearchResult(
                search_query = search_query,
                item_id = item_id,
                item_title = item_title,
                item_promoted = item_promoted,
                item_ean = ean,
                item_price = item_price,
                seller_id = seller_id,
                seller_name = seller_name,
                seller_url = seller_url,
                seller_feedback = seller_feedback,
                seller_supperSeller = seller_supperSeller,
                item_best_price_guarantee = item_best_price_guarantee,
                item_rating = item_rating,
                item_rating_count = item_rating_count,
                item_isSmart = item_isSmart,
                item_offers_count = item_offers_count,
                item_units_sold = item_units_sold,
                item_sales_value = item_sales_value,
                item_url = item_url,
                )




            except Exception as e:
                print(f"Error processing item {i}: {e}")

            result.save()



def engine(keyword, pages):
    keyword = keyword
    pages = pages
    proxies = {
        'http': 'http://192.168.100.79:3128',
        'https': 'http://192.168.100.79:3128',
        'ftp': 'http://192.168.100.79:3128',
    }
    headers = {
        "Accept": "*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pl-PL,pl;q=0.9",
        "Sec-Fetch-Site": "http://allegro.pl",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "X-Amzn-Trace-Id": "Root=1-648b70ff-5ba599d2048fa2f3782a3d4d",
    }
    current_timestamp_ms = int(time.time() * 1000)

    timestamp = {
        "emissionTimestamp": current_timestamp_ms,
    }
    current_timestamp_ms = int(time.time() * 1000)
    cookie_str = f'_cmuid=16940c14-35a0-4a73-9669-6572793e1a03; __gfp_64b=Dz4VKy.VC81lf3vJK5YSMqSZJ7h7nlA_NZ3UC0g74Yn.q7|1697922123; _tt_enable_cookie=1; _ttp=MqD4fOEVx2KUrQXgCJ036lXcq_4; gdpr_permission_given=0; ws3=LFvDveTqPjc0L05XT3YXkeQi9sR1AK693; _ga=GA1.2.615150404.1689538717; _ga_G64531DSC4=GS1.1.1703615804.12.0.1703615804.60.0.0; QXLSESSID=5e7e94f7b17ac17a650fadc8d45dccd89bd23ffc030b7b//02; parcelsChecksum=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; _gcl_au=1.1.2121870168.1707047691; __gads=ID=b4a6872f7cf0c1b0:T=1702150697:RT=1707058714:S=ALNI_MaJbQN95JF6qoca9NrtiHKdDvZK7w; __gpi=UID=00000d11057c7d03:T=1702150697:RT=1707058715:S=ALNI_MbqSLV_g8UynFHu7mRL7aPuUENOwg; __eoi=ID=46af5c4b8a69fcf5:T=1706864915:RT=1707058715:S=AA-AfjYxPsrsUVpkFssB-Z3SS4m1; wdctx=v4.cvYVsw4ANywwFiEPdeqM6zEfkIZy0INVpRc-hs44KtZl6AsExTEV_QzGoxh3MKHNPp5zuMAQwCuAJR4WsN3cvlA1j3Z8vXmwQgWB4K7zI4lhyRDoijkchOSAnWlQo2z7zM1vLWXJhBMfP1yR5OgrS_AuS0HT0p3llNncejyv9o0MUlkj4m4Q1CacNnqqIkM-swJ_PPT1lcvPBy6sOsYoJe7PM0ziUAwDMChyyeSOrMfl-WGOXSOS4fIneN4; datadome=o3YeheMDwy13x8Zc_b7oxnsvRYia9aT4P2re4ndn3P9yofbsrk4voLZRsM00RFCF52WZ7azt2kjdrxVg2kNLo49UssgLvby2umKfdRppKw4Ys2FS71v6E_JPj6WtFcm9'
    cookie_str = f"; wdctx=v4.Rmm5-e5ZubyrvwgipjB6hpto2izKOJnw9ZLdYD3TXGtCWo5uKgdh_WAzQn9txCXVXbg_ESYc8h6VjDFYF7ecp42yneqX3APgUHZuBvR4VcKGCcHBI_T4n4txYfBhuCrXKiaINt_1tWWgIf6I89kyVVA3uospE6xuwj_CmA1U4QdQM0hXP9Zd8hJipO0zMRQcDW0J7RJI0CZmNJj-DESXyq3bPpRqSAJBqUtgGVu9U985RXPA9jpf_yXTeA; gdpr_permission_given=0; __gads=ID=eb6da4d027994280:T=1708427286:RT=1708427286:S=ALNI_MY1bNInqyrV-M8lwL1gyMAlDkMC0A; __gpi=UID=00000d5ddefcf664:T=1708427286:RT=1708427286:S=ALNI_Mais4dDyb87M-ETSOzcteqGynU4gg; __eoi=ID=45b1e375607ca9b8:T=1708427286:RT=1708427286:S=AA-AfjbRThKoP3ZXQxTrwsaXZaR8; datadome=DWE9F5RoZKKFHTWo_kxQOeZXMmVSEtqC6oK7lCQYRUtae0~yMG1VXuJfWgF1RR0kd7rrOyLjIcCw4EQbDE4hv0TJ4vvfPgVlfSWo6AbNb8n1GHeiV~lKm3Ry_4NdihTD"
    cookies = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookie_str.split("; ")}
    conditions = search_conditions()
    products_on_pages = list()
    for i in range(1, pages+1):
            url = get_url(conditions, keyword, i)
            page_content = get_page(url, headers, proxies, cookies,)
            json_content = get_json(page_content)

            products_on_pages.append(json_content)
            print(len(products_on_pages))
            time.sleep(2.64)

    update_database = write_to_db(products_on_pages, url)
    #make_file = write_to_csv(json_content, url)



if __name__ == "__main__":
    main()
