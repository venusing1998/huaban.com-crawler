import json
import os
from hashlib import md5
from multiprocessing.dummy import Pool

import requests

# 参数
GROUP_START = 1
GROUP_END = 10
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")


def get_html(q, page):
    """获取网页源代码

    """
    url = "http://huaban.com/search/?q={}&page={}&per_page=20&wfl=1"
    new_url = url.format(q, page)
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Cookie": "sid=zSsA0U4c0AfF8KbWvv2GqXqWkhd.VuEkKwXpHOXMPFdYPlsLrbpjEHGoiY2perxLBTvQmsA; _f=iVBORw0KGgoAAAANSUhEUgAAADIAAAAUCAYAAADPym6aAAABJElEQVRYR%2B1VOxYCIQwMF7KzsvFGXmW9kY2VnQfxCvgCRmfzCD9lnz53myWQAJOZBEfeeyIi7xz%2FyEXzZRPFhYbPc3hHXO6I6TbFixmfEyByeQQSxu6BcAXSkIGMazMjuBcz8pQcq44o0Iuyyc1p38C62kNsOdeSZDOQlLRQ80uOMalDgWCGMfsW2B5%2FATMUyGh2uhgptV9Ly6l5nNOa1%2F6zmjTqkH2aGEk2jY72%2B5k%2BNd9lBfLMh8GIP11iK95vw8uv7RQr4oNxOfbQ%2F7g5Z4meveyt0uKDEIiMLRC4jrG1%2FjkwKxCRE2e5lF30leyXYvQ628MZKV3q64HUFvnPAMkVuSWlEouLSiuV6dp2WtPBrPZ7uO5I18tbXWvEC27t%2BTcv%2Bx0JuJAoUm2L%2FQAAAABJRU5ErkJggg%3D%3D%2CWin32.1920.1080.24; _uab_collina=153125604931874292427852; _ga=GA1.2.600245271.1531256050; UM_distinctid=16485f90feda6-045ed4a74f14aa-f373567-1fa400-16485f90fee6d7; __auc=e3b79cd016485f913afe4128210; __gads=ID=a8ef06316e773be0:T=1531256049:S=ALNI_Mb8_YS-7SIyTbj8Dlkr_oBc9jw-8Q; uid=23331150; __asc=174c0f91164875e8434fe7e29a6; CNZZDATA1256903590=1420470606-1531252207-%7C1531278738; _cnzz_CV1256903590=is-logon%7Clogged-in%7C1531279500465%26urlname%7Cjfnztqdkst%7C1531279500465",
        "Host": "huaban.com",
        "Referer": "http://huaban.com/search/?q=%E6%B3%B0%E5%A6%8D",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "X-Request": "JSON",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        response = requests.get(new_url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.ConnectionError as e:
        print(e)
        return None


def get_images(json):
    """获取image的url

    """

    pins = json.get("pins")
    if pins:
        for item in pins:
            file = item.get("file")
            if file:
                contents = {}
                contents["key"] = file.get("key")
                yield contents


def write_into_file(keyword, item):
    """写入文件

    """
    if not os.path.exists(os.path.join(DIST_DIR, keyword)):
        os.makedirs(os.path.join(DIST_DIR, keyword))
    try:
        image_url = item.get("key")
        new_image_url = "http://img.hb.aicdn.com/" + image_url
        response = requests.get(new_image_url)
        if response.status_code == 200:
            file_path = "{0}/{1}/{2}.{3}".format(DIST_DIR, keyword,
                                                 md5(response.content).hexdigest(), "jpg")
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                print("Already Downloaded", md5(
                    response.content).hexdigest(), "jpg", sep="")
    except requests.ConnectionError:
        print("Failed to save image")


def main(page):
    """主函数

    """
    # 这里修改keyword
    q = "泰妍"
    json = get_html(q, page)
    for item in get_images(json):
        print("正在下载: http://img.hb.aicdn.com/", item["key"], sep="")
        write_into_file(q, item)


if __name__ == '__main__':
    pool = Pool(16)
    groups = ([x * 20 for x in range(GROUP_START-1, GROUP_END+1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
