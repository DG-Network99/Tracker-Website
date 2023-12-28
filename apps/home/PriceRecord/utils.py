import json
import os
import secrets

import requests
import asyncio
import random
import string

import time
from datetime import date, datetime
from pytz import timezone
from dateutil import relativedelta
from urllib.parse import urlparse
from urllib.parse import parse_qs

import validators
import re


def random_values(d_lists):
    idx = secrets.randbelow(len(d_lists))
    return d_lists[idx]


def get_user_agents():
    with open('user-agents2.txt') as f:
        agents = f.read().split("\n")
        return random_values(agents)


async def get_headers2():
    # headers = {
    #     'accept': '*/*',
    #     'User-Agent': get_user_agents(),
    #     'Accept-Language': 'en-US,en;q=0.9,it;q=0.8,es;q=0.7',
    #     'referer': 'https://www.google.com/',
    #     'cookie': 'DSID=AAO-7r4OSkS76zbHUkiOpnI0kk-X19BLDFF53G8gbnd21VZV2iehu-w_2v14cxvRvrkd_NjIdBWX7wUiQ66f-D8kOkTKD1BhLVlqrFAaqDP3LodRK2I0NfrObmhV9HsedGE7-mQeJpwJifSxdchqf524IMh9piBflGqP0Lg0_xjGmLKEQ0F4Na6THgC06VhtUG5infEdqMQ9otlJENe3PmOQTC_UeTH5DnENYwWC8KXs-M4fWmDADmG414V0_X0TfjrYu01nDH2Dcf3TIOFbRDb993g8nOCswLMi92LwjoqhYnFdf1jzgK0'
    # }

    headers2 = {
        "User-Agent": get_user_agents(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    headers3 = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'text/plain;charset=UTF-8',
        # 'Cookie': 'session-id=259-8391800-0886958; session-id-time=2082787201l; i18n-prefs=INR; ubid-acbin=259-3774151-5871941; session-token=ddb6uf0VV03BsD8fe7sRZkP65JeoGNZL5RB8DSjMFICKqh8ZMIDvZC8f5p6ThF1FQKR9Bx3UQOH6Mwn1SPnJEg7WC7ymXu5fFiBOtmfSOfkq86idynniExf5Ilv/vh7C3EtjMgLeLWtZoLX5fZbOALP0cfMUspFj0TakFp0c9iWIn/HF3fRbpcaESjVT1VLJPfY3i0TXDubZhHn9jJbVnz/fhzEglda94jpjEaa2pOs=',
        'Origin': 'https://www.amazon.in',
        'Referer': 'https://www.amazon.in/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Sec-GPC': '1',
        'User-Agent': get_user_agents(),
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    headers4 = {"Authority": "www.amazon.in",
                "Method": "GET",
                "Scheme": "https",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.amazon.in/",
                "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "Windows",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-Gpc": "1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": get_user_agents(),
                }

    return headers4


async def get_headers():
    headers = {
        'accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8,es;q=0.7',
        'referer': 'https://www.google.com/',
        'cookie': 'DSID=AAO-7r4OSkS76zbHUkiOpnI0kk-X19BLDFF53G8gbnd21VZV2iehu-w_2v14cxvRvrkd_NjIdBWX7wUiQ66f-D8kOkTKD1BhLVlqrFAaqDP3LodRK2I0NfrObmhV9HsedGE7-mQeJpwJifSxdchqf524IMh9piBflGqP0Lg0_xjGmLKEQ0F4Na6THgC06VhtUG5infEdqMQ9otlJENe3PmOQTC_UeTH5DnENYwWC8KXs-M4fWmDADmG414V0_X0TfjrYu01nDH2Dcf3TIOFbRDb993g8nOCswLMi92LwjoqhYnFdf1jzgK0'
    }

    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    return headers2


def append_file(filename, content):
    try:
        with open(filename, 'a', encoding="utf-8") as f:
            f.write(content + "\n")
        print(filename + ": " + "Content Added Successfully.")
    except IOError:
        print("Error: could not append to file " + filename)


def delete_file(filename):
    try:
        os.remove(filename)
        print("File " + filename + " deleted successfully.")
    except IOError:
        print("Error: could not delete file " + filename)


async def unshort(url):
    if is_url(url):
        response = requests.get(url, headers=await get_headers())
        return response.url


def get_datetime():
    # today = date.today()
    # current_date = today.strftime("%d/%m/%Y")

    date_time = datetime.now(
        timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    print("DateTime:", date_time)
    return date_time


def read_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(e)

def write_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
    except Exception as e:
        print(e)

def append_json(filename, data):
    try:
        file_data = read_json(filename)
        if not file_data: 
            file_data = []

        elif isinstance(file_data, dict):
            temp = file_data
            file_data = []
            file_data.append(temp)

        file_data.append(data)
        write_json(filename, file_data)

       
    except Exception as e:
        print(e)


def get_current_date():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return current_date


def get_date_diff(start_date, current_date):
    try:
        d1 = datetime.strptime(start_date, "%d/%m/%Y")
        d2 = datetime.strptime(current_date, "%d/%m/%Y")

        # Get the relativedelta between two dates
        delta = relativedelta.relativedelta(d2, d1)
        # print('Years, Months, Days between two dates is')
        # print(delta.years, 'Years,', delta.months, 'months,', delta.days, 'days')

        years = delta.years
        months = delta.months
        weeks = delta.weeks
        diff = None
        if years > 0:
            diff = f"{years} " + ("Years" if years > 1 else "Year")
        elif months > 0:
            diff = f"{months} " + ("Months" if months > 1 else "Month")
        elif weeks > 0:
            diff = f"{weeks} " + ("Weeks" if weeks > 1 else "Week")

        return diff

    except Exception as e:
        print(e)


def is_url(url):
    # Also checks it is publicly accessible
    validation = validators.url(url, public=True)

    # print("Validation:", validation)

    # using regular expression

    # pattern = "^https:\/\/[0-9A-z.]+.[0-9A-z.]+.[a-z]+$"
    # result = re.match(pattern, url)
    # print("Result: ", result)

    return validation


async def product_common_url(url, merchant):
    common_url = None
    parsed_url = urlparse(url)
    # print(parsed_url)

    if merchant == "amazon":
        try:
            asin = re.findall(
                "(B[0-9]{1}[0-9A-Z]{8}|[0-9]{9}(?:X|[0-9]))", url)[0]

            hostname = parsed_url.netloc
            ext = hostname.split("amazon.")[1]

            common_url = "https://www.amazon." + ext + "/dp/" + asin + \
                         "?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"
        except:
            common_url = url

    elif merchant == "flipkart":

        try:
            pid = parse_qs(parsed_url.query)['pid'][0]
            common_url = "https://www.flipkart.com/product/p/itme?pid=" + pid
        except:
            common_url = url.split("?")[0] if '/p/itm' in url else url

    return common_url


async def id_generator():
    id1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    id2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return id1 + id2


# result = asyncio.run(unshort("http://dl.flipkart.com/s/oUWWOpuuuN"))
# print(result)

url1 = "https://www.amazon.in/Redmi-Storage-Performance-Mediatek-Display/dp/B0BYN48MQW/ref=pd_day0fbt_sccl_1/260-9624651-5894348?pd_rd_w=2WfBL&content-id=amzn1.sym.9fcd4617-323e-42b7-9728-3395e1b2fea0&pf_rd_p=9fcd4617-323e-42b7-9728-3395e1b2fea0&pf_rd_r=RVFHA2XJ97RRKKNBDNQ7&pd_rd_wg=Ar5UH&pd_rd_r=9a31a763-4b1d-4aee-900d-8bd46bc1931c&pd_rd_i=B0BYN48MQW&psc=1"
url2 = "https://www.flipkart.com/samsung-galaxy-f23-5g-aqua-blue-128-gb/p/itm89d3030e3857e?pid=MOBGBKQFHKZHTHKJ&lid=LSTMOBGBKQFHKZHTHKJ7WW16A&marketplace=FLIPKART&store=tyy%2F4io&spotlightTagId=FkPickId_tyy%2F4io&srno=b_1_4&otracker=hp_omu_Top%2BOffers_1_4.dealCard.OMU_TOO4ENUDCC8Q_4&otracker1=hp_omu_PINNED_neo%2Fmerchandising_Top%2BOffers_NA_dealCard_cc_1_NA_view-all_4&fm=neo%2Fmerchandising&iid=90156599-c02b-4729-9d06-9a95b95458a1.MOBGBKQFHKZHTHKJ.SEARCH&ppt=browse&ppn=browse"
# test = asyncio.run(product_common_url(url2, "flipkart"))
# test = asyncio.run(id_generator())
# print(test)
