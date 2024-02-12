import asyncio
import pymongo
import requests
from urllib.parse import quote
import datetime
import uuid
from .utility import product_common_url

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

# Main Tracker
# MainTracker = myclient["MainTracker"]  # DB Name
# master_products = MainTracker["tasks"]

# Web Tracker
WebTracker = myclient["products_db"] # DB Name

user_col = WebTracker["users"]
prod_col = WebTracker["web_products"]
notify_col = WebTracker["notifications"]

async def manage_users(data, action):

    # https://stackoverflow.com/questions/10522347/how-do-you-update-objects-in-a-documents-array-nested-updating

    try:
        users = user_col

        if action == "create_user":
            result = users.update_one(
                {"user_email": data["user_email"]},
                {"$set": {"products": []}},
                upsert=True)
            return True
        
        elif action == "create_product":
            check_product = list(users.find({"user_email" : data["user_email"], "products.product_link" : data["product_link"]}))
            if len(check_product)==0:
                result = users.update_one(
                {"user_email": data["user_email"]},
                {
                    "$set": {"user_email": data['user_email']},
                    "$addToSet":
                    {
                        "products": {
                            "product_link": data['product_link'],
                            "product_id": data['product_id'],
                            "is_tracking": True,
                            "is_favourite": False,
                            "date": "31-12-2023"
                        }
                    }},
                upsert=True)
            else:
                return False    
            return True

        elif action == "create":
            result = users.update_one(
                {"user_email": data["user_email"]},
                {
                    "$set": {"user_email": data['user_email']},
                    "$addToSet":
                    {
                        "products": {
                            "product_link": data['product_link'],
                            "is_tracking": data['is_tracking'],
                            "is_favourite": data['is_favourite'],
                            "date": data['date']
                        }
                    }},
                upsert=True)
            return True

        elif action == "read":
            
            result = list(users.find(data))
            return result

        elif action == "update":

            result = users.update_one(
                {
                    "user_email": data["user_email"],
                    "products.product_link": data['product_link']
                },
                {
                    "$set":
                    {
                        "user_email": data['user_email'],
                        "products.$":
                        {
                            "product_link": data['product_link'],
                            "is_tracking": data['is_tracking'],
                            "is_favourite": data['is_favourite'],
                            "date": data['date']
                        }
                    }
                }, upsert=True)

            return True

        elif action == "delete":

            result = users.update_one({"user_email": data['user_email']},
                                      {"$pull": {"products": data['products']}})

            print(result.matched_count)
            print(result.modified_count)

            return True

    except Exception as e:
        print(e)
        return False

async def manage_products(data, action):

    # https://stackoverflow.com/questions/10522347/how-do-you-update-objects-in-a-documents-array-nested-updating

    try:
        users = user_col

        if action == "create_user":
            result = users.update_one(
                {"user_email": data["user_email"]},
                {"$set": {"products": []}},
                upsert=True)
            return True
        
        elif action == "create_product":
            check_product = list(users.find({"user_email" : data["user_email"], "products.product_link" : data["product_link"]}))
            if len(check_product)==0:
                result = users.update_one(
                {"user_email": data["user_email"]},
                {
                    "$set": {"user_email": data['user_email']},
                    "$addToSet":
                    {
                        "products": {
                            "product_link": data['product_link'],
                            "product_id": data['product_link'],
                            "is_tracking": True,
                            "is_favourite": False,
                            "date": "31-12-2023"
                        }
                    }},
                upsert=True)
            else:
                return False    
            return True

        elif action == "create":
            result = users.update_one(
                {"user_email": data["user_email"]},
                {
                    "$set": {"user_email": data['user_email']},
                    "$addToSet":
                    {
                        "products": {
                            "product_link": data['product_link'],
                            "is_tracking": data['is_tracking'],
                            "is_favourite": data['is_favourite'],
                            "date": data['date']
                        }
                    }},
                upsert=True)
            return True

        elif action == "read":
            
            result = list(users.find(data))
            return result

        elif action == "update":

            result = users.update_one(
                {
                    "user_email": data["user_email"],
                    "products.product_link": data['product_link']
                },
                {
                    "$set":
                    {
                        "user_email": data['user_email'],
                        "products.$":
                        {
                            "product_link": data['product_link'],
                            "is_tracking": data['is_tracking'],
                            "is_favourite": data['is_favourite'],
                            "date": data['date']
                        }
                    }
                }, upsert=True)

            return True

        elif action == "delete":

            result = users.update_one({"user_email": data['user_email']},
                                      {"$pull": {"products": data['products']}})

            print(result.matched_count)
            print(result.modified_count)

            return True

    except Exception as e:
        print(e)
        return False

