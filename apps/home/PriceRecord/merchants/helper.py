import re
import secrets
import locale

from urllib.parse import urlparse
from urllib.parse import parse_qs
import os
module_dir = os.path.dirname(__file__)

def random_values(d_lists):
    idx = secrets.randbelow(len(d_lists))
    return d_lists[idx]


def get_user_agents():
    file_path = os.path.join(module_dir, 'user_agents_2.txt')
    
    with open(file_path) as f:
        agents = f.read().split("\n")
        return random_values(agents)


def get_random_headers():
    headers = {"Authority": "www.amazon.in",
               "Method": "GET",
               "Scheme": "https",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept-Language": "en-US,en;q=0.8",
               "Cache-Control": "max-age=0",
               "Referer": "https://www.amazon.in/",
               "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
               "Sec-Ch-Ua-Mobile": "?0",
               "Sec-Ch-Ua-Platform": "Windows",
               "Sec-Fetch-Dest": "document",
               "Sec-Fetch-Mode": "navigate",
               "Sec-Fetch-Site": "same-origin",
               "Sec-Fetch-User": "?1",
               "Sec-Gpc": "1",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": get_user_agents(),
               }

    return headers


def to_inr_currency2(number):
    # Set the locale to en_IN (English, India)
    locale.setlocale(locale.LC_NUMERIC, 'en_IN')

    # Convert the number to the Indian currency format
    formatted_number = locale.format_string("%.2f", number, grouping=True)

    # Return the formatted number
    return formatted_number

def to_inr_currency(number):
    # Set the locale to en_IN (English, India)
    locale.setlocale(locale.LC_MONETARY, 'en_IN')

    # Convert the number to the Indian currency format
    formatted_number = locale.currency(number, grouping=True)

    # Return the formatted number
    return formatted_number


def product_common_url(url, merchant):
    common_url = url
    parsed_url = urlparse(url)
    # print(parsed_url)

    match merchant:
        case "amazon":
            try:
                asin = re.findall(
                    "(B[0-9]{1}[0-9A-Z]{8}|[0-9]{9}(?:X|[0-9]))", url)[0]

                hostname = parsed_url.netloc
                ext = hostname.split("amazon.")[1]

                common_url = f"https://www.amazon.{ext}/dp/{asin}?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"

            except:
                # common_url = url
                pass

        case "flipkart":

            try:
                pid = parse_qs(parsed_url.query)['pid'][0]
                common_url = "https://www.flipkart.com/product/p/itme?pid=" + pid
            except:
                common_url = url.split("?")[0] if '/p/itm' in url else url

    return common_url


selectors = {
    "amazon": {
        "title1": '#productTitle',
        "title2": '#prologueProductTitle',
        "price1": 'span.a-price.a-text-price.a-size-medium.apexPriceToPay > span:nth-child(2)',
        "price2": 'span.a-price.aok-align-center.priceToPay > span.a-offscreen',
        "bookprices": ['#price', '#kindle-price', '#adbl_bb_price'],
        "image1": '#landingImage',
        "image2": '#imgTagWrapperId img',
        "image3": '#imgBlkFront',  # Image 3 for book doubt # #img-canvas
        "availability": '#availability span',
        "mrp1": "#corePriceDisplay_desktop_feature_div .a-spacing-small .a-offscreen",
        "mrp2": "#corePrice_desktop .a-color-secondary .a-offscreen",
    },
    "flipkart": {
        "title": '.B_NuCI',
        "price": '._30jeq3._16Jk6d',
        "image1": '#container > div > div._2c7YLP.UtUXW0._6t1WkM._3HqJxg > div._1YokD2._2GoDe3 > div._1YokD2._3Mn1Gg.col-5-12._78xt5Y > div:nth-child(1) > div > div._3li7GG > div._1BweB8 > div._3kidJX > div.CXW8mj._3nMexc > img',
        "image2": '._396QI4',
        "availability": '._16FRp0',
        "availability2": '._3utEwz span',
        "availability3": '._2JC05C',
        "availability4": '._1dVbu9',
        "mrp": '._2p6lqe',
    },
    "snapdeal": {
        "title1": '#productOverview > div.col-xs-14.right-card-zoom.reset-padding > div > div.pdp-fash-topcenter-inner.layout > div.row > div.col-xs-18 > h1',
        "title2": '.pdp-e-i-head',
        "price1": '#buyPriceBox > div.row.reset-margin > div.col-xs-14.reset-padding.padL8 > div.disp-table > div.pdp-e-i-PAY-r.disp-table-cell.lfloat > span.pdp-final-price > span',
        "price2": '.pdp-final-price',
        "image1": '.cloudzoom',  # .active img
        "image2": '#bx-slider-left-image-panel > li:nth-child(1) > img',
        "availability": '.soldleftImg.btn span',
        "mrp": '.pdpCutPrice',
    }
}

def main():
    print(to_inr_currency(1200000))
    print(to_inr_currency2(1200000))

if __name__ == '__main__':
    main()

