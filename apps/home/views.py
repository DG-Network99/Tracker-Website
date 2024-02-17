from django import template
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.urls import reverse
import asyncio
import requests
import json
from urllib.parse import quote
from .mongo_db import search_product, get_products, get_product_info, get_all_notifications, manage_users, manage_notifications, track_product, stop_tracking
from .mongo_db import get_user_details, update_user_details
from .utility import product_common_url
import datetime
import time
from bson import ObjectId
import csv

# @login_required(login_url="/login/")
@csrf_exempt
def index(request):

    if request.method == "POST" and request.POST['search'] is not None:

        if request.POST['search'] == '':
            print("got null value")
            response = JsonResponse({"error": "there was an error"})
            response.status_code = 404
            # return response
            context = {}
            html_template = loader.get_template('home/index.html')
            return HttpResponse(html_template.render(context, request))
        
            # response_data = {'error': "there was an error"}
            # return HttpResponseBadRequest(content=json.dumps(response_data), content_type='application/json')
        
        product_url = request.POST.get('search', None)

        print("SEARCHED URL :",product_url)

        data, response = search_product(product_url)
        
        print ("RESPONSE :",response)
        
        formatted_data = {}
        
        if data:
            print({"msg": "Product Fetched","URL":data["link"],"Product ID":data["productId"]})
            
            # remove mongodb object id to avoid any error
            del data['_id']

            price_history_json = json.dumps(data['price_history'])

        else:
            data={"msg" : "error"}
            price_history_json ={}

        context = {'segment': 'index', 'data': data, "price_history_json": price_history_json}

        request.session['context'] = context

        return HttpResponseRedirect(reverse('main_dashboard')) # Redirect to main_dashboard view to avoid form resubmission issue in frontend

        # html_template = loader.get_template('home/index.html')
        # return HttpResponse(html_template.render(context, request))
        # return JsonResponse(context)

        # html_template = loader.get_template('home/index.html')
        # return HttpResponse(html_template.render(context, request))
    
    else:
        context = {'segment': 'index'}
        print("GET request for Home Page")

        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))

def main_dashboard(request):

    data = request.session.pop('context', None)
    
    html_template = loader.get_template('home/index.html')

    return HttpResponse(html_template.render(data, request))
    
@csrf_exempt
def notification_update(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode('utf-8'))
        print("Post data ", post_data)
        product_url = post_data.get('productUrl', None)
        if product_url:
            res = asyncio.run(manage_users({
                'query': {"products.product_link": product_url}, 
                'projection': {'_id': 0, "user_email":1, "products.$": 1}}, 
                'projection_read'))
            print("res is ", res)
            if res:
                for user in res:
                    try:
                        if user['products'][0]['is_tracking'] == True:
                            data = {
                                "user_email": user['user_email'],
                                "product_id": post_data["productId"],
                                "product_link": post_data["productUrl"],
                                "previous_price": post_data["previousPrice"],
                                "current_price": post_data["price"],
                                "availability": post_data["availability"],
                                "change": post_data["change"],
                                "percentage": post_data["percentage"],
                                "is_read": False,
                                # any add or remove in keys, please update manage_notifications's 'create' action also in the mongo_db.py file
                                }
                            result = asyncio.run(manage_notifications(data, "create")) # creating notification for each users
                    except:
                        print("Problem in getting user['products'][0]['is_tracking']. Check notification_update function")        

        return HttpResponse("Got the post request")
    else:
        return HttpResponse("Not a valid request")

def products(request):
    return HttpResponse("products page")

def notifications(request,id):
    return HttpResponse("notification page {}".format(id))

def track(request):

    context = {}

    if request.user.is_authenticated:

        if request.method == "POST":

            user_email = request.user.email

            product_url = request.POST.get('productUrl',None)

            if product_url == None:

                response = JsonResponse({"Error": "request forbidden"})
                response.status_code = 403
                return response

            print("Product URL is ", product_url)

            track_product_response = track_product(user_email, product_url)

            print(track_product_response)

            if track_product_response['status'] == "success":
                alert = {"message":"success"}

            elif track_product_response['status'] == "failed":
                alert = {"message":"failed"}

            else:
                alert = {"message":"error"}    
            
            context = {'alert': alert}
            
            print(context)
            
            html_template = loader.get_template('home/data.html')
            
            return HttpResponse(html_template.render(context, request))
        
        else:
            html_template = loader.get_template('home/page-500.html')
            return HttpResponse(html_template.render(context, request))

    else:
        response = JsonResponse({"error": "need authentication"})
        response.status_code = 403
        return response

def stop_track(request):

    context = {}

    if request.user.is_authenticated:
        if request.method == "POST":

            user_email = request.user.email

            product_url = request.POST['productUrl']

            print("Product URL is ", product_url)

            stop_track_response, response_data = stop_tracking(user_email, product_url)

            print(response_data)

            if stop_track_response:
                response = JsonResponse({"success": "untrack successfull"})
                response.status_code = 200
                return response
            else:
                response = JsonResponse({"error": "there was an error"})
                response.status_code = 404
                return response
        
        else:
            response = JsonResponse({"error": "there was an error"})
            response.status_code = 404
            return response

    else:
        response = JsonResponse({"error": "need authentication"})
        response.status_code = 403
        return response