async def manage_notifications(data, action):

    try:
        notifications = notify_col

        if action == "read":
            result = list(notifications.find(data))
            # print("Result: ", result)
            return result

        elif action == "create":

            isoformat = datetime.datetime.now().isoformat()

            result = notifications.update_one(
                {"user_email": data["user_email"]},
                {
                    "$addToSet": {
                        "notifications":
                        {
                            "notification_id": str(uuid.uuid4()),
                            "product_link": data["product_link"],
                            "previous_price": data["previous_price"],
                            "current_price": data["current_price"],
                            "availability": data["availability"],
                            "is_read": data["is_read"],
                            "change": data["change"],
                            "current_date": isoformat
                        }
                    },

                }, upsert=True)

            return True

        elif action == "delete":
            try:

                pass
                # print(data)

                # result = notifications.update_one(
                #     {"users": data}, {"$pull": {"users": data}}, )
                # # print(result.matched_count)
                # # print(result.raw_result)
                # # print(result.modified_count)
                # # print(result.acknowledged)
                # print(result.matched_count)
                # return True if result.matched_count > 0 else None

            except pymongo.errors.PyMongoError as e:
                return False

    except Exception as e:
        print(e)

# Manage Single Products Collection
def manage_productbase(data, action):
    try:

        if action == "create_product":

            query = {'link': data['link']}

            update_operation = {'$set': data['product_data']}

            result = prod_col.update_one(query, update_operation, upsert=True)

            if result.modified_count > 0 or result.upserted_id is not None:
                return True
            else:
                return False
            
        if action == "read":
            query = {''}
            

    except Exception as e:

        print(e)   
        return False     

def track_product(user_email, product_url):

    try:

        API_URL = "http://89.116.230.121:3007"

        product_url = product_common_url(product_url)

        is_product_available = user_col.find_one({'user_email': user_email, 
                                                'products': {'$elemMatch': {'product_link': product_url}}},
                                                projection={'_id': 0, 'products': 1})

        if is_product_available == None:

            try:
                payload = {'url':product_url, 'user_email' : user_email}

                post_product_request = requests.post(f"{API_URL}/addWebProduct", json=payload)

                result = post_product_request.json()

                if result['data']:

                    product_data = result['data']

                    fields_to_exclude = ['_id', 'users']

                    # Remove excluded fields from the product_data
                    product_data_filtered = {key: value for key, value in product_data.items() if key not in fields_to_exclude}
                    
                    # print(product_data_filtered)

                    add_product_result = manage_productbase(
                        {'link': product_data_filtered['link'], 
                         'product_data' : product_data_filtered,
                         }, 'create_product')

                    if add_product_result:

                        # add products for tracking
                        asyncio.run(manage_users({"user_email": user_email, "product_link": product_url, 'product_id': product_data_filtered['productId']},"create_product"))
                        
                        return {'status':'success', 'msg':'product added'}
                    else:
                        return {'status':'error', 'msg':'Error adding product to product base'}
                
                else:
                    return {'status':'error', 'msg':'Error getting product from server'}

            except Exception as e:
                print(e)

                return {'status':'error', 'msg':'Error adding product'}

        else:
            return {'status':'failed', 'msg':'product already available'}    

    except Exception as e:
        print(e)
        return {'status':'error', 'msg':'Error adding product'}   

def get_products(user_email):

    # all_records = []
    # products = prod_col.find({"users.userEmail": user_email})

    # if products != None:
    #     for prod in products:
    #         product = {'product_id': prod['_id'], 'url' : prod['link'], 
    #                 'title' : prod['title'], 'price' : prod['price'], 'initPrice' : prod['initPrice'],
    #                 'merchant' : prod['merchant'],'image' : "https://m.media-amazon.com/images/W/MEDIAX_792452-T1/images/I/71ZOtNdaZCL._SX569_.jpg",
    #                 'tracking_id' : prod['users'][0]['tracking_id']
    #                 }
    #         all_records.append(product)

    # return all_records   

    try: 
        
        user_data = user_col.find_one({"user_email": user_email})

        if user_data:

            products = user_data.get('products', None)

            if products:

                products_urls = [product.get('product_link') for product in products]

                product_details = prod_col.find({"link": {"$in": products_urls}})

                products_details_list = list(product_details)

                return True, products_details_list
            else:
                print("no products")

                return False, []
        else:
            print("user not found") 

            return False, "User Not Found"
        
    except Exception as e:
        print(e)
        return False, "Error"


    # if products:
    #     product_urls = []
    #     for prod in products:
    #         product_url = prod['product_link']
    #         product_urls.append(product_url)
    
    #     payload = {"products": product_urls}
    #     print(payload)
    #     api_endpoint = "http://89.116.230.121:3007/getProducts"
    #     response = requests.get(api_endpoint, params=payload)
    #     print(response.status_code)
    #     response_json = response.json()
    #     product_details = response_json['details']

    #     # to convert _id to id
    #     updated_product_details = [{'id': item.pop('_id'),**item} for item in product_details]

    #     product_details = updated_product_details

    # print("All Products Details : ", product_details)
    # return product_details

