import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---

# 设置你的豆瓣用户ID
# 建议使用环境变量来管理敏感信息
# 你也可以直接在这里赋值, 例如: DOUBAN_ID = "your_douban_id"
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")

# 爬取页数范围 (每页15个)
# 例如 range(0, 15*10, 15) 会爬取前10页
PAGE_RANGE = range(0, 255, 15) 

# 输出文件名
OUTPUT_FILENAME = 'index.html'

# 请求头，模拟浏览器访问
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# 代理设置 (如果需要)
# 如果你不需要代理，请将 PROXIES 设置为 None
# PROXIES = {'http': 'http://127.0.0.1:7890', 'https:': 'http://127.0.0.1:7890'}
PROXIES = None

# --- HTML 模板 ---

# 这是新的 Apple 风格 HTML 文件的头部和主要结构
# 直接从你的新设计中复制而来
HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的电影照片墙</title>
    <!-- 引入 Tailwind CSS 以实现快速、现代化的样式 -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- 引入 Google Fonts 的 Inter 字体，这是 Apple 风格常用的字体 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* 自定义样式，补充 Tailwind CSS */
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        /* 为电影海报容器添加一个统一的宽高比，确保网格对齐 */
        .poster-aspect {
            aspect-ratio: 2 / 3;
        }
        /* 图像将覆盖整个容器，避免拉伸变形 */
        .poster-aspect img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
    </style>
</head>
<body class="bg-black text-gray-200">
    <!-- 页面容器 -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 头部标题 -->
        <header class="py-12 sm:py-16 lg:py-20 text-center">
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white">
                我的电影 Top 250
            </h1>
            <p class="mt-4 text-lg text-gray-400">一份精选的电影收藏集</p>
        </header>
        <!-- 电影海报网格 -->
        <main>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 gap-6 md:gap-8">
"""

# 这是新的 HTML 文件的页脚部分
HTML_FOOT = """
            </div>
        </main>
        <!-- 页脚 -->
        <footer class="text-center py-10 mt-12 sm:mt-16 border-t border-gray-800">
            <p class="text-sm text-gray-500">含哺而熙，鼓腹而游 © 2025</p>
        </footer>
    </div>
</body>
</html>
"""

# --- 固定的电影内容 ---
# 这部分内容会始终显示在页面顶部，并且不会被爬虫覆盖
FIXED_MOVIE_CONTENT_HTML = """
                <!-- 固定的电影: Дорогие товарищи! -->
                <div class="group">
                    <a title='Дорогие товарищи!' target="_blank" href='https://www.imdb.com/title/tt10796286'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-red-500/30">
                            <img src='https://m.media-amazon.com/images/M/MV5BZGZlNTAwNzgtODUwYy00YjZiLWJlMzctYjFjNDFmYjE3M2ZlXkEyXkFqcGc@._V1_QL75_UX322_.jpg' alt='Дорогие товарищи! 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
                <!-- 固定的电影: 1987 -->
                <div class="group">
                    <a title='1987' target="_blank" href='https://www.imdb.com/title/tt6493286'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-blue-500/30">
                            <img src='https://m.media-amazon.com/images/M/MV5BZjU2OTJkNWUtMTBhZi00NDJjLTgwMmYtOGQ3YmQ4ZjE3NWI1XkEyXkFqcGc@._V1_QL75_UX306_.jpg' alt='1987 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
                <!-- 固定的电影: 택시운전사 -->
                <div class="group">
                    <a title='택시운전사' target="_blank" href='https://www.imdb.com/title/tt6878038'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-green-500/30">
                           <img src='https://m.media-amazon.com/images/M/MV5BYWU2YzE1YWQtYTNhYi00YTk3LTgxZTMtODA3ZTJkZGU3MWVkXkEyXkFqcGc@._V1_QL75_UX306_.jpg' alt='택시운전사 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
                <!-- 固定的电影: 悲兮魔兽 -->
                <div class="group">
                    <a title='悲兮魔兽' target="_blank" href='https://www.imdb.com/title/tt4901304'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-yellow-500/30">
                            <img src='https://m.media-amazon.com/images/M/MV5BMTQ5MTk5NTgyMV5BMl5BanBnXkFtZTgwNDI0NTY4MDI@._V1_FMjpg_UX1200_.jpg' alt='悲兮魔兽 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
                <!-- 固定的电影: The Death of Stalin -->
                <div class="group">
                    <a title='The Death of Stalin' target="_blank" href='https://www.imdb.com/title/tt4686844/'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-purple-500/30">
                           <img src='https://m.media-amazon.com/images/M/MV5BMTcxMDc1NjcyNl5BMl5BanBnXkFtZTgwNDU0NDYxMzI@._V1_QL75_UX380_CR0,0,380,562_.jpg' alt='The Death of Stalin 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
