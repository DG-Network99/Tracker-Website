import asyncio
import re
import os
import json
import pymongo
import requests
from urllib.parse import quote
import datetime
import uuid
from .utility import product_common_url

from dotenv import load_dotenv
load_dotenv()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

API_URL = os.environ['API_URL']

DB_NAME = os.environ['DB_NAME']

# Web Tracker
WebTracker = myclient[DB_NAME] # DB Name

user_col = WebTracker["users"]
prod_col = WebTracker["web_products"]
notify_col = WebTracker["notifications"]

def format_product_data(prod):

    price_history = []
    prices = []

    productId = prod.get("productId", None) 

    try:
        for x in prod['priceHistory']:
            if x['price'] != "":
                y={}
                # x['price'] = x['price'] if x['price'] != "" else previous_price

                price = re.sub("[^\d\.]", "", x['price'])
                y['x'] = x['date'] 
                y['y'] = price
                prices.append(int(float(price)))
                price_history.append(y)
                # previous_price = price

                del x['date']
                del x['price']
    except Exception as e:
        print(e)

    try:
        image_url = prod['image']
    except:
        image_url = None
    try:
        availability = prod['availability']
    except:
        availability = None
    try:
        last_updated = prod['lastUpdated']
    except:
        last_updated = None    

    try:
        highest_price = max(prices)
        highest_price = f"{highest_price:,}"
    except:
        highest_price = None

    try:
        lowest_price = min(prices)
        lowest_price = f"{lowest_price:,}"
    except:
        lowest_price = None 

    try:
        tracking_id = prod['users'][0]['tracking_id']
    except:
        tracking_id = None      

    price_history = price_history if len(price_history)!=0 else None 
    
    if prod['merchant']=="flipkart":
        try:
            # product_link = prod['shopsyLink']
            product_link = prod['earnkarolink']
        except:
            product_link = prod['link']
    else:
        product_link = prod['link']
    

    product = {'productId' : productId ,'link' : product_link, 'title' : prod['title'], 
        'price' : prod['price'], 'initPrice' : prod['initPrice'],
        'tracking_id' : tracking_id,
        'price_history' : price_history, 
        'highest_price' : highest_price, 'lowest_price' : lowest_price, 
        'merchant' : prod.get('merchant', ""), 'image' : image_url, 'availability': availability,
        'last_updated' : last_updated
        }
    return product

def formatted_price_history(prod):

    price_history = []
    prices = []

    try:
        for x in prod['priceHistory']:
            if x['price'] != "":
                y={}
                # x['price'] = x['price'] if x['price'] != "" else previous_price

                price = re.sub("[^\d\.]", "", x['price'])
                y['x'] = x['date'] 
                y['y'] = price
                prices.append(int(float(price)))
                price_history.append(y)
                # previous_price = price

                del x['date']
                del x['price']

        try:
            highest_price = max(prices)
            highest_price = f"{highest_price:,}"
        except:
            highest_price = None

        try:
            lowest_price = min(prices)
            lowest_price = f"{lowest_price:,}"
        except:
            lowest_price = None
        
        prod['price_history'] = price_history
        prod['highest_price'] = highest_price
        prod['lowest_price'] = lowest_price

        return prod

    except Exception as e:
        print(e)

        return prod

async def manage_users(data, action):

    # https://stackoverflow.com/questions/10522347/how-do-you-update-objects-in-a-documents-array-nested-updating

    try:
        users = user_col

        # Called when user creates an account <-using
        if action == "create_user":
            result = users.update_one(
                {"user_email": data["user_email"]},
                {"$set": {"products": [], "gender": None, "phone": None}},
                upsert=True)
            return True
        
        elif action == "create_product":

            check_product = list(users.find({"user_email" : data["user_email"], 
                                             "products.product_link" : data["product_link"]}))
            
            if len(check_product)==0:

                current_date = datetime.datetime.now()

                indian_date_format = current_date.strftime('%d-%m-%Y')

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
                            "date": indian_date_format
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

        # read is used to get user info <-using
        elif action == "read":
            
            result = list(users.find(data))
            return result
        
        elif action =="projection_read":
            result = list(users.find(data['query'], projection = data.get('projection', {'_id':0})))
            return result

        elif action == "update_primaries":

            result = users.update_one(
                {
                    "user_email": data["user_email"]},
                {
                    "$set": data["data"]
                }, upsert=True)
            
            # print(f"result in mongodb.py -> modified Count:{result.modified_count}, upserted id: {result.upserted_id}, acknowlged :{result.acknowledged}, match_count: {result.matched_count}")

            if result.modified_count > 0 or result.upserted_id is not None:
                return True
            else:
                return False

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
            if result.modified_count > 0:
                return True
            else:
                return False

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
                            "product_id": data["product_id"],
                            "product_link": data["product_link"],
                            "previous_price": data["previous_price"],
                            "current_price": data["current_price"],
                            "availability": data["availability"],
                            "is_read": data["is_read"],
                            "change": data["change"],
                            "percentage": data["percentage"],
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

