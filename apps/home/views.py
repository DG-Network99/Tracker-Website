from django import template
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.template import loader
from django.urls import reverse
from .PriceRecord.process_url import process_url
import asyncio
import requests
import json
from urllib.parse import quote
from .mongo_db import get_products, get_product_info, get_all_notifications


# @login_required(login_url="/login/")
def index(request):

    if request.method == "POST" and request.POST['input_value'] is not None:
        if request.POST['input_value'] == '':
            print("got null value")
            response = JsonResponse({"error": "there was an error"})
            response.status_code = 404
            return response
            # response_data = {'error': "there was an error"}
            # return HttpResponseBadRequest(content=json.dumps(response_data), content_type='application/json')
        
        print("post value is ",request.POST['input_value'])
        product_url = request.POST.get('input_value', False)
        print("###### Search #####")
        print(product_url)
        print("###### Search #####")
     
        encoded_url = quote(product_url, safe='')

        print(encoded_url)

        get_result = requests.get(
            f"http://89.116.230.121:3007/getProductOf?url={encoded_url}")

        print(get_result)
        print(get_result.status_code)
        print(get_result.text)
        print(get_result.json())
        data = get_result.json()
        
        print("#########  Printing Data ##########")
        print(data)
        print("###### Data End #####")

        context = {'segment': 'index', 'data': data}

        html_template = loader.get_template('home/index.html')
        # return HttpResponse(html_template.render(context, request))
        # return JsonResponse(context)
        html_template = loader.get_template('home/data.html')
        return HttpResponse(html_template.render(context, request))
    
    else:
        context = {'segment': 'index'}
        print("empty search or error")

        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))

def products(request):
    return HttpResponse("Products Page")

def notifications(request,id):
    return HttpResponse("notification page {}".format(id))

@login_required(login_url="login")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        print("##################")
        print(load_template)

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        if load_template == 'products':

            print(request.user.email)
            data = get_products(request.user.email)
            # print(data)
            context = {'segment': load_template, 'data': data}
            page = 'home/' + load_template+".html"
            return render(request, page, {"data":data})
        
        if load_template == 'product':
            if request.GET['pid']:
                product_id = request.GET.get('pid', None)
                notification_id = request.GET.get('nid', None)
                if notification_id is not None:
                    data = get_product_info(request.user.email, product_id, notification_id)
                else:
                    data = get_product_info(request.user.email, request.GET['pid'])
                print(data)
                return render(request, 'home/product.html', {"product":data})
            else:
                html_template = loader.get_template('home/page-404.html')
                return HttpResponse(html_template.render(context, request))

        if load_template == 'notifications':
            try:
                data = get_all_notifications(request.user.email)
                print(data)

            except Exception as e:
                print(e)    
            return render(request, 'home/notifications.html', {"data":data[::-1]})
        
        if load_template == 'telegram':
            try:
                print("Telegram Page")

            except Exception as e:
                print(e)    
            return render(request, 'home/telegram.html')
        
        if load_template == 'track':
            return render(request, 'home/track.html')
               
        page = 'home/' + load_template+".html"
        return render(request, page, {"form": "hi"})

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
    


