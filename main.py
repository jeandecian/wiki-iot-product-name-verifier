from bs4 import BeautifulSoup
import requests

WIKI_IOT_BASE_URL = "https://fehmijaafar.net/wiki-iot/index.php"
APPROVED_REVS_TITLE = "Special:ApprovedRevs"


def get_page(url=""):
    return requests.get(WIKI_IOT_BASE_URL + url).text


def get_approved_products(limit=500, offset=0):
    page = get_page(
        f"?title={APPROVED_REVS_TITLE}&limit={limit}&offset={offset}&show=all"
    )

    soup = BeautifulSoup(page, "html.parser")
    products = []
    for tag in soup.find("ol", class_="special").find_all("li"):
        text = tag.text

        if "Template:" in text or "User:" in text:
            continue

        if text in ("Allowed Domains", "Calculator version", "Methodology"):
            continue

        text = text.split(" (revision")[0]
        products.append(text)

    if 'class="mw-nextlink"' in page:
        return products + get_approved_products(limit, offset + limit)

    return products


print(get_approved_products())