def add_web_product(product_url, user_email):

    payload = {'url':product_url, 'user_email' : user_email}

    post_product_request = requests.post(f"{API_URL}/addWebProduct", json=payload)

    result = post_product_request.json()

    return result

def track_product(user_email, product_url):

    try:

        product_url = product_common_url(product_url)
        
        # is_product_available = user_col.find_one({"user_email": user_email,"products.product_link" : product_url}, 
        #                           projection={'_id': 0, 'products.$': 1})
        
        is_product_available = user_col.find_one(
            {
                'user_email': user_email,
                'products': {
                    '$elemMatch': {
                        'product_link': product_url
                    }
                }
            },
            {'products.$': 1}
        )

        if is_product_available:
            
            is_tracking = is_product_available['products'][0]['is_tracking'] 
            
            if is_tracking == True:
                return {'status':'failed', 'msg':'product already tracking'}
            
            result = add_web_product(product_url, user_email)

            if 'data' in result:

                product_data = result['data']

                fields_to_include = ['usersCount']

                # add only necessary fields from the product_data
                product_data_filtered = {key: value for key, value in product_data.items() if key in fields_to_include}
                
                update_productbase = prod_col.update_one(
                        {'link': product_url},
                        {'$set': {'usersCount': product_data_filtered['usersCount']}},
                        upsert=False
                    )
                
                update_user = user_col.update_one(
                    {'user_email': user_email, 'products.product_link': product_url},
                    {'$set': {'products.$.is_tracking': True}}
                )

                if update_user.modified_count > 0:
                    return {'status':'success', 'msg':'product added to tracking'}
                
                else:
                    return {'status':'error', 'msg':'Error adding product to track'}
                
            else:
                return {'status':'error', 'msg':'Error getting product from server'}
            
        try:

            result = add_web_product(product_url, user_email)

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
         
    except Exception as e:
        print(e)
        return {'status':'error', 'msg':'Error adding product'}   

def stop_tracking(user_email, product_url):

    try:

        product_url = product_common_url(product_url)

        result = user_col.update_one(
            {'user_email': user_email, 'products.product_link': product_url},
            {'$set': {'products.$.is_tracking': False}}
        )

        if result.modified_count > 0:
            print("update successfull")

            try:
                payload = {'url':product_url, 'user_email' : user_email}

                post_product_request = requests.post(f"{API_URL}/removeWebProduct", json=payload)

                result = post_product_request.json()

                if result['data']:

                    product_data = result['data']

                    fields_to_include = ['usersCount']

                    # Remove excluded fields from the product_data
                    product_data_filtered = {key: value for key, value in product_data.items() if key in fields_to_include}
                    
                    # print(product_data_filtered)

                    result = prod_col.update_one(
                        {'link': product_url},
                        {'$set': {'usersCount': product_data_filtered['usersCount']}},
                        upsert=False
                    )

                    if result.modified_count > 0:
                    
                        return True, {'status':'success', 'msg': 'update success in API and Local'}
                    
                    else:
                        return True, {'status':'error', 'msg': 'update success in API but not in Local'}
                
                else:
                    return False, {'status':'error', 'msg':'Error removing product from API'}

            except Exception as e:
                print(e)

                return False, {'status':'error', 'msg':'Error removing product from API'}

        else:
            return False, {'status':'error', 'msg': 'update not done'}

    except Exception as e:
        print(e)

        return False, {'status':'error', 'msg':'Error stop tracking'}  

