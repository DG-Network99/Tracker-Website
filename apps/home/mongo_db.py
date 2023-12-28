import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["products_db"]

prod_col = mydb["web_products"]
notify_col = mydb["notifications"]


def get_products(user_email):

    all_records = []
    products = prod_col.find({"users.userEmail": user_email})

    for prod in products:
        product = {'product_id': prod['_id'], 'url' : prod['link'], 
                   'title' : prod['title'], 
                   'price' : prod['price'], 'initPrice' : prod['initPrice'],
                   'tracking_id' : prod['users'][0]['tracking_id']
                   }
        all_records.append(product)

    return all_records   


def get_product_info(user_email, product_id, notification_id=None):

    # notifications_user = notify_col.find_one({"user_email": user_email})
    # notifications = notifications['notification']
    if notification_id:
        query = {"user_email": user_email, "notification.notification_id": notification_id}
        update_document = {"$set" : {"notification.$.is_read": "True"}}
        notify_col.update_one(query, update_document)


    # for prod in notifications:
    #     if str(prod['product_id']) == str(product_id):
    #         notifications.update_one({"user_email": user_email},{"$set":{"is_read" : "True"}})

    for prod in prod_col.find():       
        if str(prod['_id']) == str(product_id):      
            product = {'url' : prod['link'], 'title' : prod['title'], 
                'price' : prod['price'], 'initPrice' : prod['initPrice'],
                'tracking_id' : prod['users'][0]['tracking_id']
                }
            return product
 

def get_all_notifications(user_email):
    notifications = notify_col.find_one({"user_email": user_email})
    all_records = []
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
    data = get_products() 
    print(data)