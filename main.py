import requests

WIKI_IOT_BASE_URL = "https://fehmijaafar.net/wiki-iot/index.php"


def get_page(url=""):
    return requests.get(WIKI_IOT_BASE_URL + url).text


print(get_page())
