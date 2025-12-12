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

# --- HTML 模板 (The Darkroom 风格: 黑白交互、无序号、紧凑网格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE CINEMA ARCHIVE</title>
    
    <meta name="referrer" content="no-referrer">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg: #050505;
            --text: #e0e0e0;
            --border: #1f1f1f; /* 极细的深灰边框 */
            --card-min-width: 140px; /* 适配小图的最佳宽度 */
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* 顶部设计：极简主义 */
        header {
            padding: 5rem 2rem;
            border-bottom: 1px solid var(--border);
            max-width: 1920px;
            margin: 0 auto;
            width: 100%;
        }

        h1.title {
            font-family: 'Playfair Display', serif;
            font-size: clamp(2.5rem, 6vw, 5rem);
            font-weight: 400;
            letter-spacing: -0.02em;
            margin: 0;
            line-height: 1;
        }
        
        .subtitle {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: #555;
            margin-top: 1rem;
        }

        /* 网格容器：利用背景色和 gap 制造 1px 边框 */
        .archive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr));
            gap: 1px;
            background-color: var(--border);
            border-bottom: 1px solid var(--border);
            max-width: 1920px;
            margin: 0 auto;
            width: 100%;
        }

        /* 单个卡片 */
        .film-card {
            position: relative;
            background-color: var(--bg);
            aspect-ratio: 2 / 3;
            overflow: hidden;
            text-decoration: none;
            /* 关键：去掉圆角，回归硬朗 */
        }

        /* 图片容器 */
        .img-wrap {
            width: 100%;
            height: 100%;
            position: relative;
        }

        .img-wrap img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            
            /* --- 核心设计：默认黑白+轻微降暗 --- */
            filter: grayscale(100%) brightness(0.9);
            opacity: 0.9;
            
            /* 平滑过渡，像胶片显影一样 */
            transition: filter 0.6s cubic-bezier(0.22, 1, 0.36, 1), 
                        transform 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                        opacity 0.6s ease;
        }

        /* 信息浮层：默认隐藏 */
        .info-layer {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 1.5rem 1rem;
            background: linear-gradient(to top, rgba(0,0,0,0.95), transparent);
            transform: translateY(100%); /* 藏在下面 */
            transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
            display: flex;
            align-items: flex-end;
            z-index: 2;
        }

        .movie-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #fff;
            line-height: 1.3;
            letter-spacing: 0.02em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        /* --- 交互状态 (Hover) --- */
        
        .film-card:hover {
            z-index: 10;
        }

        /* 鼠标悬停：变彩色 + 轻微放大 */
        .film-card:hover img {
            filter: grayscale(0%) brightness(1.05);
            transform: scale(1.03);
            opacity: 1;
        }

        /* 鼠标悬停：浮出文字 */
        .film-card:hover .info-layer {
            transform: translateY(0);
        }

        /* 页脚 */
        footer {
            padding: 4rem 2rem;
            text-align: center;
            font-size: 0.75rem;
            color: #444;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* 简单的载入动画 */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .film-card {
            animation: fadeIn 0.8s ease-out forwards;
        }

        @media (max-width: 600px) {
            .archive-grid {
                /* 手机端每行3个，保持密集感 */
                grid-template-columns: repeat(3, 1fr); 
            }
            .info-layer { display: none; } /* 手机端太小，不显示悬停文字，只看图 */
            header { padding: 3rem 1.5rem; }
            h1.title { font-size: 3rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="title">Cinema Archive</h1>
        <div class="subtitle">A Visual Collection / Top 250</div>
    </header>
    
    <main class="archive-grid">
"""

HTML_FOOT = """
    </main>
    <footer>
        <p>Curated by Fox / Generated via Python</p>
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

def generate_movie_html(movie_data, counter):
    """
    生成单个电影HTML
    """
    title = movie_data['title'].replace("'", "&apos;")
    
    # 占位图
    placeholder = "https://placehold.co/300x450/1a1a1a/1a1a1a.png"
    
    # 注意：移除了 index 序号的显示
    return f"""
        <a class="film-card" href="{movie_data['href']}" target="_blank" title="{title}">
            <div class="img-wrap">
                <img src="{movie_data['img_src']}" 
                     alt="{title}" 
                     loading="lazy" 
                     decoding="async"
                     referrerPolicy="no-referrer"
                     onerror="this.onerror=null;this.src='{placeholder}';">
            </div>
            <div class="info-layer">
                <h3 class="movie-title">{title}</h3>
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
                
                # --- 核心：保持使用小图 (s_ratio_poster) ---
                raw_src = item_img_tag['src']
                
                movie_data = {
                    "title": item_img_tag['alt'],
                    "href": item_link_tag['href'],
                    "img_src": raw_src, # 直接用原图，最快最稳
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
        
        for movie_data in FIXED_MOVIES:
            all_movie_content += generate_movie_html(movie_data, movie_counter)
            movie_counter += 1
        
        all_movie_content += fetch_movies(start_counter=movie_counter)
        
        if all_movie_content:
            write_html_file(all_movie_content)
        else:
            print("未生成任何内容。")
