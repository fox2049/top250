import requests
from bs4 import BeautifulSoup
import time
import random
import os

# --- 配置区 ---
DOUBAN_ID = os.environ.get("DOUBAN_ID", "your_douban_id_here")
PAGE_RANGE = range(0, 150, 15)
OUTPUT_FILENAME = 'index.html'

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
    <meta name="referrer" content="no-referrer">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #050505; --text: #e0e0e0; --border: #1f1f1f; --card-min-width: 160px; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; line-height: 1.5; }
        header { padding: 5rem 2rem 3rem; text-align: left; max-width: 1400px; margin: 0 auto; }
        h1.title { font-family: 'Playfair Display', serif; font-weight: 900; font-size: clamp(2.5rem, 7vw, 5rem); letter-spacing: -0.04em; line-height: 1; text-transform: uppercase; }
        .subtitle { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.3em; color: #666; margin-top: 1.5rem; }
        .archive-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--card-min-width), 1fr)); gap: 1px; background-color: var(--border); border-top: 1px solid var(--border); }
        .film-card { position: relative; background-color: var(--bg); aspect-ratio: 2 / 3; overflow: hidden; text-decoration: none; display: block; }
        .img-wrap { width: 100%; height: 100%; transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); background-color: #111; }
        .img-wrap img { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%) contrast(1.1); transition: all 0.7s ease; opacity: 0; }
        .img-wrap img.loaded { opacity: 1; }
        .film-card:hover .img-wrap { transform: scale(1.05); }
        .film-card:hover img { filter: grayscale(0%) contrast(1); }
        .info-layer { position: absolute; inset: 0; padding: 1.5rem; display: flex; flex-direction: column; justify-content: flex-end; background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent 60%); opacity: 0; transition: opacity 0.4s ease; }
        .film-card:hover .info-layer { opacity: 1; }
        .movie-title { font-size: 0.8rem; color: #fff; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        footer { padding: 6rem 2rem; text-align: center; font-size: 0.65rem; color: #333; letter-spacing: 0.1em; text-transform: uppercase; }
        @media (max-width: 600px) { 
            .archive-grid { grid-template-columns: repeat(3, 1fr); }
            .info-layer { display: none; }
        }
    </style>
</head>
<body>
    <header>
        <h1 class="title">Cinema<br/>Archive</h1>
        <div class="subtitle">Personal Collection / Managed by Fox</div>
    </header>
    <main class="archive-grid">
"""

# 在底部加入一段简单的 JS，用于在主代理失效时尝试备用方案，并处理图片加载状态
HTML_FOOT = """
    </main>
    <footer>Designed and Generated via Python Script</footer>
    <script>
        document.querySelectorAll('.img-wrap img').forEach(img => {
            img.onload = () => img.classList.add('loaded');
            
            // 如果当前的代理地址加载失败，尝试换一个代理
            img.onerror = function() {
                const originalUrl = this.getAttribute('data-original');
                if (!originalUrl) return;
                
                console.log('正在尝试备用代理: ' + originalUrl);
                // 方案 2: 使用 images.weserv.nl 的另一种格式
                const fallback = 'https://images.weserv.nl/?url=' + encodeURIComponent(originalUrl);
                
                if (this.src !== fallback) {
                    this.src = fallback;
                } else {
                    // 如果都失败了，显示占位图
                    this.src = 'https://placehold.co/300x450/1a1a1a/555?text=Image+Error';
                    this.onerror = null;
                }
            };
            
            // 触发加载
            if (img.complete) img.onload();
        });
    </script>
</body>
</html>
"""

def generate_movie_html(movie_data):
    title = movie_data['title'].replace("'", "&apos;")
    original_img = movie_data['img_src']
    
    # 方案 1: 默认使用 WordPress 的 Photon 代理，因为它对豆瓣图片的兼容性目前较好
    # 格式：https://i0.wp.com/{url_without_protocol}
    if "doubanio.com" in original_img:
        clean_url = original_img.replace("https://", "").replace("http://", "")
        proxy_url = f"https://i0.wp.com/{clean_url}"
    else:
        proxy_url = original_img
    
    return f"""
        <a class="film-card" href="{movie_data['href']}" target="_blank">
            <div class="img-wrap">
                <img src="{proxy_url}" 
                     data-original="{original_img}"
                     alt="{title}" 
                     loading="lazy"
                     referrerpolicy="no-referrer">
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
            response = requests.get(page_url, headers=DOUBAN_HEADERS, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"[!] 无法访问页面 {i}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        movie_list = soup.find_all('div', class_="item")

        if not movie_list:
            print(f"[*] 页面 {i} 无内容，或已触发表单验证。")
            break

        for item in movie_list:
            try:
                img_tag = item.find("img")
                link_tag = item.find("a")
                if not img_tag or not link_tag: continue
                
                movie_data = {
                    "title": img_tag.get('alt', '未知电影'),
                    "href": link_tag.get('href', '#'),
                    "img_src": img_tag.get('src', '').replace('s_ratio_poster', 'm_ratio_poster'), # 尝试使用中等尺寸图片，有时比小图更容易通过检测
                }
                movie_items_html += generate_movie_html(movie_data)
                total_movies += 1
            except Exception as e:
                print(f"[!] 解析条目出错: {e}")
                continue
        
        print(f"[+] 已处理 {total_movies} 部电影...")
        time.sleep(random.uniform(3, 7))

    return movie_items_html

if __name__ == '__main__':
    if DOUBAN_ID == "your_douban_id_here":
        print("请在代码开头配置你的 DOUBAN_ID")
    else:
        content = fetch_movies()
        if content:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(HTML_HEAD + content + HTML_FOOT)
            print(f"\n[OK] 页面已生成：{os.path.abspath(OUTPUT_FILENAME)}")
        else:
            print("\n[!] 未能抓取到内容，请检查豆瓣 ID 是否正确，或尝试在浏览器中登录豆瓣后再运行。")
