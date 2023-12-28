import pymongo
import asyncio
from .config import DB_URL

from .utils import get_current_date, get_datetime


async def connect_db():
    try:
        my_client = pymongo.MongoClient(DB_URL)
        db = my_client["WebAppTest"]
        print("DB Connection Successful!")
        return db

    except Exception as e:
        print("DB Failed to Connect", e)


async def manage_users(data, action):
    db = await connect_db()

    try:
        users = db["users"]
        if action == "create":
            # new_values = {"$set": {"earnkarolink": earnkaro_link}}
            result = users.update_one({"user_email": data["user_email"]}, {
                                      "$set": {"user_email": data['user_email']},
                                      "$addToSet": {"products": {"product_id": data['product_id'],
                                                                 "is_tracking": data['is_tracking'],
                                                                 "is_favourite": data['is_favourite'],
                                                                 "date": data['date']}}},
                                      upsert=True)
            return True
        
        elif action == "read":
            result = list(users.find(data))
            return result

        elif action == "update":
            # new_values = {"$set": {"earnkarolink": earnkaro_link}}
            result = users.update_one({"user_email": data["user_email"], "products.product_id": data['product_id']},
                                       {
                                      "$set": {"user_email": data['user_email'],
                                               "products.$": {"product_id": data['product_id'],
                                                              "is_tracking": data['is_tracking'],
                                                              "is_favourite": data['is_favourite'],
                                                              "date": data['date']}}},
                                      upsert=True)
            return True

        elif action == "delete":

            result = users.update_one({"user_email": data['user_email']},
                                      {"$pull": {"products": data['products']}})
            print(result.matched_count)
            return True

    except Exception as e:
        print(e)


async def manage_products(data, action):
    db = await connect_db()

    try:
        products = db["products"]

        if action == "read":
            result = list(products.find(data))
            # print("Result: ", result)
            return result

        elif action == "update":

            # newvalues = {"$set": {"earnkarolink": earnkaro_link}}
            # newvalues = {"$push": {"pricehistory": {"Date": date, "Price": ""}}}

            price = data["price"]  # change_if_dollor()

            new_values = {
                "link": data["link"], "title": data["title"],
                "image": data["image"], "merchant": data["merchant"],
                "price_details": {
                    "mrp": data["mrp"],
                    "current_price": price,
                    "previous_price": data["previous_price"],
                    "c_availability": data['availability'],
                    "p_availability": data['p_availability'],
                },
                "more_details": {
                    "categories": data["categories"],
                    "category": data["category"],
                    "ratings": data["ratings"],
                    "ratings_count": data["ratings_count"],
                    "reviews_url": data.get('reviews_url')
                },
                "last_updated": get_datetime()
            }

            result = products.update_one({"link": data["link"]},
                                         {"$set": new_values,
                                          "$addToSet": {"price_history": {"date": get_current_date(), "price": price}},
                                          },
                                         upsert=True)

            return True

        elif action == "delete":
            try:
                print(data)
                result = products.update_one({"users": data}, {"$pull": {"users": data}}, )
                # print(result.matched_count)
                # print(result.raw_result)
                # print(result.modified_count)
                # print(result.acknowledged)
                print(result.matched_count)
                return True if result.matched_count > 0 else None

            except pymongo.errors.PyMongoError as e:
                return False

    except Exception as e:
        print(e)

# asyncio.run(products("update", {"id": "1", "merchant":"amazon"}))
# asyncio.run(products("update", {"id": "1", "merchant":"flipkart"}))


def main():
    asyncio.run(manage_users(
        {"user_email": "giri@gmail.com", "product_id": 1234}, "update"))
    # asyncio.run(manage_users(
    # {"user_email": "giri@gmail.com", "products": {"date":{'$regex':"^2023-07-29"}, "product_id": 1234}}, "delete"))


if __name__ == '__main__':
    main()
