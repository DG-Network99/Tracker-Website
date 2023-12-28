import math
import time

from bs4 import BeautifulSoup
import asyncio
import json
from amazon import get_html
from helper import to_inr_currency


async def get_myntra_details(url):
    try:

        html_doc = await get_html(url)
        soup = BeautifulSoup(html_doc, 'lxml')

        for s in soup.find_all("script"):
            if 'pdpData' in s.text:
                script = s.get_text(strip=True)
                # print(script)
                json_dict = json.loads(script[script.index('{'):])
                details = json_dict["pdpData"]

                title = details["name"]
                price = details["price"]["discounted"]
                mrp = details["price"]["mrp"]

                price = to_inr_currency(
                    price) if not math.isnan(price) else price

                mrp = to_inr_currency(mrp) if not math.isnan(mrp) else mrp

                if details['flags']['outOfStock']:
                    availability = "Out of Stock"
                else:
                    availability = "In Stock"

                product_url = "https://www.myntra.com/" + \
                    details["landingPageUrl"]  # response.url

                # print(details["ratings"])

                if "averageRating" in details["ratings"]:
                    ratings = round(details["ratings"]["averageRating"], 1)
                    ratings_count = details["ratings"]["totalCount"]
                else:
                    ratings = ratings_count = 0

                image = details["media"]["albums"][0]["images"][0]["imageURL"]

                # image2 = details["media"]["albums"][0]["images"][1]["imageURL"]
                # product_id = details['id']

                analytics = details['analytics']
                category = analytics['articleType']
                categories = [analytics['masterCategory'],
                              analytics['subCategory'], category]

                result = {
                    "link": product_url, "title": title, "image": image, "merchant": "myntra",
                    "price": price, "mrp": mrp, "ratings": ratings, "ratings_count": ratings_count,
                    "availability": availability, "category": category, "categories": categories,
                    "reviews_url": None,
                }

                for key in result:
                    print(key, ":", result[key])

                return result

    except Exception as e:
        print(e)


async def main():
    url3 = "https://www.myntra.com/activity-toys-and-games/imagimake/imagimake-kids-multi-colored-do-it-yourself-kit-activity-toys-and-games/20003670/buy"
    url2 = 'https://www.myntra.com/mattress-protector/la-verne/la-verne-grey-king-size-cotton-terry-waterproof-mattress-protector/14997940/buy'
    url = "https://www.myntra.com/tshirts/roadster/roadster-men-navy-blue-typography-printed-cotton-t-shirt/9329623/buy"
    # asyncio.run(get_myntra_details(url))
    # asyncio.run(get_myntra_details(url2))
    # asyncio.run(get_myntra_details(url3))
    begin = time.time()
    result = None
    for i in range(1, 3):
        print(i)
        result = asyncio.create_task(get_myntra_details(url))
        # await result
        print(i)

    await result

    end = time.time()
    print(f"Total runtime of the program is {end - begin}")

if __name__ == '__main__':
    asyncio.run(main())
