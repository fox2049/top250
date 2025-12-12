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

# --- HTML 模板 (Cyber-Minimalism 风格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FOX's CINEMA UNIVERSE</title>
    <meta name="description" content="A curated collection of movies">
    
    <meta name="referrer" content="no-referrer">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=Space+Grotesk:wght@300;700&display=swap" rel="stylesheet">
    
    <style>
        /* --- 变量定义 --- */
        :root {
            --bg-color: #050505;
            --card-bg: rgba(255, 255, 255, 0.03);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent-gradient: linear-gradient(45deg, #ff0055, #00ddff);
            --glow-color: rgba(0, 221, 255, 0.3);
            --card-radius: 16px;
            --transition-curve: cubic-bezier(0.34, 1.56, 0.64, 1); /* 顺滑的贝塞尔曲线 */
        }

        /* --- 全局重置 --- */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            background-color: var(--bg-color);
            /* 背景流体光斑 */
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.15), transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(0, 221, 255, 0.15), transparent 25%);
            color: var(--text-primary);
            font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; /* 混搭字体 */
            min-height: 100vh;
            overflow-x: hidden;
            padding: 2rem 5%;
        }

        /* --- 核心设计：动态背景噪点 (Noise) --- */
        /* 这层蒙版会让网页瞬间拥有"质感" */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: -1;
        }

        /* --- 标题区域 --- */
        header {
            text-align: center;
            margin: 6rem 0 6rem 0;
            position: relative;
        }

        .main-title {
            /* 巨大的排版 */
            font-size: clamp(3rem, 10vw, 6rem);
            font-weight: 700;
            line-height: 0.9;
            letter-spacing: -0.04em;
            text-transform: uppercase;
            
            /* 渐变文字 */
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            margin-bottom: 1.5rem;
            position: relative;
            display: inline-block;
            animation: titleEnter 1.2s var(--transition-curve);
        }
        
        /* 标题下的动态装饰线 */
        .main-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--accent-gradient);
            transform: scaleX(0);
            transform-origin: right;
            transition: transform 0.5s ease;
            animation: lineEnter 1s 0.8s forwards ease;
        }

        @keyframes titleEnter {
            from { opacity: 0; transform: translateY(50px) skewY(5deg); }
            to { opacity: 1; transform: translateY(0) skewY(0); }
        }
        
        @keyframes lineEnter {
            to { transform: scaleX(1); transform-origin: left; }
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            letter-spacing: 0.2em; /* 极宽的字间距 */
            animation: fadeIn 1s 0.5s forwards;
            opacity: 0;
            font-weight: 300;
        }

        /* --- 网格布局 --- */
        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 2rem;
            max-width: 1600px;
            margin: 0 auto;
        }

        /* --- 前卫卡片设计 --- */
        .movie-card {
            position: relative;
            border-radius: var(--card-radius);
            overflow: hidden;
            text-decoration: none;
            
            /* 玻璃拟态背景 */
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px); /* 磨砂玻璃效果 */
            
            transition: all 0.4s var(--transition-curve);
            aspect-ratio: 2 / 3;
            opacity: 0;
            transform: translateY(30px);
            animation: cardEnter 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        /* 默认遮罩 */
        .movie-card::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.8) 100%);
            z-index: 1;
            opacity: 0.5;
            transition: opacity 0.3s;
        }

        .movie-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.7s var(--transition-curve); /* 图片移动慢一点，制造视差感 */
            display: block;
            filter: grayscale(20%); /* 默认稍微去色，更高级 */
        }

        /* --- 信息浮层 --- */
        .card-info {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 1.5rem;
            z-index: 2;
            transform: translateY(10px);
            opacity: 0;
            transition: all 0.4s var(--transition-curve);
        }

        .movie-title {
            color: #fff;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.8);
            line-height: 1.2;
        }

        .view-btn {
            display: inline-block;
            margin-top: 0.8rem;
            font-size: 0.75rem;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid rgba(255,255,255,0.5);
            padding-bottom: 2px;
            opacity: 0.8;
        }

        /* --- 悬停交互 (Hover) --- */
        .movie-card:hover {
            transform: translateY(-10px) scale(1.02);
            /* 发光边框 */
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(0, 221, 255, 0.1);
            z-index: 10;
        }

        .movie-card:hover img {
            transform: scale(1.1);
            filter: grayscale(0%); /* 悬停恢复色彩 */
        }

        .movie-card:hover::before {
            opacity: 0.8; /* 加深背景以便看清文字 */
        }

        .movie-card:hover .card-info {
            transform: translateY(0);
            opacity: 1;
        }

        /* --- 动画关键帧 --- */
        @keyframes cardEnter {
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            to { opacity: 1; }
        }

        /* --- 页脚 --- */
        footer {
            margin-top: 8rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.8rem;
            padding-bottom: 3rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            opacity: 0.5;
        }

        /* --- 响应式 --- */
        @media (max-width: 600px) {
            .movie-grid {
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 1rem;
            }
            .main-title { font-size: 3.5rem; }
            header { margin: 4rem 0; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="main-title">CINEMA 250</h1>
        <div class="subtitle">A VISUAL COLLECTION BY FOX</div>
    </header>
    
    <main class="movie-grid">
"""

HTML_FOOT = """
    </main>
    <footer>
        <p>Designed by Python & GitHub Actions © 2025</p>
    </footer>
</body>
</html>
"""

# --- 固定的电影内容 (保持你的数据) ---
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
    包含：防盗链、占位图、延迟动画
    """
    # 让动画像多米诺骨牌一样流畅，但限制最大延迟
    delay = min(counter * 0.04, 2.0) 
    title = movie_data['title'].replace("'", "&apos;")
    
    # 极简主义风格的占位图
    placeholder = "https://placehold.co/400x600/1a1a1a/444444?text=NO+IMG"
    
    return f"""
        <a class="movie-card" href="{movie_data['href']}" target="_blank" style="animation-delay: {delay}s;">
            <img src="{movie_data['img_src']}" 
                 alt="{title}" 
                 onerror="this.onerror=null;this.src='{placeholder}';" 
                 referrerPolicy="no-referrer"
                 loading="lazy">
            <div class="card-info">
                <h3 class="movie-title">{title}</h3>
                <span class="view-btn">View Details</span>
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
                # 尝试获取更高清的图片链接
                img_src = item_img_tag['src'].replace('s_ratio_poster', 'l_ratio_poster').replace('small', 'large')
                
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
        
        # 随机暂停，避免被封IP
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
    # ⚠️ 请确保在运行时设置环境变量 DOUBAN_ID，或者在此处直接修改
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
