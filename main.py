from bs4 import BeautifulSoup
import pandas as pd
import requests

WIKI_IOT_BASE_URL = "https://fehmijaafar.net/wiki-iot/index.php"
APPROVED_REVS_TITLE = "Special:ApprovedRevs"
README_MD_PATH = "README.md"
MD_TABLE_TAG_START = "<!-- TABLE_START -->"
MD_TABLE_TAG_END = "<!-- TABLE_END -->"


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


def get_unapproved_products(limit=500, offset=0, show="unapproved"):
    return get_products(limit, offset, show)


def get_modified_products(limit=500, offset=0, show=""):
    return get_products(limit, offset, show)


def sort_products(products):
    return sorted(products, key=lambda x: x.lower())


def update_readme_table(dataframes):
    table_md = (
        "| CSV File | Number of Products |\n"
        "|-----------|--------------------|\n"
        + "\n".join(f"| {name} | {len(df)} |" for name, df in dataframes.items())
    )

    with open(README_MD_PATH, "r") as f:
        readme_md = f.read()

    readme_md = (
        readme_md.split(MD_TABLE_TAG_START)[0]
        + MD_TABLE_TAG_START
        + "\n"
        + table_md
        + "\n"
        + MD_TABLE_TAG_END
        + readme_md.split(MD_TABLE_TAG_END)[1]
    )

    with open(README_MD_PATH, "w") as f:
        f.write(readme_md)


approved_products = get_approved_products()

verified_df = pd.read_csv("verified.csv").sort_values(by="Product")
verified_df.to_csv("verified.csv", index=False)
verified_products = set(verified_df["Product"].str.strip())
verified_products = sort_products(
    [name for name in verified_products if name in approved_products]
)

verified_df = pd.DataFrame(verified_products, columns=["Product"])
verified_df.to_csv("verified.csv", index=False)

unverified_products = sort_products(
    [name for name in approved_products if name not in verified_products]
)

unverified_df = pd.DataFrame(unverified_products, columns=["Product"])
unverified_df.to_csv("unverified.csv", index=False)

unapproved_products = sort_products(get_unapproved_products())
unapproved_df = pd.DataFrame(unapproved_products, columns=["Product"])
unapproved_df.to_csv("unapproved.csv", index=False)

combined_df = pd.DataFrame(
    sort_products(approved_products + unapproved_products), columns=["Product"]
)
combined_df.to_csv("combined.csv", index=False)

normalized = combined_df["Product"].str.lower().str.strip()
duplicated_mask = normalized.duplicated(keep=False)
duplicated_df = combined_df[duplicated_mask]
duplicated_df.to_csv("duplicated.csv", index=False)

modified_products = [name.split(" (diff")[0] for name in get_modified_products()]
modified_products = sort_products(
    [name for name in modified_products if name in verified_products]
)
modified_df = pd.DataFrame(modified_products, columns=["Product"])
modified_df.to_csv("modified.csv", index=False)

dataframes = {
    "combined.csv": combined_df,
    "verified.csv": verified_df,
    "unapproved.csv": unapproved_df,
    "unverified.csv": unverified_df,
    "modified.csv": modified_df,
    "duplicated.csv": duplicated_df,
}
update_readme_table(dataframes)
