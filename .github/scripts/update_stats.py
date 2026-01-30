import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")
PAGE_RANGE = range(0, 255, 15) 
OUTPUT_FILENAME = 'index.html'
# 模拟真实浏览器
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# 关键：爬取页面时必须伪造的头
DOUBAN_HEADERS = {
    'User-Agent': USER_AGENT,
    'Referer': 'https://www.douban.com/'
}
PROXIES = None

# --- HTML 模板 ---
HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE CINEMA ARCHIVE</title>
    <meta name="referrer" content="no-referrer">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #050505; --text: #e0e0e0; --border: #1f1f1f; --card-min-width: 140px; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; display: flex; flex-direction: column; }
        header { padding: 4rem 2rem; border-bottom: 1px solid var(--border); }
        h1.title { font-family: 'Playfair Display', serif; font-weight: 900; font-size: clamp(3rem, 8vw, 6rem); letter-spacing: -0.04em; line-height: 0.9; text-transform: uppercase; }
        .subtitle { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: #555; margin-top: 1rem; }
        .archive-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr)); gap: 1px; background-color: var(--border); }
        .film-card { position: relative; background-color: var(--bg); aspect-ratio: 2 / 3; overflow: hidden; text-decoration: none; animation: fadeIn 0.8s ease-out forwards; }
        .img-wrap { width: 100%; height: 100%; }
        .img-wrap img { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%) brightness(0.9); transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1); }
        .film-card:hover img { filter: grayscale(0%) brightness(1.05); transform: scale(1.03); }
        .info-layer { position: absolute; bottom: 0; width: 100%; padding: 1.5rem 1rem; background: linear-gradient(to top, rgba(0,0,0,0.95), transparent); transform: translateY(100%); transition: transform 0.4s ease; }
        .film-card:hover .info-layer { transform: translateY(0); }
        .movie-title { font-size: 0.85rem; color: #fff; line-height: 1.3; }
        footer { padding: 4rem 2rem; text-align: center; font-size: 0.75rem; color: #444; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @media (max-width: 600px) { .archive-grid { grid-template-columns: repeat(3, 1fr); } .info-layer { display: none; } }
    </style>
</head>
<body>
    <header>
        <h1 class="title">Cinema Archive</h1>
        <div class="subtitle">Collection by Fox2049</div>
    </header>
    <main class="archive-grid">
"""

HTML_FOOT = """
    </main>
    <footer><p>Curated by Fox / Generated via Python</p></footer>
</body>
</html>
"""

FIXED_MOVIES = [
    {"title": "Дорогие товарищи!", "href": "https://www.imdb.com/title/tt10796286", "img_src": "https://m.media-amazon.com/images/M/MV5BZGZlNTAwNzgtODUwYy00YjZiLWJlMzctYjFjNDFmYjE3M2ZlXkEyXkFqcGc@._V1_QL75_UX322_.jpg"},
    {"title": "1987", "href": "https://www.imdb.com/title/tt6493286", "img_src": "https://m.media-amazon.com/images/M/MV5BZjU2OTJkNWUtMTBhZi00NDJjLTgwMmYtOGQ3YmQ4ZjE3NWI1XkEyXkFqcGc@._V1_QL75_UX306_.jpg"},
    {"title": "택시운전사", "href": "https://www.imdb.com/title/tt6878038", "img_src": "https://m.media-amazon.com/images/M/MV5BYWU2YzE1YWQtYTNhYi00YTk3LTgxZTMtODA3ZTJkZGU3MWVkXkEyXkFqcGc@._V1_QL75_UX306_.jpg"},
    {"title": "悲兮魔兽", "href": "https://www.imdb.com/title/tt4901304", "img_src": "https://m.media-amazon.com/images/M/MV5BMTQ5MTk5NTgyMV5BMl5BanBnXkFtZTgwNDI0NTY4MDI@._V1_FMjpg_UX1200_.jpg"},
    {"title": "The Death of Stalin", "href": "https://www.imdb.com/title/tt4686844/", "img_src": "https://m.media-amazon.com/images/M/MV5BMTcxMDc1NjcyNl5BMl5BanBnXkFtZTgwNDU0NDYxMzI@._V1_QL75_UX380_CR0,0,380,562_.jpg"}
]

def generate_movie_html(movie_data):
    title = movie_data['title'].replace("'", "&apos;")
    img_url = movie_data['img_src']
    
    # --- 核心改进：如果是豆瓣的图片，使用 weserv 代理绕过防盗链 ---
    if "doubanio.com" in img_url:
        # 去掉协议头，交给 weserv 处理
        clean_url = img_url.replace("https://", "").replace("http://", "")
        img_url = f"https://images.weserv.nl/?url={clean_url}"
    
    placeholder = "https://placehold.co/300x450/1a1a1a/1a1a1a.png"
    
    return f"""
        <a class="film-card" href="{movie_data['href']}" target="_blank">
            <div class="img-wrap">
                <img src="{img_url}" alt="{title}" loading="lazy" 
                     onerror="this.onerror=null;this.src='{placeholder}';">
            </div>
            <div class="info-layer">
                <h3 class="movie-title">{title}</h3>
            </div>
        </a>"""

def fetch_movies(start_counter):
    movie_items_html = ""
    total_movies = 0
    
    print(f"--- 启动抓取: {DOUBAN_ID} ---")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        try:
            # 关键：此处传入带有 Referer 的 headers
            response = requests.get(page_url, headers=DOUBAN_HEADERS, proxies=PROXIES, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[错误] 访问失败: {e}")
            break

        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        movie_list = soup.findAll('div', class_="item")

        if not movie_list:
            print("--- 扫描结束 ---")
            break

        for item in movie_list:
            try:
                img_tag = item.find("img")
                link_tag = item.find("a")
                
                movie_data = {
                    "title": img_tag['alt'],
                    "href": link_tag['href'],
                    "img_src": img_tag['src'],
                }
                movie_items_html += generate_movie_html(movie_data)
                total_movies += 1
            except Exception:
                continue
        
        print(f"已获取 {total_movies} 条记录...")
        time.sleep(random.uniform(2, 4)) # 豆瓣抓取建议间隔长一点，防止封 IP

    return movie_items_html

def write_html_file(content):
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write(HTML_HEAD + content + HTML_FOOT)
    print(f"成功导出: {os.path.abspath(OUTPUT_FILENAME)}")

if __name__ == '__main__':
    if DOUBAN_ID == "your_douban_id_here":
        print("错误: 请先配置环境变量 DOUBAN_ID")
    else:
        # 1. 加载固定内容
        all_content = "".join([generate_movie_html(m) for m in FIXED_MOVIES])
        # 2. 抓取动态内容
        all_content += fetch_movies(start_counter=len(FIXED_MOVIES))
        # 3. 写入文件
        if all_content:
            write_html_file(all_content)
