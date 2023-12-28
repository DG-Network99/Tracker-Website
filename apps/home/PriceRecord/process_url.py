import asyncio
import re
import math
import time

from .utils import is_url, id_generator, get_current_date, append_json
from .merchants import get_product_details, product_common_url
from .db import manage_products, manage_users


def parse_number(price_string):
    try:
        return float(re.sub("[^0-9^.]", "", price_string))
    except:
        return price_string


async def compare_prices(product, details, update=True):
    try:
        diff = "No Change"

        price_details = product["price_details"]
        p_price = parse_number(price_details['current_price'])
        c_price = parse_number(details['price'])

        p_availability = price_details['c_availability']
        c_availability = details['availability']

        print("Previous Price:", p_price)
        print("Current Price:", c_price)

        if (p_availability == "Out of Stock" and c_availability != "Out of Stock") or (
                p_availability != "Out of Stock" and c_availability == "Out of Stock"):
            diff = "Change in Availability"

        elif not math.isnan(c_price) and not math.isnan(p_price) and p_price != c_price:

            diff = round(((p_price - c_price) / p_price) * 100, 2)

        else:
            return {"ok": True, "is_change": False, "diff": diff}

        if update:
            new_values = {
                # "link2": product['link2'],
                "link": product['link'], "title": details['title'],
                "merchant": product['merchant'], "price": details['price'], "previous_price": price_details['current_price'],
                "p_availability": p_availability, "availability": c_availability,
                'mrp': details['mrp'] or price_details['mrp'],
                'image': details['image'] or product['image'],
                'category': details['category'] or product['more_details']['category'],
                'categories': details['categories'] or product['more_details']['categories'],
                'ratings': details['ratings'] or product['more_details']['ratings'],
                'ratings_count': details['ratings_count'] or product['more_details']['ratings_count'],
                'reviews_url': details['reviews_url'] or product.get('reviews_url')
            }

            await manage_products(new_values, "update")

        return {"ok": True, "is_change": True, "diff": diff}

    except Exception as e:
        print(e)
        return {"ok": False}


async def update_product(product):

    # link2
    details = await get_product_details(product['link'], product['merchant'])

    print("Product Details:", details)

    if not details:
        return False, "Error In Getting Details"

    compare_result = await compare_prices(product, details)


async def switch_tracking(product_id, user_details):

    users = await manage_users({"user_email": user_details['user_email'], "products.product_id": product_id}, "read")

    if len(users) > 0:
        user = users[0]
        products = user['products']
        for product in products:
            if product['product_id'] == product_id:
                is_tracking = not product['is_tracking']
                is_favourite = product['is_favourite']
                details = {
                    "user_email": user_details['user_email'],
                    "name": user_details['name'],
                    "product_id": product_id,
                    "is_tracking": is_tracking,
                    "is_favourite": is_favourite,
                    "date": product['date']
                }
                await manage_users(details, "update")
                break
    else:
        is_tracking = True
        is_favourite = False
    

        details = {
        "user_email": user_details['user_email'],
        "name": user_details['name'],
        "product_id": product_id,
        "is_tracking": is_tracking,
        "is_favourite": is_favourite,
        "date": get_current_date()
    }

        await manage_users(details, "create")


async def switch_favourite(product_id, user_details):
    users = await manage_users({"user_email": user_details['user_email'], "products.product_id": product_id}, "read")

    if len(users) > 0:
        user = users[0]
        products = user['products']
        for product in products:
            if product['product_id'] == product_id:
                is_tracking = product['is_tracking']
                is_favourite = not product['is_favourite']
                details = {
                    "user_email": user_details['user_email'],
                    "name": user_details['name'],
                    "product_id": product_id,
                    "is_tracking": is_tracking,
                    "is_favourite": is_favourite,
                    "date": product['date']
                }
                await manage_users(details, "update")
                break
    else:
        details = {
            "user_email": user_details['user_email'],
            "name": user_details['name'],
            "product_id": product_id,
            "is_tracking": False,
            "is_favourite": True,
            "date": get_current_date()
        }

        await manage_users(details, "create")


async def process_url(msg, user_data={}):
    try:
        print("Initial Link:", msg)

        extracted_url = "http" + \
            msg.split("http")[1].split(" ")[0].replace("dl.", "www.")
        print("extractedUrl:", extracted_url)
        # To implement later because problem in scraping amazon
        # productUrl = await unshort(extractedUrl);

        product_url = extracted_url
        print("Unshorted Link:", product_url)

        if not is_url(product_url):
            return False, "Url is invalid"

        if "m.snapdeal" in product_url:  # for snapdeal
            merchant = product_url.replace(
                "m.", "").split("//")[1].split(".")[0]
        else:
            merchant = product_url.replace(
                "www.", "").split("//")[1].split(".")[0]

        print("Merchant:", merchant)

        merchant = "amazon" if merchant == "amzn" else merchant

        supported_merchants = ['amazon', 'flipkart', 'myntra', 'snapdeal']

        is_match = True if any(
            mer == merchant for mer in supported_merchants) else False

        if not is_match:
            return False, "Merchant is not supported"

        products = await manage_products({"link": product_common_url(product_url, merchant)}, "read")

        if not products:
            # product_list = [doc for doc in products]
            products = []

        if len(products) > 0:
            product = products[0]
            print("Existing Product:", product)
            asyncio.create_task(update_product(product))
            await update_product(product)
            price_details = product["price_details"]

            product_details = {
                "link": product['link'], "title": product['title'],
                "merchant": product['merchant'], 'mrp': price_details['mrp'],
                "price": price_details['current_price'], "p_price": price_details['previous_price'],
                "p_availability": price_details['p_availability'], "availability": price_details['c_availability'],
                'image': product['image'],
                'category': product['more_details']['category'], 'categories': product['more_details']['categories'],
                'ratings': product['more_details']['ratings'], 'ratings_count': product['more_details']['ratings_count']
            }
            append_json("test.json", product_details)

            return True, product_details
            # details = product # doubt

        else:
            details = await get_product_details(product_url, merchant)

            print("Product Details:", details)

            if not details:
                return False, "Error In Getting Details"

            more_details = {
                "previous_price": details['price'], "p_availability": details['availability']}
            details.update(more_details)

            await manage_products(details, "update")

            print(details)

            append_json("test.json", details)

            return True, details

    except Exception as e:
        print(e)
        return False, None


def main():
    begin = time.time()
    # asyncio.run(process_url("https://www.flipkart.com/s/ev4b3DNNNN"))
    in_stock = "https://www.amazon.in/dp/B0819RF3F2?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"

    asyncio.run(process_url(in_stock))

    end = time.time()
    print(f"Total runtime of the program is {end - begin}")


async def test_db():
    await switch_tracking("1234", {"user_email": "giri1@gmail.com", "name": "Giri"})
    await switch_tracking("1235", {"user_email": "giri@gmail.com", "name": "Giri"})

    await switch_favourite("1235", {"user_email": "dina@gmail.com", "name": "Dina"})
    await switch_favourite("1236", {"user_email": "dina@gmail.com", "name": "Dina"})


if __name__ == '__main__':
    main()
    # asyncio.run(test_db())