def search_product(original_product_url):

    try:

        product_url = product_common_url(original_product_url)

        product_details = prod_col.find_one({"link": product_url})

        if product_details == None:

            try:
                encoded_url = quote(original_product_url, safe='')

                get_result = requests.get(f"{API_URL}/getProductOf?url={encoded_url}")

                data = get_result.json()

                if data.get("error"):

                    return {}, {'status':'error', 'msg': data.get("error")}

                if data:

                    formatted_data = formatted_price_history(data)

                    return formatted_data, {'status':'success', 'msg':'API product fetch success'}
                
                else:
                    return {}, {'status':'error', 'msg':'Data is Null or Error getting product from API'}

            except Exception as e:
                print(e)

                return {}, {'status':'error', 'msg':'Error getting product from API'}

        else:
            formatted_data = formatted_price_history(product_details)

            return formatted_data, {'status':'success', 'msg':'local product fetch success'}    

    except Exception as e:
        print(e)
        return {'status':'error', 'msg':'Error getting product from local'}   

def get_products(user_email):

    try:

        user_data = user_col.find_one({"user_email": user_email})

        if user_data:

            products = user_data.get('products', None)

            if products:

                products_urls = [product.get('product_link') for product in products if product['is_tracking']]

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

def get_product_info(user_email, product_id, notification_id=None):

    if notification_id:
        try: 
            
            query = {"user_email": user_email, "notifications.notification_id": notification_id}

            update_document = {"$set" : {"notifications.$.is_read": True}}

            notify_col.update_one(query, update_document)

        except Exception as e:
            print("Exception at notificartion in get_product_info: ", e)

    # check product is available to user and is tracking
    is_product_available = user_col.find_one(
            {'user_email': user_email},
             projection={'_id': 0, 'products': 1}
        )
    
    products_list = is_product_available.get('products', None)

    if products_list:
        found_product = next((product for product in products_list if product['product_id'] == product_id), None)

        if not found_product:
            return False

        if found_product and not found_product['is_tracking']:
            return False

    # get product from PRODUCT BASE using Product ID
    product_details = prod_col.find_one({"productId": product_id})

    if product_details:

        formatted_product_details = format_product_data(product_details)

        return formatted_product_details 
    
    else:
        return False
        
def get_all_notifications(user_email):
    notifications = notify_col.find_one({"user_email": user_email})
    all_records = []

    if notifications != None:
        for prod in notifications['notifications']:

            # getting product details
            # for product in prod_col.find():
            #     if str(product['link']) == str(prod['product_link']):      
            #         product_detail = {'url' : product['link'], 'title' : product['title'], 
            #             'price' : product['price'], 'initPrice' : product['initPrice'],
            #             'tracking_id' : product['users'][0]['tracking_id']
            #             }
            product_details = prod_col.find_one({'link': prod['product_link']}, projection={'_id': 0, 'priceHistory': 0, 'usersCount': 0})

            # product_info = {'product_id' : prod['product_id'], "notification_id" : prod['notification_id'],
            #         'product_detail' : product_details ,'change' : prod['change'], 
            #         'percentage' : prod['percentage'], 'previous_price' : prod['previous_price'],
            #         'current_price' : prod['current_price'], 'availability' : prod['availability'],
            #         'is_read' : prod['is_read']
            #         }

            product_info = prod
            product_info['product_detail'] = product_details
            all_records.append(product_info)
    return all_records

def get_user_details(user_email):
    user_data = asyncio.run(manage_users({'user_email': user_email}, 'read'))
    return user_data[0]

def update_user_details(user_email, data):
    user_data_response = asyncio.run(manage_users({'user_email': user_email, "data": data}, 'update_primaries'))
    return user_data_response

if __name__ == "__main__":
    # data = get_products("dina@gmail.com") 
    # print(data)

    # data = get_product_info("dina@gmail.com", "4ea35c26-1d26-4cdd-a221-d9f1ab79f17e", notification_id=None)
    # print(data)

    data, response = search_product("https://www.amazon.in/boAt-Airdopes-Atom-81-Wireless/dp/B0BKG5PQ6T")
    print(data)