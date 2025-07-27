import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")
PAGE_RANGE = range(0, 255, 15) 
OUTPUT_FILENAME = 'index.html'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
PROXIES = None

# --- HTML 模板 (全新矩阵风格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fox的电影Top250</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* --- 全局与主题设置 --- */
        :root {
            --background-color: #101010; /* 深邃的炭黑背景 */
            --text-color: #e0e0e0; /* 柔和的白色文字 */
            --primary-glow-color: rgba(0, 255, 255, 0.15); /* 青色辉光 */
            --secondary-glow-color: rgba(0, 255, 255, 0.05);
            --card-border-radius: 12px;
            --grid-gap: 1.5rem; /* 网格间距 */
        }

        body {
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif, "Microsoft YaHei";
            margin: 0;
            padding: 2rem;
            overflow-x: hidden;
        }

        /* --- 标题样式 --- */
        .main-title {
    text-align: center;
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 700;
    margin-bottom: 3rem;
    
    /* 关键改动在这里 */
    display: inline-block; /* 或者 width: fit-content; */
    
    background: linear-gradient(90deg, #6a71e0, #42a5f5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-fill-color: transparent;
    animation: fadeInDown 1s ease-out;
}
        
        /* --- 电影网格布局 (CSS Grid) --- */
        .movie-grid {
            display: grid;
            /* 核心响应式布局：自动填充，每列最小140px，最大1fr */
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: var(--grid-gap);
        }

        /* --- 电影卡片样式 --- */
        .movie-card {
            position: relative;
            display: block;
            overflow: hidden;
            border-radius: var(--card-border-radius);
            transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1),
                        box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            text-decoration: none;
            color: inherit;
            opacity: 0; /* 初始不可见，为加载动画准备 */
            animation: fadeInUp 0.5s ease-out forwards;
        }
        
        .movie-card img {
            width: 100%;
            height: 100%;
            object-fit: cover; /* 保证图片比例，裁剪多余部分 */
            display: block;
            transition: transform 0.4s ease;
        }
        
        /* --- 悬停效果 --- */
        .movie-card:hover {
            transform: scale(1.05) translateY(-8px);
            box-shadow: 0 0 20px var(--primary-glow-color),
                        0 0 40px var(--secondary-glow-color);
            z-index: 10; /* 确保悬停的卡片在最上层 */
        }
        
        .movie-card:hover img {
            transform: scale(1.1); /* 图片轻微放大，增加动感 */
        }

        /* --- 卡片信息浮层 --- */
        .card-info {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 2rem 1rem 1rem 1rem;
            background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 20%, transparent 100%);
            transform: translateY(100%); /* 初始状态在卡片下方 */
            opacity: 0;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }

        .movie-card:hover .card-info {
            transform: translateY(0);
            opacity: 1;
        }

        .movie-title {
            margin: 0;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.3;
            color: #fff;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }

        /* --- 页脚 --- */
        .footer {
            text-align: center;
            padding: 4rem 0 1rem 0;
            font-size: 0.9rem;
            color: #555;
            animation: fadeInUp 1s 0.5s ease-out forwards;
            opacity: 0;
        }
        
        /* --- 加载动画 --- */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInDown {
             from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>
    <h1 class="main-title">Fox的电影Top250</h1>
    <main class="movie-grid">
"""

HTML_FOOT = """
    </main>
    <footer class="footer">
        <p>含哺而熙，鼓腹而游 @ 2025</p>
    </footer>
</body>
</html>
"""

# --- 固定的电影内容 ---
# 注意：浮层中的标题将使用爬取到的原始标题。
FIXED_MOVIES = [
    {
        "title": "Дорогие товарищи!",
        "href": "https://www.imdb.com/title/tt10796286",
        "img_src": "https://m.media-amazon.com/images/M/MV5BZGZlNTAwNzgtODUwYy00YjZiLWJlMzctYjFjNDFmYjE3M2ZlXkEyXkFqcGc@._V1_QL75_UX322_.jpg",
    },
    {
        "title": "1987",
        "href": "https://www.imdb.com/title/tt6493286",
        "img_src": "https://m.media-amazon.com/images/M/MV5BZjU2OTJkNWUtMTBhZi00NDJjLTgwMmYtOGQ3YmQ4ZjE3NWI1XkEyXkFqcGc@._V1_QL75_UX306_.jpg",
    },
    {
        "title": "택시운전사",
        "href": "https://www.imdb.com/title/tt6878038",
        "img_src": "https://m.media-amazon.com/images/M/MV5BYWU2YzE1YWQtYTNhYi00YTk3LTgxZTMtODA3ZTJkZGU3MWVkXkEyXkFqcGc@._V1_QL75_UX306_.jpg",
    },
    {
        "title": "悲兮魔兽",
        "href": "https://www.imdb.com/title/tt4901304",
        "img_src": "https://m.media-amazon.com/images/M/MV5BMTQ5MTk5NTgyMV5BMl5BanBnXkFtZTgwNDI0NTY4MDI@._V1_FMjpg_UX1200_.jpg",
    },
    {
        "title": "The Death of Stalin",
        "href": "https://www.imdb.com/title/tt4686844/",
        "img_src": "https://m.media-amazon.com/images/M/MV5BMTcxMDc1NjcyNl5BMl5BanBnXkFtZTgwNDU0NDYxMzI@._V1_QL75_UX380_CR0,0,380,562_.jpg",
    }
]

def generate_movie_html(movie_data, counter):
    """根据电影数据和计数器生成单个电影的HTML块"""
    delay = counter * 0.05  # 计算动画延迟时间
    title = movie_data['title'].replace("'", "&apos;") # 处理标题中的单引号
    
    return f"""
        <a class="movie-card" href="{movie_data['href']}" target="_blank" title="{title}" style="animation-delay: {delay}s;">
            <img src="{movie_data['img_src']}" alt="{title}" onerror="this.onerror=null;this.src='https://placehold.co/400x600/101010/e0e0e0?text=Image+Not+Found';" referrerPolicy="no-referrer">
            <div class="card-info">
                <h3 class="movie-title">{title}</h3>
            </div>
        </a>"""

def fetch_movies(start_counter):
    """爬取豆瓣电影数据并返回HTML内容块"""
    movie_items_html = ""
    total_movies = 0
    movie_counter = start_counter

    print(f"开始从豆瓣用户 '{DOUBAN_ID}' 的收藏页面爬取数据...")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        try:
            print(f"正在爬取页面: {page_url}")
            response = requests.get(page_url, headers={'User-Agent': USER_AGENT}, proxies=PROXIES, timeout=10)
            response.raise_for_status()
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
                item_link_tag = item.find("a")
                item_img_tag = item.find("img")
                movie_data = {
                    "title": item_img_tag['alt'],
                    "href": item_link_tag['href'],
                    "img_src": item_img_tag['src'].replace('small', 'large'),
                }
                movie_items_html += generate_movie_html(movie_data, movie_counter)
                total_movies += 1
                movie_counter += 1
                print(f"  [+] 成功提取: {movie_data['title']}")
            except Exception as e:
                print(f"  [!] 解析某个项目时出错: {e}")
        
        pause_time = random.uniform(2, 5)
        print(f"\n...页面处理完毕，暂停 {pause_time:.2f} 秒...\n")
        time.sleep(pause_time)

    print(f"\n爬取完成！共提取 {total_movies} 部电影。")
    return movie_items_html

def write_html_file(content):
    """将所有内容组合并写入最终的HTML文件"""
    print(f"正在生成 HTML 文件: {OUTPUT_FILENAME}")
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(HTML_HEAD)
            f.write(content)
            f.write(HTML_FOOT)
        print("文件生成成功！")
    except IOError as e:
        print(f"!!! 写入文件时发生错误: {e}")

if __name__ == '__main__':
    if DOUBAN_ID == "your_douban_id_here":
        print("!!! 请在脚本中设置你的 DOUBAN_ID。")
    else:
        movie_counter = 0
        all_movie_content = ""
        
        print("正在处理固定的电影内容...")
        for movie_data in FIXED_MOVIES:
            all_movie_content += generate_movie_html(movie_data, movie_counter)
            movie_counter += 1
            print(f"  [+] 已添加固定电影: {movie_data['title']}")
        
        all_movie_content += fetch_movies(start_counter=movie_counter)
        
        if all_movie_content:
            write_html_file(all_movie_content)
        else:
            print("未能生成任何电影内容，不创建 HTML 文件。")
