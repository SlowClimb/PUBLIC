from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_driver_path = '/Users/a1234/Downloads/chromedriver-mac-arm64/chromedriver'

# 设定Bilibili登录网址
login_url = "https://passport.bilibili.com/login"
# 设定视频的评论API模板
comments_api_url = "https://api.bilibili.com/x/v2/reply?pn={page}&type=1&oid={aid}"
get_aid_url = 'https://api.bilibili.com/x/web-interface/view?bvid={video_id}'

# 模拟登录并获取cookie
def login_and_get_cookies():
    # 手动指定 ChromeDriver 的路径
    # 手动指定 chromedriver 的路径
    service = Service('/Users/a1234/Downloads/chromedriver-mac-arm64/chromedriver')

    # driver = webdriver.Chrome(executable_path='/Users/a1234/Downloads/chromedriver-mac-arm64/chromedriver')
    # 创建 Chrome 实例
    driver = webdriver.Chrome(service=service)

    # 手动指定 ChromeDriver 的路径
    driver.get(login_url)
    
    # 等待用户登录完成，检查某个登录后特定的元素是否出现，例如用户头像
    try:
        # 在这里等待 B站页面上显示用户头像，代表登录成功
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header-avatar-wrap"))  # 用户头像的class
        )
        print("检测到用户已登录")

        # 获取登录后的 cookies
        cookies = driver.get_cookies()
        # driver.quit()
        # print(cookies)

        # 可以将 cookies 转换为字典
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        return cookie_dict

    except Exception as e:
        print("登录检测失败或超时：", str(e))
    driver.quit()
    
    return None


# 自动生成请求的 headers
def generate_headers(cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
        'Referer': 'https://www.bilibili.com/',
    }

    return headers  

def get_aid(video_id, cookies):
    url = get_aid_url.format(video_id=video_id)
    print(f"get aid url: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"请求失败，状态码: {response.status_code}, 原因: {response.text}")

    # 解析评论数据
    if data['data']['aid']:
        return data['data']['aid']
    else:
        return None

# 获取视频的评论信息
def get_comments(video_id, cookies):
    page = 1
    user_ids = []
    # print(f"get_comments cookes: {cookies}")
    aid = get_aid(video_id, cookies)
    # print(f"get_comments aid: {aid}")
    while True:
        url = comments_api_url.format(page=page, aid=aid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
        }
        response = requests.get(url, cookies=cookies, headers=headers)
        data = response.json()

        # 解析评论数据
        if data['data']['replies']:
            for reply in data['data']['replies']:
                user_id = reply['mid']  # 获取用户的UID
                user_ids.append(user_id)
            page += 1
        else:
            break

    return user_ids

# 批量将用户加入黑名单
def add_to_blacklist(user_ids, cookies):
    blacklist_url = "https://api.bilibili.com/x/relation/modify"
    join_black_count = 0
    for user_id in user_ids:
        data = {
            "fid": user_id,
            "act": 6,  # 5代表加入黑名单
            "re_src": 11,
            "csrf": cookies['bili_jct']
        }
        # 生成 headers
        headers = generate_headers(cookies)

        response = requests.post(blacklist_url, data=data, cookies=cookies, headers=headers)

        if response.json()['code'] == 0:
            print(f"成功将用户 {user_id} 加入黑名单")
            join_black_count += 1
        else:
            print(f"将用户 {user_id} 加入黑名单失败：", response.json()['message'])
    print(f"total {join_black_count} user to blacklist!")

# 主函数
def main():
    video_id = "BV1nF4m1L75f"
    # 1. 登录并获取cookies
    cookies = login_and_get_cookies()
    # print(f"get cookies: {cookies}")

    # 2. 获取视频评论中的用户UID
    user_ids = get_comments(video_id, cookies)

    # 3. 将用户批量加入黑名单
    add_to_blacklist(user_ids, cookies)

if __name__ == "__main__":
    main()
