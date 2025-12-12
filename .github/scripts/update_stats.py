import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")  # 替换成你的 ID
PAGE_RANGE = range(0, 255, 15) 
OUTPUT_FILENAME = 'index.html'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
PROXIES = None

# --- HTML 模板 (更新为你的"Top250"深色辉光风格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    
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
            display: block; 
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
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: var(--grid-gap);
            max-width: 1400px;
            margin: 0 auto;
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
            opacity: 0;
            animation: fadeInUp 0.5s ease-out forwards;
            aspect-ratio: 2 / 3;
            background: #1a1a1a;
        }
        
        .movie-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.4s ease;
        }
        
        /* --- 悬停效果 --- */
        .movie-card:hover {
            transform: scale(1.05) translateY(-8px);
            box-shadow: 0 0 20px var(--primary-glow-color),
                        0 0 40px var(--secondary-glow-color);
            z-index: 10;
        }
        
        .movie-card:hover img {
            transform: scale(1.1);
        }

        /* --- 卡片信息浮层 --- */
        .card-info {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 2rem 1rem 1rem 1rem;
            background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 20%, transparent 100%);
            transform: translateY(100%);
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
        
        /* --- 动画 --- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInDown {
             from { opacity: 0; transform: translateY(-20px); }
             to { opacity: 1; transform: translateY(0); }
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

# --- 固定的电影内容 (保持不变) ---
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
    """
    生成单个电影的HTML块
    关键修改：添加 referrerPolicy 和 onerror
    """
    delay = min(counter * 0.05, 3.0) 
    title = movie_data['title'].replace("'", "&apos;")
    
    # 占位图：当图片加载失败时显示的灰色卡片
    placeholder = "https://placehold.co/400x600/101010/e0e0e0?text=Image+Not+Found"
    
    return f"""
        <a class="movie-card" href="{movie_data['href']}" target="_blank" title="{title}" style="animation-delay: {delay}s;">
            <img src="{movie_data['img_src']}" 
                 alt="{title}" 
                 onerror="this.onerror=null;this.src='{placeholder}';" 
                 referrerPolicy="no-referrer">
            <div class="card-info">
                <h3 class="movie-title">{title}</h3>
            </div>
        </a>"""

def fetch_movies(start_counter):
    """爬取豆瓣电影数据并返回HTML内容块"""
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
            print(f"[错误] 无法
