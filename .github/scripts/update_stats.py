import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---
# 建议通过环境变量设置，或直接在此处修改默认值
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")
PAGE_RANGE = range(0, 150, 15)  # 抓取页数范围
OUTPUT_FILENAME = 'index.html'

# 模拟真实浏览器请求，防止被豆瓣反爬虫直接拦截
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DOUBAN_HEADERS = {
    'User-Agent': USER_AGENT,
    'Referer': 'https://movie.douban.com/'
}

# --- HTML 模板 ---
HTML_HEAD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE CINEMA ARCHIVE</title>
    <!-- 关键：禁止浏览器发送 Referer，绕过初级防盗链 -->
    <meta name="referrer" content="no-referrer">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #050505; --text: #e0e0e0; --border: #1f1f1f; --card-min-width: 160px; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
        header { padding: 5rem 2rem 3rem; text-align: left; max-width: 1400px; margin: 0 auto; }
        h1.title { font-family: 'Playfair Display', serif; font-weight: 900; font-size: clamp(2.5rem, 7vw, 5rem); letter-spacing: -0.04em; line-height: 1; text-transform: uppercase; }
        .subtitle { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.3em; color: #666; margin-top: 1.5rem; }
        .archive-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr)); gap: 1px; background-color: var(--border); border-top: 1px solid var(--border); }
        .film-card { position: relative; background-color: var(--bg); aspect-ratio: 2 / 3; overflow: hidden; text-decoration: none; display: block; }
        .img-wrap { width: 100%; height: 100%; transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
        .img-wrap img { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%) contrast(1.1); transition: all 0.7s ease; }
        .film-card:hover .img-wrap { transform: scale(1.05); }
        .film-card:hover img { filter: grayscale(0%) contrast(1); }
        .info-layer { position: absolute; inset: 0; padding: 1.5rem; display: flex; flex-direction: column; justify-content: flex-end; background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent 60%); opacity: 0; transition: opacity 0.4s ease; }
        .film-card:hover .info-layer { opacity: 1; }
        .movie-title { font-size: 0.8rem; color: #fff; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        footer { padding: 6rem 2rem; text-align: center; font-size: 0.65rem; color: #333; letter-spacing: 0.1em; text-transform: uppercase; }
        @media (max-width: 600px) { 
            .archive-grid { grid-template-columns: repeat(2, 1fr); }
            .info-layer { opacity: 1; padding: 0.8rem; background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, transparent 40%); }
            .movie-title { font-size: 0.7rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="title">Cinema<br/>Archive</h1>
        <div class="subtitle">Personal Collection / Edited by Fox</div>
    </header>
    <main class="archive-grid">
"""

HTML_FOOT = """
    </main>
    <footer>Designed and Generated via Python Script</footer>
</body>
</html>
"""

FIXED_MOVIES = [
    {"title": "The Death of Stalin", "href": "https://movie.douban.com/subject/26790933/", "img_src": "https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2495908091.webp"}
]

def generate_movie_html(movie_data):
    title = movie_data['title'].replace("'", "&apos;")
    img_url = movie_data['img_src']
    
    # --- 核心改进：防盗链处理逻辑 ---
    # 逻辑：如果是豆瓣域名，则通过 weserv 代理加载
    if "doubanio.com" in img_url:
        # 清理原 URL 协议头，weserv 能够更好地处理
        raw_url = img_url.split('://')[-1]
        # 使用 weserv 代理，并强制转换为 webp 或高质量 jpg 以提高加载速度
        img_url = f"https://images.weserv.nl/?url={raw_url}&default=ssl:placehold.co/300x450/1a1a1a/1a1a1a.png"
    
    return f"""
        <a class="film-card" href="{movie_data['href']}" target="_blank">
            <div class="img-wrap">
                <img src="{img_url}" alt="{title}" loading="lazy">
            </div>
            <div class="info-layer">
                <h3 class="movie-title">{title}</h3>
            </div>
        </a>"""

def fetch_movies():
    movie_items_html = ""
    total_movies = 0
    
    print(f"[*] 准备抓取用户 ID: {DOUBAN_ID}")

    for i in PAGE_RANGE:
        page_url = f'https://movie.douban.com/people/{DOUBAN_ID}/collect?start={i}&sort=time&rating=all&filter=all&mode=grid'
        try:
            # 必须模拟 Referer 访问豆瓣网页，否则会被拦截
            response = requests.get(page_url, headers=DOUBAN_HEADERS, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"[!] 无法访问页面 {i}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        movie_list = soup.find_all('div', class_="item")

        if not movie_list:
            print(f"[*] 页面 {i} 无内容，可能已抓取完毕。")
            break

        for item in movie_list:
            try:
                img_tag = item.find("img")
                link_tag = item.find("a")
                if not img_tag or not link_tag: continue
                
                movie_data = {
                    "title": img_tag.get('alt', '未知电影'),
                    "href": link_tag.get('href', '#'),
                    "img_src": img_tag.get('src', ''),
                }
                movie_items_html += generate_movie_html(movie_data)
                total_movies += 1
            except Exception as e:
                print(f"[!] 解析条目出错: {e}")
                continue
        
        print(f"[+] 已处理 {total_movies} 部电影...")
        # 豆瓣反爬严格，建议保持 3-6 秒的随机间隔
        time.sleep(random.uniform(3, 6))

    return movie_items_html

if __name__ == '__main__':
    if DOUBAN_ID == "your_douban_id_here":
        print("请在代码开头配置你的 DOUBAN_ID")
    else:
        # 1. 抓取动态内容
        dynamic_content = fetch_movies()
        
        # 2. 合并固定电影内容（如果有的话）
        fixed_content = "".join([generate_movie_html(m) for m in FIXED_MOVIES])
        
        # 3. 写入文件
        if dynamic_content or fixed_content:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(HTML_HEAD + fixed_content + dynamic_content + HTML_FOOT)
            print(f"\n[OK] 页面已生成：{os.path.abspath(OUTPUT_FILENAME)}")
        else:
            print("\n[!] 未抓取到任何内容，请检查 ID 是否正确或是否被豆瓣拦截。")