"""

def fetch_movies():
    """
    爬取豆瓣电影数据并返回 HTML 内容块。
    """
    movie_items_html = ""
    total_movies = 0

    print(f"开始从豆瓣用户 '{DOUBAN_ID}' 的收藏页面爬取数据...")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        
        try:
            print(f"正在爬取页面: {page_url}")
            response = requests.get(page_url, headers={'User-Agent': USER_AGENT}, proxies=PROXIES, timeout=10)
            response.raise_for_status()  # 如果请求失败 (如 404, 500), 则会抛出异常
        except requests.exceptions.RequestException as e:
            print(f"!!! 无法访问页面 {page_url}。错误: {e}")
            continue

        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        movie_list = soup.findAll('div', class_="item")

        if not movie_list:
            print("在此页面未找到更多电影，可能已到达末页。")
            break

        for item in movie_list:
            try:
                # 提取电影信息
                item_link_tag = item.find("a")
                item_img_tag = item.find("img")

                item_url = item_link_tag['href']
                # 将豆瓣图片URL从小图替换为大图，获得更高清的画质
                img_url = item_img_tag['src'].replace('small', 'large')
                item_title = item_img_tag['alt']

                # 这是为每个电影生成的 HTML 代码块，完全匹配新的 Apple 风格设计
                item_html = f"""
                <!-- 电影: {item_title} -->
                <div class="group">
                    <a title='{item_title}' target="_blank" href='{item_url}'>
                        <div class="poster-aspect overflow-hidden rounded-xl shadow-lg transform transition-all duration-300 ease-in-out group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-blue-500/30">
                            <img src='{img_url}' alt='{item_title} 海报' referrerpolicy='no-referrer' />
                        </div>
                    </a>
                </div>
                """
                movie_items_html += item_html
                total_movies += 1
                print(f"  [+] 成功提取: {item_title}")

            except Exception as e:
                print(f"  [!] 解析某个项目时出错: {e}")
        
        # 礼貌性地暂停，避免给服务器造成过大压力
        pause_time = random.uniform(2, 5)
        print(f"\n...页面处理完毕，暂停 {pause_time:.2f} 秒...\n")
        time.sleep(pause_time)

    print(f"\n爬取完成！共提取 {total_movies} 部电影。")
    return movie_items_html


def write_html_file(content):
    """
    将所有内容组合并写入最终的 HTML 文件。
    """
    print(f"正在生成 HTML 文件: {OUTPUT_FILENAME}")
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            # 写入头部
            f.write(HTML_HEAD)
            # 写入所有电影的 HTML
            f.write(content)
            # 写入尾部
            f.write(HTML_FOOT)
        print("文件生成成功！")
    except IOError as e:
        print(f"!!! 写入文件时发生错误: {e}")


if __name__ == '__main__':
    # 检查是否设置了豆瓣ID
    if DOUBAN_ID == "your_douban_id_here":
        print("!!! 请在脚本中设置你的 DOUBAN_ID。")
    else:
        # 首先加载固定的电影内容
        all_movie_content = FIXED_MOVIE_CONTENT_HTML
        # 然后追加从豆瓣爬取的内容
        all_movie_content += fetch_movies()
        
        if all_movie_content:
            write_html_file(all_movie_content)
        else:
            print("未能爬取到任何电影内容，不生成 HTML 文件。")

