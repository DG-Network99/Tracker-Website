import time

from bs4 import BeautifulSoup
import requests
import asyncio
import json

from helper import product_common_url
from amazon import extract_text, extract_tag, get_html

selectors = {
    "flipkart": {
        "title": '.B_NuCI',
        "price": '._30jeq3._16Jk6d',
        "image1": '#container > div > div._2c7YLP.UtUXW0._6t1WkM._3HqJxg > div._1YokD2._2GoDe3 > div._1YokD2._3Mn1Gg.col-5-12._78xt5Y > div:nth-child(1) > div > div._3li7GG > div._1BweB8 > div._3kidJX > div.CXW8mj._3nMexc > img',
        "image2": '._396QI4',
        "availability1": '._16FRp0',
        "availability2": '._3utEwz span',
        "availability3": '._2JC05C',
        "availability4": '._1dVbu9',
        "mrp": '._2p6lqe',
    }
}


async def get_flipkart_details(url):
    try:

        common_url = product_common_url(url, "flipkart")
        html_doc = await get_html(url)
        soup = BeautifulSoup(html_doc, 'lxml')

        selector = selectors['flipkart']

        price = extract_text(soup, selector['price'])
        mrp = extract_text(soup, selector['mrp'])

        title = extract_text(soup, selector['title'])
        image = extract_tag(soup, selector['image1']) or extract_tag(
            soup, selector['image2'])  # ._3qGmMb

        if image:
            srcset = image.get('srcset')
            image = srcset.split(' ')[0].strip() if srcset else image['src']

        avail = extract_text(soup, selector['availability1']) or extract_text(
            soup, selector['availability2']) or extract_text(soup, selector['availability3'])

        ratings = extract_text(soup, "._3LWZlK")  # or "_2d4LTz"
        ratings_count = extract_text(soup, "._2_R_DZ")

        categories = soup.select("._2whKao")
        tags = []
        for category in categories:
            tags.append(category.text.strip())

        tags.pop()
        category = tags[-1]

        special_tag = extract_text(soup, "._220jKJ FEJ_PY")

        links = soup.find(
            'div', attrs={'class': 'col JOpGWq'}).findChildren('a')

        reviews_url = "https://www.flipkart.com" + links[-1]['href']

        result = {
            "link": common_url, "title": title, "image": image, "merchant": "flipkart",
            "price": price, "mrp": mrp, "ratings": ratings, "ratings_count": ratings_count,
            "availability": avail, "category": category, "categories": tags,
            "reviews_url": reviews_url, "special_tag": special_tag
        }

        for key in result:
            print(key, ":", result[key])
        return result

    except Exception as e:
        print(e)


