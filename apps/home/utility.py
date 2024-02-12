import re
from urllib.parse import urlparse, parse_qs

def product_common_url(link):
    url, id, common_url = None, None, None

    if "m.snapdeal" in link:
        url = urlparse(link.replace("m.", ""))
    else:
        url = urlparse(link.replace("www.", ""))

    merchant = url.hostname.split(".")[0]

    if merchant == "amazon":
        id_match = re.match(
            r'https?://(www\.)?(.*)amazon\.([a-z\.]{2,6})(/d/(.*)|/(.*)/?(?:dp|o|gp|-)/)(aw/d/|product/)?(B[0-9]{1}[0-9A-Z]{8}|[0-9]{9}(?:X|[0-9]))',
            link, re.IGNORECASE
        )
        id = id_match.groups()[-1] if id_match else None

        hst = url.hostname.split("zon.")[1] if "zon." in url.hostname else ""
        common_url = f"https://www.amazon.{hst}/dp/{id}?tag=dgofferzone-21&linkCode=ogi&th=1&psc=1" if id else link

    elif merchant == "flipkart":
        id = parse_qs(url.query).get("pid")
        common_url = f"https://www.flipkart.com/product/p/itme?pid={id[0]}" if id else link.split('?')[0] if '/p/itm' in link else link

    elif merchant == "shopsy":
        id = parse_qs(url.query).get("pid")
        common_url = f"https://www.shopsy.in/product/p/itme?pid={id[0]}&affid=inf_df14122e-4049-4a14-a0e5-33b2911d8eb3" if id else f"{link}?&affid=inf_df14122e-4049-4a14-a0e5-33b2911d8eb3" if '/p/itm' in link else link

    elif merchant in ["myntra", "ajio", "snapdeal"]:
        common_url = link

    else:
        common_url = link

    return common_url


if __name__ == "__main__":
    result = product_common_url("https://www.amazon.in/realme-Feather-Segment-Charging-Slimmest/dp/B0C45N5VPT/ref=pd_day0fbt_d_sccl_1/260-7908400-8445964?pd_rd_w=7VOHq&content-id=amzn1.sym.9fcd4617-323e-42b7-9728-3395e1b2fea0&pf_rd_p=9fcd4617-323e-42b7-9728-3395e1b2fea0&pf_rd_r=S6PRGCEJZ6Y8RNZHC5EZ&pd_rd_wg=zXUcp&pd_rd_r=1f2ab992-1ff6-4a9a-85db-f38eb5837fe1&pd_rd_i=B0C45N5VPT&th=1")    

    print(result)