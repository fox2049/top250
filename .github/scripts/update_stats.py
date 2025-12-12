import requests
from bs4 import BeautifulSoup
import time
import random
import os
from urllib.parse import quote

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here") 
PAGE_RANGE = range(0, 255, 15)
OUTPUT_FILENAME = 'index.html'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
PROXIES = None

# --- 图片代理函数 (核心修复) ---
def get_proxy_url(original_url):
    """
    使用 wsrv.nl 代理服务。
    作用：
    1. 绕过豆瓣防盗链 (Referer check)
    2. 解决 IMDb 在国内无法加载的问题
    3. 自动压缩为 WebP 格式，加载更快
    """
    if not original_url:
        return ""
    # output=webp: 转换为 webp 格式
    # q=75: 75% 质量压缩
    return f"https://wsrv.nl/?url={quote(original_url)}&output=webp&q=75"

# --- HTML 模板 (Brutalist Cinema 风格) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FOX's ARCHIVE</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #080808;
            --text-main: #f0f0f0;
            --text-sub: #666;
            --accent: #ff3333; /* 电影红 */
            --grid-line: #1a1a1a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'JetBrains Mono', monospace; /* 像剧本一样的字体 */
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* 顶部设计 */
        header {
            padding: 4rem 2rem;
            border-bottom: 1px solid var(--grid-line);
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            max-width: 1800px;
            margin: 0 auto;
        }

        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 400;
            font-style: italic;
            line-height: 1;
            margin-bottom: 1rem;
            color: var(--text-main);
        }

        .subtitle {
            font-size: 0.9rem;
            color: var(--text-sub);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .subtitle::before {
            content: '';
            display: block;
            width: 40px;
            height: 1px;
            background: var(--accent);
        }

        /* 电影网格 */
        .movie-grid {
            display: grid;
            /* 响应式网格 */
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            /* 极简分割线效果：利用 gap 和背景色 */
            gap: 1px;
            background-color: var(--grid-line); 
            border-bottom: 1px solid var(--grid-line);
            max-width: 1800px;
            margin: 0 auto;
        }

        /* 电影卡片 */
        .movie-card {
            position: relative;
            background-color: var(--bg-color);
            aspect-ratio: 2 / 3;
            overflow: hidden;
            text-decoration: none;
            transition: z-index 0s 0.3s; /* 延迟层级变化 */
        }

        /* 图片容器 */
        .img-wrapper {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
        }

        .movie-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            filter: grayscale(100%) contrast(1.1); /* 默认黑白 */
            transition: transform 0.5s cubic-bezier(0.2, 1, 0.3, 1),
                        filter 0.5s ease;
            opacity: 0.8;
        }

        /* 编号/信息浮层 */
        .meta-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            opacity: 0;
            background: rgba(8, 8, 8, 0.8);
            backdrop-filter: blur(4px);
            transition: opacity 0.3s ease;
            z-index: 2;
        }

        .movie-index {
            font-size: 0.8rem;
            color: var(--accent);
            font-weight: 700;
        }

        .movie-title {
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            line-height: 1.2;
            color: #fff;
            transform: translateY(20px);
            transition: transform 0.4s ease;
        }

        /* 悬停交互 */
        .movie-card:hover {
            z-index: 10;
        }

        .movie-card:hover img {
            filter: grayscale(0%) contrast(1); /* 恢复彩色 */
            transform: scale(1.1);
            opacity: 1;
        }

        .movie-card:hover .meta-layer {
            opacity: 1;
        }

        .movie-card:hover .movie-title {
            transform: translateY(0);
        }

        /* 页脚 */
        footer {
            padding: 4rem 2rem;
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-sub);
            border-top: 1px solid var(--grid-line);
            max-width: 1800px;
            margin: 0 auto;
        }

        /* 初始加载动画 */
        .movie-card {
            animation: fadeIn 0.6s ease-out forwards;
            opacity: 0;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            .movie-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .main-title { font-size: 3rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="main-title">Cinema Archive</h1>
        <div class="subtitle">Fox's Collection / Top 250</div>
    </header>
    
    <main class="movie-grid">
"""

HTML_FOOT = """
    </main>
    <footer>
        <p>CURATED BY FOX • GENERATED VIA PYTHON</p>
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
    生成单个电影的 HTML 块
    使用代理 URL 确保图片 100% 显示
    """
    # 动画延迟，产生流水线效果
    delay = min(counter * 0.03, 1.5) 
    
    # 获取原始图片链接并转换为代理链接
    original_img = movie_data['img_src']
    proxy_img = get_proxy_url(original_img)
    
    title = movie_data['title'].replace("'", "&apos;")
    # 编号格式化，例如 001, 002
    index_str = f"NO.{counter + 1:03d}"
    
    # 占位图使用深灰色纯色，保持极简
    placeholder = "https://placehold.co/400x600/111/111.png"
    
    return f"""
        <a class="movie-card" href="{movie_data['href']}" target="_blank" style="animation-delay: {delay}s;">
            <div class="img-wrapper">
                <img src="{proxy_img}" 
                     alt="{title}" 
                     loading="lazy"
                     onerror="this.onerror=null;this.src='{placeholder}';">
            </div>
            <div class="meta-layer">
                <span class="movie-index">{index_str}</span>
                <h3 class="movie-title">{title}</h3>
            </div>
        </a>"""

def fetch_movies(start_counter):
    """爬取豆瓣电影数据并返回 HTML 内容块"""
    movie_items_html = ""
    total_movies = 0
    movie_counter = start_counter

    print(f"--- 开始执行 ---")
    print(f"目标用户: {DOUBAN_ID}")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        try:
            print(f"正在读取: 第 {i} - {i+15} 条目...")
            response = requests.get(page_url, headers={'User-Agent': USER_AGENT}, proxies=PROXIES, timeout=15)
            
            if response.status_code == 403:
                print("!! 遇到 403 禁止访问，可能 IP 被暂时限制，休息 5 秒...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[错误] 网络请求失败: {e}")
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
                
                # 获取原始链接
                raw_src = item_img_tag['src']
                # 尝试替换为大图链接 (虽然我们会用代理，但给代理高清源地址更好)
                img_src = raw_src.replace('s_ratio_poster', 'l_ratio_poster').replace('small', 'large').replace('img1', 'img9').replace('img3', 'img9')
                
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
        
        # 稍微增加随机延迟，保护爬虫
        time.sleep(random.uniform(2, 4))

    print(f"--- 任务完成: 共获取 {total_movies} 部电影 ---")
    return movie_items_html

def write_html_file(content):
    """写入 HTML 文件"""
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(HTML_HEAD)
            f.write(content)
            f.write(HTML_FOOT)
        print(f"成功生成文件: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"写入文件失败: {e}")

if __name__ == '__main__':
    # ⚠️ 请确保在运行时设置环境变量 DOUBAN_ID
    if DOUBAN_ID == "your_douban_id_here":
        print("警告: 未设置 DOUBAN_ID。")
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
