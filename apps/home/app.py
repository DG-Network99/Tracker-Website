import requests

from urllib.parse import quote

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'


# product_url = "https://www.amazon.in/dp/B0BD8WVQ22?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1"

product_url = "https://www.amazon.in/dp/B0C2D1P8DD"
# product_url = "https://www.amazon.in/dp/B0BD8WVQ22"

def request_product():

    encoded_url = quote(product_url, safe='')

    print(encoded_url)

    get_result = requests.get(
        f"http://89.116.230.121:3007/getProductOf?url={ encoded_url}")

    print(get_result)
    print(get_result.status_code)
    print(get_result.text)
    print(get_result.json())


def update_product():

    myobj = {'url': product_url, "count": 1}

    post_request = requests.post(
        "http://localhost:3007/incrementProductCountof", json=myobj)

    print(post_request)
    print(post_request.status_code)
    print(post_request.text)
    print(post_request.json())


request_product()

# update_product()


@app.route("/price_change", methods=["POST"])
def price_change():
    try:

        data = request.json

        print(data)

        return jsonify({"message": f"Data Received Successfully"}), 201

    except Exception as e:
        print(e)


# main driver function
if __name__ == '__main__':
    # app.run()
    app.run(debug=True, port=8001)
