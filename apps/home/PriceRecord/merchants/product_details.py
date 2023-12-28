from amazon import get_amazon_details
from flipkart import get_flipkart_details
from myntra import get_myntra_details


async def get_product_details(product_url, merchant):

    print("Getting Product Details...")
    product_details = None

    match merchant:

        case "amazon":
            product_details = await get_amazon_details(product_url)

        case "flipkart":
            product_details = await get_flipkart_details(product_url)

        case "myntra":
            product_details = await get_myntra_details(product_url)

        # case "snapdeal":
        #     product_details = await get_snapdeal_details(product_url)

    return product_details
