import requests
from bs4 import BeautifulSoup
import time
import random
import os
import re

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")
PAGE_RANGE = range(0, 255, 15) 
OUTPUT_FILENAME = 'index.html'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
PROXIES = None

# --- HTML 模板 (The Archive 风格: 极简、硬朗、网格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CINEMA ARCHIVE</title>
    <meta name="description" content="A visual archive of films">
    
    <meta name="referrer" content="no-referrer">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg: #0a0a0a;
            --text-main: #ededed;
            --text-dim: #666666;
            --accent: #ff3300; /* 档案红 */
            --border: #222222;
            --card-min-width: 160px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* 顶部设计 */
        header {
            padding: 4rem 2rem;
            border-bottom: 1px solid var(--border);
            text-align: left;
        }

        h1.title {
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            font-size: clamp(3rem, 8vw, 6rem);
            letter-spacing: -0.04em;
            line-height: 0.9;
            text-transform: uppercase;
            margin-bottom: 1rem;
            color: var(--text-main);
        }

        .meta-info {
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-dim);
            font-size: 0.85rem;
            display: flex;
            gap: 2rem;
        }

        .meta-info span {
            display: block;
        }

        .meta-info span::before {
            content: '●';
            color: var(--accent);
            margin-right: 0.5em;
            font-size: 0.6em;
            vertical-align: middle;
        }

        /* 网格系统：使用 gap 制造边框效果 */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr));
            gap: 1px; /* 关键：配合背景色形成1px边框 */
            background-color: var(--border); /* 网格线的颜色 */
            border-bottom: 1px solid var(--border);
        }

        /* 电影卡片 */
        .card {
            background-color: var(--bg);
            position: relative;
            aspect-ratio: 2 / 3;
            overflow: hidden;
            text-decoration: none;
            transition: background-color 0.2s;
            group: card;
        }

        /* 图片处理 */
        .card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            /* 默认黑白+低对比度，制造一种“未激活”的冷淡感 */
            filter: grayscale(100%) contrast(90%);
            opacity: 0.8;
            transition: filter 0.4s ease, transform 0.6s cubic-bezier(0.25, 1, 0.5, 1), opacity 0.4s ease;
            will-change: transform, filter;
        }

        /* 信息层：默认隐藏，悬停显示 */
        .card-overlay {
            position: absolute;
            inset: 0;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 60%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 2;
        }

        /* 序号 */
        .index-num {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--accent);
            transform: translateY(-10px);
            transition: transform 0.3s ease;
        }

        /* 标题 */
        .movie-name {
            font-weight: 600;
            font-size: 1.1rem;
            line-height: 1.2;
            color: #fff;
            transform: translateY(10px);
            transition: transform 0.3s ease;
        }

        /* --- 交互状态 --- */
        .card:hover {
            z-index: 10;
        }

        .card:hover img {
            filter: grayscale(0%) contrast(100%); /* 恢复全彩 */
            opacity: 1;
            transform: scale(1.05); /* 轻微放大 */
        }

        .card:hover .card-overlay {
            opacity: 1;
        }

        .card:hover .index-num,
        .card:hover .movie-name {
            transform: translateY(0);
        }

        /* 页脚 */
        footer {
            padding: 4rem 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--text-dim);
            text-align: right;
        }

        /* 简单的淡入动画，不用延迟，解决慢的感觉 */
        @keyframes simpleFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .card {
            animation: simpleFadeIn 0.6s ease-out forwards;
        }

        @media (max-width: 600px) {
            :root { --card-min-width: 130px; }
            h1.title { font-size: 3rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="title">Cinema<br>Archive.</h1>
        <div class="meta-info">
            <span>COLLECTION: TOP 250</span>
            <span>CURATED BY FOX</span>
        </div>
    </header>
    
    <main class="grid-container">
"""

HTML_FOOT = """
    </main>
    <footer>
        [END OF ARCHIVE]<br>
        GENERATED VIA PYTHON
    </footer>
</body>
</html>
"""

# --- 固定的电影内容 ---
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

def clean_douban_url(url):
    """
    清洗豆瓣图片链接，强制替换为 img1 域名
    """
    if not url:
        return ""
    
    # 1. 替换海报尺寸为大图
    url = url.replace('s_ratio_poster', 'l_ratio_poster').replace('small', 'large')
    
    # 2. 强制将 img3, img9, img2 等替换为 img1 (关键修复!)
    # 使用正则确保只替换域名部分的 imgX
    url = re.sub(r'img[0-9]\.doubanio\.com', 'img1.doubanio.com', url)
    
    return url

def generate_movie_html(movie_data, counter):
    """
    生成单个电影HTML。
    """
    title = movie_data['title'].replace("'", "&apos;")
    index_str = f"{counter + 1:03d}"
    
    # 极简深色占位图
    placeholder = "https://placehold.co/400x600/111/111.png"
    
    return f"""
        <a class="card" href="{movie_data['href']}" target="_blank" title="{title}">
            <img src="{movie_data['img_src']}" 
                 alt="{title}" 
                 loading="lazy" 
                 decoding="async"
                 referrerPolicy="no-referrer"
                 onerror="this.onerror=null;this.src='{placeholder}';">
            <div class="card-overlay">
                <span class="index-num">#{index_str}</span>
                <h3 class="movie-name">{title}</h3>
            </div>
        </a>"""

def fetch_movies(start_counter):
    """爬取豆瓣电影数据"""
    movie_items_html = ""
    total_movies = 0
    movie_counter = start_counter

    print(f"--- 开始执行 ---")
    print(f"目标用户: {DOUBAN_ID}")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        try:
            print(f"正在读取: 第 {i} - {i+15} 条目...")
            response = requests.get(page_url, headers={'User-Agent': USER_AGENT}, proxies=PROXIES, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[错误] 无法访问: {e}")
            continue

        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        movie_list = soup.findAll('div', class_="item")

        if not movie_list:
            print("--- 已到达列表末尾 ---")
            break

        for item in movie_list:
            try:
                item_link_tag = item.find("a")
                item_img_tag = item.find("img")
                
                raw_src = item_img_tag['src']
                # 使用清洗函数处理图片链接
                img_src = clean_douban_url(raw_src)
                
                movie_data = {
                    "title": item_img_tag['alt'],
                    "href": item_link_tag['href'],
                    "img_src": img_src,
                }
                movie_items_html += generate_movie_html(movie_data, movie_counter)
                total_movies += 1
                movie_counter += 1
            except Exception as e:
                pass 
        
        time.sleep(random.uniform(1, 3))

    print(f"--- 任务完成: 共获取 {total_movies} 部电影 ---")
    return movie_items_html

def write_html_file(content):
    """写入HTML"""
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(HTML_HEAD)
            f.write(content)
            f.write(HTML_FOOT)
        print(f"成功生成文件: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"写入文件失败: {e}")

if __name__ == '__main__':
    if DOUBAN_ID == "your_douban_id_here":
        print("警告: 未设置 DOUBAN_ID。请修改代码或设置环境变量。")
    else:
        movie_counter = 0
        all_movie_content = ""
        
        # 1. 处理固定电影
        for movie_data in FIXED_MOVIES:
            all_movie_content += generate_movie_html(movie_data, movie_counter)
            movie_counter += 1
        
        # 2. 爬取豆瓣电影
        all_movie_content += fetch_movies(start_counter=movie_counter)
        
        # 3. 生成文件
        if all_movie_content:
            write_html_file(all_movie_content)
        else:
            print("未生成任何内容。")
