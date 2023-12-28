import asyncio
import aiohttp

from bs4 import BeautifulSoup
from amazon_paapi import AmazonApi

from helper import product_common_url, get_random_headers

selectors = {
    "amazon": {
        "title1": '#productTitle',
        "title2": '#prologueProductTitle',
        "price1": 'span.a-price.a-text-price.a-size-medium.apexPriceToPay > span:nth-child(2)',
        "price2": 'span.a-price.aok-align-center.priceToPay > span.a-offscreen',
        "price2_2": 'span.a-price.aok-align-center.priceToPay > span > span.a-price-whole',
        "price3": '#corePrice_feature_div .a-price.aok-align-center .a-offscreen',
        "price4": '#newAccordionRow_0 .mobb-header-css .a-color-price',  # Without Exchange
        "bookprices": ['#price', '#kindle-price', '#adbl_bb_price'],
        "image1": '#landingImage',
        "image2": '#imgTagWrapperId img',
        "image3": '#imgBlkFront',  # Image 3 for book doubt # #img-canvas
        "availability": '#availability span',
        "mrp1": "#corePriceDisplay_desktop_feature_div .a-spacing-small .a-offscreen",
        "mrp2": "#corePrice_desktop .a-color-secondary .a-offscreen",
    }
}


async def get_html(url, count=1):

    try:
        async with aiohttp.ClientSession(headers=get_random_headers()) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html_doc = await response.text()
                    print(response.status,
                          "automated access to Amazon data" in html_doc)
                    if "automated access to Amazon data" in html_doc and count < 3:
                        res = await get_html(url, count + 1)
                        return res
                    return html_doc

    except Exception as e:
        print(e)


def extract_text(soup, selector):
    try:
        return soup.select_one(selector).get_text().strip()
    except AttributeError as e:
        print("Extract Error", selector, e)


def extract_tag(soup, selector):
    try:
        return soup.select_one(selector)
    except AttributeError as e:
        print(e)


async def get_amazon_details(url):
    # headers =  get_headers2()

    common_url = product_common_url(url, "amazon")
    html = await get_html(url)  # common_url vs url

    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    selector = selectors["amazon"]

    image = None

    img = extract_tag(soup, selector['image1'])

    if img:
        # print("Image 1: ", img)
        # image["data-a-dynamic-image"]
        image = img.get("data-old-hires") or img.get("src")

    else:
        img = extract_tag(soup, selector['image2'])
        if img:
            # print("Image 2: ", img)
            image = img.get('data-a-hires') or img.get("src")

    title = extract_text(soup, selector['title1']) or extract_text(
        soup, selector['title2'])

    price = extract_text(soup, selector['price1']) or extract_text(
        soup, selector['price2'])

    price = price or extract_text(soup, selector['price2_2'])

    if not price:
        for priceSelector in selector['bookprices']:
            price = extract_text(soup, priceSelector)
            if price:
                break

    mrp = extract_text(soup, selector['mrp1']) or extract_text(
        soup, selector['mrp2'])

    availability = extract_text(soup, selector['availability'])

    if "in stock" in availability.lower():
        availability = "In Stock"
    else:
        availability = "Out of Stock"

    ratings = extract_text(soup, "#acrPopover .a-color-base")
    # ratings = extract_text(soup, "#averageCustomerReviews .a-icon-alt")
    ratings_count = extract_text(soup, "#acrCustomerReviewText")
    # ratings_count = int(re.sub("[^0-9^.]", "", ratings_count))

    categories = soup.select(
        "#wayfinding-breadcrumbs_feature_div .a-link-normal.a-color-tertiary")

    # print("Categories:", categories)

    tags = []

    for category in categories:
        tags.append(category.text.strip())

    category = tags[-1] if categories else None

    reviews_tag = extract_tag(soup, "#cr-pagination-footer-0 .a-text-bold")

    reviews_url = "https://www.amazon.in" + \
        reviews_tag['href'] if reviews_tag else None

    results = {
        "link": common_url, "title": title, "image": image, "merchant": "amazon",
        "price": price, "mrp": mrp, "ratings": ratings, "ratings_count": ratings_count,
        "availability": availability, "category": category,
        "categories": tags, "reviews_url": reviews_url
    }

    for key in results:
        print(key, ":", results[key])

    return results


async def get_amazon_details2(url):

    KEY = 'AKIAIOD76FJGCTSBILBQ'
    SECRET = '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'
    TAG = 'dgofferzone-21'
    COUNTRY = 'IN'

    amazon = AmazonApi(KEY, SECRET, TAG, COUNTRY)

    data = amazon.get_items(url)

    item = data[0]

    response_url = item.detail_page_url or url

    price = mrp = avail = ""

    # print(item)

    title = item.item_info.title.display_value

    offers = item.offers

    if offers:
        savings = offers.listings[0].price.savings
        # if savings:
        #     mrp2 = offers.listings[0].price.amount + savings.amount
        mrp = offers.listings[0].saving_basis.display_amount
        avail = offers.listings[0].availability.message
        price = offers.listings[0].price.display_amount

    image = item.images.primary.large.url

    price = price.split(".00")[0] if ".00" in price else price
    mrp = mrp.split(".00")[0] if ".00" in mrp else mrp

    results = {
        "link": response_url, "title": title, "image": image, "merchant": "amazon",
        "price": price, "mrp": mrp, "availability": avail,
        "ratings": "", "ratingsCount": "",
        "category": "",
        "categories": "", "reviewsUrl": ""
    }

    for key in results:
        print(key, results[key])

    customer_reviews = item.customer_reviews

    if customer_reviews:
        print(customer_reviews.count)
        print(customer_reviews.star_rating)

    # brand = item.item_info.by_line_info.brand.display_value
    # classification = item.item_info.classifications.binding.display_value
    # print(brand, classification)

    return results


def main():
    in_stock = "https://www.amazon.in/dp/B0819RF3F2?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"
    in_stock2 = "https://www.amazon.in/dp/B01M1EEPOB?ref_=cm_sw_r_apin_dp_BAQM4KM5D4R5YQ0WWXQB?th=1&psc=1"
    in_stock3 = "https://www.amazon.in/dp/B093SGQDSF?th=1&psc=1"

    out_of_stock = "https://www.amazon.in/dp/B08VHK2TMY?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"
    book = 'https://www.amazon.in/dp/1447288505/'

    url = "https://www.amazon.in/Echo-Dot-4th-Gen-Blue/dp/B084KSRFXJ/ref=sr_1_1?keywords=amazon+alexa&sr=8-1"

    # These 2 gives incorrect price and avail == "" from api !!

    url2 = "https://www.amazon.in/dp/B09XJ48QPR?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"
    url3 = "https://www.amazon.in/dp/B01DF8YVEY?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"

    for i in range(100):
        asyncio.run(get_amazon_details(in_stock))
        break


if __name__ == '__main__':
    main()