def get_product_info(user_email, product_id, notification_id=None):

    product_details = []

    if notification_id:
        try: 
            query = {"user_email": user_email, "notification.notification_id": notification_id}
            update_document = {"$set" : {"notification.$.is_read": "True"}}
            notify_col.update_one(query, update_document)
        except Exception as e:
            print("Exception at notificartion in get_product_info: ", e)

    try:
        payload = {"product_ids": [product_id]}
        print(payload)
        api_endpoint = "http://89.116.230.121:3007/getProducts"
        response = requests.get(api_endpoint, params=payload)
        print(response.status_code)
        response_json = response.json()
        product_details = response_json['details']
    except Exception as e:
        print("Exception at get_product_info: ", e)

    return product_details

# def get_product_info(user_email, product_id, notification_id=None):

#     # notifications_user = notify_col.find_one({"user_email": user_email})
#     # notifications = notifications['notification']
#     if notification_id:
#         query = {"user_email": user_email, "notification.notification_id": notification_id}
#         update_document = {"$set" : {"notification.$.is_read": "True"}}
#         notify_col.update_one(query, update_document)


#     # for prod in notifications:
#     #     if str(prod['product_id']) == str(product_id):
#     #         notifications.update_one({"user_email": user_email},{"$set":{"is_read" : "True"}})
    
#     for prod in prod_col.find():       
#         if str(prod['_id']) == str(product_id):      
#             product = {'url' : prod['link'], 'title' : prod['title'], 
#                 'price' : prod['price'], 'initPrice' : prod['initPrice'],
#                 'tracking_id' : prod['users'][0]['tracking_id']
#                 }
#             return product
 

def get_all_notifications(user_email):
    notifications = notify_col.find_one({"user_email": user_email})
    all_records = []
    if notifications != None:
        for prod in notifications['notification']:

            # getting product details
            for product in prod_col.find():       
                if str(product['_id']) == str(prod['product_id']):      
                    product_detail = {'url' : product['link'], 'title' : product['title'], 
                        'price' : product['price'], 'initPrice' : product['initPrice'],
                        'tracking_id' : product['users'][0]['tracking_id']
                        }
                
            product_info = {'product_id' : prod['product_id'], "notification_id" : prod['notification_id'],
                        'product_detail' : product_detail ,'change' : prod['change'], 
                    'percentage' : prod['percentage'], 'previous_price' : prod['previous_price'],
                    'current_price' : prod['current_price'], 'availability' : prod['availability'],
                    'is_read' : prod['is_read']
                    }
            all_records.append(product_info)
    return all_records    


if __name__ == "__main__":
    # data = get_products("dina@gmail.com") 
    # print(data)

    product_data = {'link': 'https://www.amazon.in/dp/B08TV2P1N8?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1', 
                    'link2': 'https://www.amazon.in/boAt-Rockerz-255-Pro-Earphones/dp/B08TV2P1N8/ref=pd_bxgy_img_sccl_1/258-2127604-8056607?pd_rd_w=j5Mqm&content-id=amzn1.sym.2f895d58-7662-42b2-9a98-3a18d26bef33&pf_rd_p=2f895d58-7662-42b2-9a98-3a18d26bef33&pf_rd_r=1ZZ9DSQP6RG2DFFX2Y8F&pd_rd_wg=1Dhw2&pd_rd_r=281db0de-a04b-4ab2-88f6-3eec96c3888f&pd_rd_i=B08TV2P1N8&psc=1', 
                    'merchant': 'amazon', 
                    'initPrice': '₹999', 
                    'price': '₹1,099', 
                    'title': 'boAt Rockerz 255 Pro+ Bluetooth in Ear Neckband with Upto 60 Hours Playback, ASAP Charge, IPX7, Dual Pairing and Bluetooth v5.2(Active Black)',
                    'image': 'https://m.media-amazon.com/images/I/51aBTOiXRlL._SL1500_.jpg', 
                    'mrp': '₹3,990', 
                    'availability': 'In Stock', 
                    'lastUpdated': '2024-01-17 21:20:02', 
                    'rating': 4.1, 'ratingCount': 184163, 
                    'brand': 'boAt', 
                    'categories': ['Electronics', 'Headphones, Earbuds & Accessories', 'Headphones', 'In-Ear'], 
                    'productId': 'e7a3284d-5e2b-44cb-b5ae-0844bc6c10c7', 'usersCount': {'website': 7}
                    }

    fields_to_exclude = ['_id', 'users']

    # Remove excluded fields from the product_data
    product_data_filtered = {key: value for key, value in product_data.items() if key not in fields_to_exclude}
    
    print(product_data_filtered)

    add_product_result = manage_productbase(
        {'link': product_data_filtered['link'], 
            'product_data' : product_data_filtered,
            }, 'create')