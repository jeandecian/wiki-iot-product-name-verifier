from bs4 import BeautifulSoup
import pandas as pd
import requests

WIKI_IOT_BASE_URL = "https://fehmijaafar.net/wiki-iot/index.php"
APPROVED_REVS_TITLE = "Special:ApprovedRevs"


def get_page(url=""):
    return requests.get(WIKI_IOT_BASE_URL + url).text


def get_products(limit=500, offset=0, show="all"):
    page = get_page(
        f"?title={APPROVED_REVS_TITLE}&limit={limit}&offset={offset}&show={show}"
    )

    soup = BeautifulSoup(page, "html.parser")
    products = []
    for tag in soup.find("ol", class_="special").find_all("li"):
        text = tag.text
        text = text.split(" (revision")[0]

        if "Template:" in text or "User:" in text:
            continue

        if text in (
            "Allowed Domains",
            "Calculator version",
            "Grade Calculator",
            "Main Page",
            "Methodology",
        ):
            continue

        products.append(text)

    if 'class="mw-nextlink"' in page:
        return products + get_approved_products(limit, offset + limit, show)

    return products


def get_approved_products(limit=500, offset=0, show="all"):
    return get_products(limit, offset, show)


approved_products = get_approved_products()

verified_df = pd.read_csv("verified.csv").sort_values(by="Product")
verified_df.to_csv("verified.csv", index=False)
verified_products = set(verified_df["Product"].str.strip())
verified_products = sorted(
    [name for name in verified_products if name in approved_products]
)

verified_df = pd.DataFrame(verified_products, columns=["Product"])
verified_df.to_csv("verified.csv", index=False)

unverified_products = sorted(
    [name for name in approved_products if name not in verified_products],
    key=lambda x: x.lower(),
)

unverified_df = pd.DataFrame(unverified_products, columns=["Product"])
unverified_df.to_csv("unverified.csv", index=False)