async def main():
    url5 = "https://www.flipkart.com/realme-gt-neo-3t-dash-yellow-128-gb/p/itmd1b8c6a6c8604?pid=MOBGHBJGFNFHDQ8D&lid=LSTMOBGHBJGFNFHDQ8DKBQ6C5&marketplace=FLIPKART&store=tyy%2F4io&spotlightTagId=FkPickId_tyy%2F4io&srno=b_1_12&otracker=nmenu_sub_Electronics_0_Realme&fm=organic&iid=087dc19a-61d3-4b4f-9e5a-20ec27dcc778.MOBGHBJGFNFHDQ8D.SEARCH&ppt=browse&ppn=browse&ssid=xnxz8907rk0000001686458757838"
    url4 = "https://www.flipkart.com/sleepyhead-orthopedic-memory-6-inch-king-high-density-hd-foam-mattress/p/itm6562f5d7f9942?pid=BEMF3XZ4FMNFT2GR&lid=LSTBEMF3XZ4FMNFT2GRQFIKCX&marketplace=FLIPKART&fm=factBasedRecommendation%2FrecentlyViewed&iid=R%3Arv%3Bpt%3App%3Buid%3A6b8006d7-0812-11ee-b6cc-0bed15a93d4e%3B.BEMF3XZ4FMNFT2GR&ppt=pp&ppn=pp&ssid=fqli2n3o5c0000001686458257883&otracker=pp_reco_Recently%2BViewed_12_39.productCard.RECENTLY_VIEWED_Sleepyhead%2BOrthopedic%2BMemory%2B6%2Binch%2BKing%2BHigh%2BDensity%2B%2528HD%2529%2BFoam%2BMattress_BEMF3XZ4FMNFT2GR_factBasedRecommendation%2FrecentlyViewed_11&otracker1=pp_reco_PINNED_factBasedRecommendation%2FrecentlyViewed_Recently%2BViewed_DESKTOP_HORIZONTAL_productCard_cc_12_NA_view-all&cid=BEMF3XZ4FMNFT2GR"
    url3 = "https://www.flipkart.com/realme-motion-activated-light-night-lamp/p/itm55e26a67a2007?pid=TLPGYGNTYWDMKWUX&lid=LSTTLPGYGNTYWDMKWUXVB1HRG&marketplace=FLIPKART&fm=factBasedRecommendation%2FrecentlyViewed&iid=R%3Arv%3Bpt%3App%3Buid%3Aa4851ce1-0810-11ee-b4a4-7f21cf71b83e%3B.TLPGYGNTYWDMKWUX&ppt=pp&ppn=pp&ssid=ikw43xtkps0000001686457658813&otracker=pp_reco_Recently%2BViewed_4_39.productCard.RECENTLY_VIEWED_realme%2BMotion%2BActivated%2BLight%2BNight%2BLamp_TLPGYGNTYWDMKWUX_factBasedRecommendation%2FrecentlyViewed_3&otracker1=pp_reco_PINNED_factBasedRecommendation%2FrecentlyViewed_Recently%2BViewed_DESKTOP_HORIZONTAL_productCard_cc_4_NA_view-all&cid=TLPGYGNTYWDMKWUX"
    url2 = "https://www.flipkart.com/hp-15s-intel-core-i5-12th-gen-8-gb-512-gb-ssd-windows-11-home-15s-fq5111tu-thin-light-laptop/p/itmbecf654716fd5?pid=COMGG63HGDTFCCGW&lid=LSTCOMGG63HGDTFCCGWLETTA9&marketplace=FLIPKART&fm=factBasedRecommendation%2FrecentlyViewed&iid=R%3Arv%3Bpt%3App%3Buid%3Aa4851ce1-0810-11ee-b4a4-7f21cf71b83e%3B.COMGG63HGDTFCCGW&ppt=pp&ppn=pp&ssid=ikw43xtkps0000001686457658813&otracker=pp_reco_Recently%2BViewed_3_39.productCard.RECENTLY_VIEWED_HP%2B15s%2BIntel%2BCore%2Bi5%2B12th%2BGen%2B-%2B%25288%2BGB%252F512%2BGB%2BSSD%252FWindows%2B11%2BHome%2529%2B15s-fq5111TU%2BThin%2Band%2BLight%2BLaptop_COMGG63HGDTFCCGW_factBasedRecommendation%2FrecentlyViewed_2&otracker1=pp_reco_PINNED_factBasedRecommendation%2FrecentlyViewed_Recently%2BViewed_DESKTOP_HORIZONTAL_productCard_cc_3_NA_view-all&cid=COMGG63HGDTFCCGW"
    # asyncio.run(get_flipkart_details('https://www.flipkart.com/prestige-pkoss-electric-kettle/p/itmerhhdgxetkdys?pid=EKTERHHDFKZ55GHW&lid=LSTEKTERHHDFKZ55GHWZXEAHA&marketplace=FLIPKART&store=j9e%2Fm38%2Fxrv&srno=b_1_1&otracker=nmenu_sub_Appliances_0_Electric%20Kettle&fm=organic&iid=en_Ema3b5IbIYN3%2F5XsNZmlcneYKJHhAH4iz5VrC3GfdCqQeBoeLrricr%2BBPIMEDu6dbhAhc47HUhlqWUGQ0irWdg%3D%3D&ppt=clp&ppn=big-saving-days-june-23-sale-store&ssid=0ds57cpr4g0000001686384464826'))
    # asyncio.run(get_flipkart_details(url2))
    # asyncio.run(get_flipkart_details(url3))
    # asyncio.run(get_flipkart_details(url4))
    # asyncio.run(get_flipkart_details(url5))

    begin = time.time()
    result = None
    for i in range(1, 3):
        print(i)
        result = asyncio.create_task(get_flipkart_details(url4))
        # await result
        print(i)

    await result

    end = time.time()
    print(f"Total runtime of the program is {end - begin}")

    url6 = "https://www.flipkart.com/realme-buds-2-wired-headset/p/itm393326c26b6ad"
    # Out of Stock

    # asyncio.run(get_flipkart_details(url6))

if __name__ == '__main__':
    asyncio.run(main())