@csrf_exempt
def contact_us(request):
    if request.method == 'POST':
        
        try:
            email = request.POST.get('email', '')
            subject = request.POST.get('subject', '')
            message = request.POST.get('message', '')

            # Write data to CSV file
            with open('contact_data.csv', 'a', newline='') as csvfile:
                fieldnames = ['Email', 'Subject', 'Message']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if csvfile.tell() == 0:
                    writer.writeheader()

                writer.writerow({'Email': email, 'Subject': subject, 'Message': message})
                messages.success(request, 'Message sent successfully.')

        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong')
        
        return redirect(request.path)    
    else:
        return render(request, 'legal_pages/contact_us.html')

def about_us(request):
    return render(request, 'legal_pages/about_us.html')

@login_required(login_url="login")
def pages(request):
    context = {}
    try:

        load_template = request.path.split('/')[-1]

        print("##################")
        print(load_template, " module")

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        
        context['segment'] = load_template

        if load_template == 'products':

            # print(request.user.email)

            response, data = get_products(request.user.email)

            if response or data==[]:

                context = {'segment': load_template, 'data': data}

                page = 'home/' + load_template+".html"

                html_template = loader.get_template('home/products.html')

                # return render(request, page, context)
                return HttpResponse(html_template.render(context, request))
            
            else:
                html_template = loader.get_template('home/page-500.html')

                return HttpResponse(html_template.render(context, request))
        
        if load_template == 'product':

            if request.GET['pid']:

                product_id = request.GET.get('pid', None)

                notification_id = request.GET.get('nid', None)

                if notification_id is not None:
                    data = get_product_info(request.user.email, product_id, notification_id)

                else:
                    data = get_product_info(request.user.email, request.GET['pid'])
                    
                if not data:
                    print("product not found")

                    html_template = loader.get_template('home/page-404.html')

                    return HttpResponse(html_template.render(context, request))
                
                price_history_json = json.dumps(data['price_history'])
                
                return render(request, 'home/product.html', {"product":data, "price_history_json": price_history_json})
            
            else:
                html_template = loader.get_template('home/page-404.html')
                return HttpResponse(html_template.render(context, request))

        if load_template == 'notifications':
            try:
                data = get_all_notifications(request.user.email)

            except Exception as e:
                print(e)    
            return render(request, 'home/notifications.html', {'segment': 'notifications', "data":data[::-1]})
        
        if load_template == 'telegram':
            try:
                print("Telegram Page")

            except Exception as e:
                print(e)    
            return render(request, 'home/telegram.html')
        
        # maybe not necessary # check once
        if load_template == 'stop_track':

            if request.method == "POST":

                user_email = request.user.email

                product_url = request.POST['productUrl']

                print("Product URL is ", product_url)

                stop_track_response, response_data = stop_track(user_email, product_url)

                if stop_track_response:
                    response = JsonResponse({"success": "untrack successfull"})
                    response.status_code = 200
                    return response
                else:
                    response = JsonResponse({"error": "there was an error"})
                    response.status_code = 404
                    return response
            
            elif request.method == "GET":
                html_template = loader.get_template('home/page-500.html')
                return HttpResponse(html_template.render(context, request))
            else:
                response = JsonResponse({"error": "there was an error"})
                response.status_code = 404
                return response

        if load_template == 'profile':

            page = 'home/' + load_template+".html"
            user_email = request.user.email
            user_name = request.user.email.split('@')[0]

            def get_primary_data():
                user_data = get_user_details(user_email)
                user_phone = user_data.get("phone", None)
                user_gender = user_data.get("gender", None)
                user_primary_data = {'segment': 'profile', "user_name": user_name, "user_phone": user_phone ,"user_gender": user_gender}
                return user_primary_data

            if request.method == "POST":

                print(request.POST)

                if 'input-phone-number' in request.POST:
                    phone_number = request.POST.get('input-phone-number', None)
                    gender = request.POST.get('input-gender', None)
                    db_query = {"gender": gender.lower() if gender else gender, "phone": phone_number}
                    update_db_response = update_user_details(user_email, db_query)
                    if update_db_response:
                        messages.success(request, 'Your data has been updated successfully.')
                        # return redirect(request.path)
                        # return render(request, page, {**get_primary_data(), 'success_msg': 'Profile updated successfully'})
                    else:
                        messages.error(request, 'No changes to update or Cannot update data.')

                elif 'old-password' in request.POST:
                    old_password = request.POST.get("old-password")
                    input_password1 = request.POST.get("input-password1")
                    input_password2 = request.POST.get("input-password2")

                    if old_password == None or input_password1 == None or input_password2 == None or input_password1 != input_password2:
                        messages.error(request, 'Something Went Wrong.')
                        return redirect(request.path)

                    user_auth = authenticate(username=user_email,password=old_password)

                    try:
                        if user_auth is not None:
                            request.user.set_password(input_password1)
                            request.user.save()
                            messages.success(request, 'Password changed successfully.')
                        else:
                            messages.error(request, 'Incorrect Old Password.')
                    except:
                        messages.error(request, 'Something Went Wrong.')
                
                return redirect(request.path)
            
            elif request.method == "GET":

                return render(request, page, get_primary_data())
            
            else:
                html_template = loader.get_template('home/page-404.html')
                return HttpResponse(html_template.render(context, request))   
               
        page = 'home/' + load_template+".html"
        return render(request, page, {"form": "hi"})

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))