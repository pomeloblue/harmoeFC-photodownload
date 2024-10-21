import requests
from bs4 import BeautifulSoup
import os
import datetime
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import logging
import time

# 设置日志
logging.basicConfig(filename='download_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def select_download_path():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path


def login(username, password):
    try:
        session = requests.Session()
        login_url = "https://harmoe-fc.jp/slogin.php"

        logging.info(f"正在获取登录页面: {login_url}")
        response = session.get(login_url)
        logging.info(f"登录页面状态码: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"获取登录页面失败，状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        logging.info(f"登录页面标题: {soup.title.string if soup.title else 'No title'}")

        form_data = {}
        for input_field in soup.find_all('input'):
            if input_field.get('name'):
                form_data[input_field['name']] = input_field.get('value', '')

        form_data['user_id_or_email'] = username
        form_data['password'] = password

        logging.info("正在提交登录表单")

        response = session.post(login_url, data=form_data)
        logging.info(f"登录后页面状态码: {response.status_code}")

        if "ログアウト" in response.text or "マイページ" in response.text:
            logging.info("登录成功")
            return session
        else:
            logging.error("登录失败，请检查用户名和密码")
            return None
    except Exception as e:
        logging.error(f"登录过程中出错: {str(e)}")
        return None


def get_image_links(session, start_date, end_date):
    try:
        image_links = []
        page = 1
        while True:
            url = f"https://harmoe-fc.jp/photogallery/?page_no={page}"
            response = session.get(url)
            logging.info(f"正在处理图片库页面 {page}")

            soup = BeautifulSoup(response.text, 'html.parser')

            items = soup.find_all('li', class_='list__item')
            if not items:
                logging.info(f"在页面 {page} 上没有找到图片项，结束搜索")
                break

            for item in items:
                date_elem = item.find('div', class_='list__date')
                if not date_elem:
                    logging.warning(f"在页面 {page} 上的一个项目中没有找到日期")
                    continue

                date_str = date_elem.text.strip().replace('\n', '').replace(' ', '')
                try:
                    date = datetime.datetime.strptime(date_str, '%Y.%m.%d')
                except ValueError:
                    logging.warning(f"无法解析日期: {date_str}")
                    continue

                if start_date <= date <= end_date:
                    img_tag = item.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        img_src = img_tag['src']
                        if img_src.lower().endswith(('.jpg', '.jpeg', '.png')):
                            full_img_src = f"https:{img_src}" if img_src.startswith('//') else img_src
                            image_links.append(full_img_src)
                        else:
                            logging.warning(f"找到的图片链接不是jpg/jpeg/png格式: {img_src}")
                    else:
                        logging.warning(f"在页面 {page} 上的一个项目中没有找到图片链接")
                elif date < start_date:
                    logging.info(f"日期 {date} 早于开始日期 {start_date}，结束搜索")
                    return image_links

            logging.info(f"页面 {page} 处理完成，当前共找到 {len(image_links)} 张图片")
            page += 1
            time.sleep(1)  # 添加延迟以避免频繁请求

        return image_links
    except Exception as e:
        logging.error(f"获取图片链接失败: {str(e)}")
        return []


def download_image(session, url, path):
    try:
        response = session.get(url)
        filename = url.split('/')[-1]
        filepath = os.path.join(path, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logging.error(f"下载图片 {url} 失败: {str(e)}")
        return False


def get_valid_date(prompt):
    while True:
        date_str = simpledialog.askstring("输入", prompt)
        if date_str is None:
            return None
        try:
            return datetime.datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用YYYYMMDD格式（例：20240403）")


def main():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    username = simpledialog.askstring("登录", "请输入fc登录id:")
    if username is None:
        return

    password = simpledialog.askstring("输入", "请输入密码:", show='*')
    if password is None:
        return

    start_date = get_valid_date("请输入需要下载的开始日期(YYYYMMDD):")
    if start_date is None:
        return

    end_date = get_valid_date("请输入结束日期(YYYYMMDD):")
    if end_date is None:
        return

    download_path = select_download_path()
    if not download_path:
        messagebox.showwarning("警告", "未选择下载路径，程序退出。")
        return

    session = login(username, password)
    if not session:
        messagebox.showerror("错误", "登录失败，请检查用户名和密码。")
        return

    logging.info("正在获取图片链接...")
    image_links = get_image_links(session, start_date, end_date)
    if not image_links:
        messagebox.showinfo("信息", "未找到符合条件的图片。")
        return

    logging.info(f"找到 {len(image_links)} 张图片，开始下载...")

    successful_downloads = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(download_image, session, link, download_path): link for link in image_links}
        for future in concurrent.futures.as_completed(future_to_url):
            if future.result():
                successful_downloads += 1
                logging.info(f"已下载 {successful_downloads}/{len(image_links)}")

    logging.info(f"下载完成。成功下载 {successful_downloads} 张图片，位于 {download_path}")
    logging.info(f"总共尝试下载 {len(image_links)} 张图片。")
    if successful_downloads < len(image_links):
        logging.warning(f"有 {len(image_links) - successful_downloads} 张图片下载失败。详情请查看日志文件。")

    messagebox.showinfo("下载完成", f"成功下载 {successful_downloads} 张图片\n保存在文件夹: {download_path}")


if __name__ == "__main__":
    main()