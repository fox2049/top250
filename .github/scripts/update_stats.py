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

# --- HTML 模板 (Archive 风格 - 适配小图加载) ---

HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FOX's COLLECTION</title>
    <meta name="description" content="A visual archive of cinema">
    
    <meta name="referrer" content="no-referrer">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg: #0f0f0f;
            --text: #e0e0e0;
            --text-dim: #555;
            --accent: #fff;
            /* 调整：因为是小图，卡片最小宽度稍微调小一点，保证清晰度 */
            --grid-gap: 30px; 
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            padding: 0 4vw;
        }

        header {
            padding: 6rem 0 3rem 0;
            border-bottom: 1px solid #222;
            margin-bottom: 3rem;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }

        h1.title {
            font-family: 'Playfair Display', serif;
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 400;
            line-height: 1;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
        }

        h1.title span {
            display: block;
            font-style: italic;
            color: var(--text-dim);
            font-size: 0.5em;
            margin-top: 0.2em;
        }

        .meta {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--text-dim);
            margin-top: 1rem;
        }

        /* 瀑布流网格 */
        .gallery {
            display: grid;
            /* 自动填充，每列最小 140px，这样小图不会被拉伸得太模糊 */
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: var(--grid-gap) 15px; 
            padding-bottom: 8rem;
        }

        .item {
            position: relative;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
        }

        .poster-box {
            position: relative;
            aspect-ratio: 2 / 3;
            overflow: hidden;
            background: #1a1a1a;
            margin-bottom: 10px;
            transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.4s ease;
        }

        .poster-box img {
            width: 100%;
            height: 100%;
            object-fit: cover; /* 保持比例填满 */
            display: block;
            opacity: 0.8;
            filter: grayscale(20%); /* 降低一点点饱和度，增加质感 */
            transition: opacity 0.4s ease, filter 0.4s ease, transform 0.7s ease;
        }

        .info {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            opacity: 0.5;
            transition: opacity 0.3s ease;
            font-size: 0.85rem;
        }

        .movie-title {
            font-weight: 500;
            line-height: 1.3;
            max-width: 90%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap; /* 单行显示标题，保持整洁 */
        }

        .index {
            font-family: 'Playfair Display', serif;
            font-style: italic;
            font-size: 0.8rem;
            color: var(--text-dim);
            margin-left: 8px;
        }

        /* 交互效果 */
        .item:hover .poster-box {
            transform: translateY(-4px);
            box-shadow: 0 10px 20px -5px rgba(0,0,0,0.5);
        }

        .item:hover img {
            opacity: 1;
            filter: grayscale(0%);
            transform: scale(1.05);
        }

        .item:hover .info {
            opacity: 1;
            color: var(--accent);
        }

        /* 懒加载淡入 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .item {
            animation: fadeIn 0.6s ease-out forwards;
        }

        footer {
            border-top: 1px solid #222;
            padding: 3rem 0;
            color: var(--text-dim);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        @media (max-width: 600px) {
            h1.title { font-size: 3.5rem; }
            .gallery {
                grid-template-columns: repeat(3, 1fr); /* 手机上每行3个 */
                gap: 15px 8px;
            }
            body { padding: 0 3vw; }
            .movie-title { font-size: 0.75rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="title">
            Top 250
            <span>The Cinema Archive</span>
        </h1>
        <div class="meta">Fox's Collection</div>
    </header>
    
    <main class="gallery">
"""

HTML_FOOT = """
    </main>
    <footer>
        <p>Generated via Python</p>
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
    index_str = f"{counter + 1}"
    
    # 占位图
    placeholder = "https://placehold.co/270x400/1a1a1a/1a1a1a.png"
    
    return f"""
        <a class="item" href="{movie_data['href']}" target="_blank" title="{title}">
            <div class="poster-box">
                <img src="{movie_data['img_src']}" 
                     alt="{title}" 
                     loading="lazy" 
                     decoding="async"
                     referrerPolicy="no-referrer"
                     onerror="this.onerror=null;this.src='{placeholder}';">
            </div>
            <div class="info">
                <span class="movie-title">{title}</span>
                <span class="index">{index_str}</span>
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
                
                # --- 关键修改：直接使用原始链接 (即 s_ratio_poster) ---
                # 不进行任何 replace 操作，确保链接最原始、最稳定
                raw_src = item_img_tag['src']
                img_src = raw_src 
                
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
        
        # 随机暂停
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
