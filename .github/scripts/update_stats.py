# from socket import SO_USELOOPBACK
from requests import get
from bs4 import BeautifulSoup
import time
import random

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'


# li = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>My Top 250 Movies</title> <style>
      /* 全局样式设置 */
      body {
        font-family: Arial, sans-serif; /* 更现代的字体 */
        margin: 0; /* 移除 body 默认 margin */
        padding: 20px; /* 增加 body 内边距，页面内容不紧贴浏览器边缘 */
        background-color: #f4f4f4; /* 浅灰色背景 */
        color: #333; /* 深灰色文字颜色 */
        line-height: 1.6; /* 行高 */
      }

      h2 {
        text-align: center;
        color: #333; /* 标题颜色 */
        margin-bottom: 30px; /* 标题下方间距 */
        margin-top: 20px; /* 标题上方间距 */
        font-weight: bold; /* 标题加粗 */
      }

      /* 图片容器样式 */
      div.img {
        /* 移除边框 */
        /* border: 1px solid #ccc; */
        overflow: hidden; /* 确保 hover 放大效果不超出容器 */
        background-color: #fff; /* 图片容器背景白色 */
        border-radius: 8px; /* 圆角边框 */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* 轻微阴影 */
        transition: transform 0.3s ease; /* 添加过渡效果，使 hover 效果更平滑 */
      }

      div.img:hover {
        /* border: 1px solid #777; */ /* 移除 hover 边框 */
        transform: scale(1.05); /* hover 时 हल्का放大 */
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); /* hover 时阴影更明显 */
      }

      div.img img {
        width: 100%;
        aspect-ratio: 1 / 1.47;
        display: block; /* 移除图片下方默认间隙 */
        border-radius: 8px 8px 0 0; /* 图片上方圆角 */
      }

      /* 描述文字样式 */
      div.desc {
        padding: 15px;
        text-align: center;
        font-size: 14px; /* 描述文字字号 */
        color: #555; /* 描述文字颜色 */
      }

      /* 清除浮动 */
      .clearfix:after {
        content: "";
        display: table;
        clear: both;
      }

      /* 响应式列布局 */
      .responsive {
        padding: 0 6px;
        float: left;
        width: 4.99999%;
        margin: 6px 0;
      }

      /* 大屏幕 (大于 2000px) */
      @media only screen and (max-width: 2000px) {
        .responsive {
          width: 9.99999%; /* 每行 10 列 */
          margin: 6px 0;
        }
      }

      /* 中等屏幕 (大于 1000px) */
      @media only screen and (max-width: 1000px) {
        .responsive {
          width: 19.99999%; /* 每行 5 列 */
          margin: 6px 0;
        }
      }

      /* 小屏幕 (大于 500px) */
      @media only screen and (max-width: 500px) {
        .responsive {
          width: 24.99999%; /* 每行 4 列 */
          margin: 6px 0;
        }
      }

      /* 超小屏幕 (小于 500px) 可以考虑一行一列，这里保持原状，您可以根据需要调整 */

      /* 页脚样式 */
      .footer {
        text-align: center;
        padding: 20px 0;
        font-size: 14px;
        color: #777; /* 页脚文字颜色 */
        border-top: 1px solid #eee; /* 页脚上方添加分割线 */
        margin-top: 30px; /* 页脚上方外边距 */
      }
    </style>
  </head>
  <body>
    <h2 style="text-align: center">My Movie Top 250</h2>
"""

insert_content = """
<div class="responsive"><div class="img"><a title='Дорогие товарищи!' target="_blank" href='https://www.imdb.com/title/tt10796286'>\n <img src='https://m.media-amazon.com/images/M/MV5BOWNjYmM0MTYtZDA1My00ZTdhLWFkODktMDdlNTc5MTI5OGRhXkEyXkFqcGdeQXVyODc0OTEyNDU@._V1_FMjpg_UX394_.jpg' alt='Дорогие товарищи!' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n
<div class="responsive"><div class="img"><a title='1987' target="_blank" href='https://www.imdb.com/title/tt6493286'>\n <img src='https://m.media-amazon.com/images/M/MV5BY2U1YWQwNTItNDJlZC00NDYyLWE5NGMtMDU1MjIwZTFiZmYwXkEyXkFqcGdeQXVyNTQ0NTUxOTA@._V1_FMjpg_UX1000_.jpg' alt='1987' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n
<div class="responsive"><div class="img"><a title='택시운전사' target="_blank" href='https://www.imdb.com/title/tt6878038'>\n <img src='https://m.media-amazon.com/images/M/MV5BMDA4NmRiMzQtZTI5My00YWExLTgzZTItNGRiZjYyYjcwNTY3XkEyXkFqcGdeQXVyMTA4NjE0NjEy._V1_FMjpg_UY452_.jpg' alt='택시운전사' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n
<div class="responsive"><div class="img"><a title='悲兮魔兽' target="_blank" href='https://www.imdb.com/title/tt4901304'>\n <img src='https://m.media-amazon.com/images/M/MV5BMTQ5MTk5NTgyMV5BMl5BanBnXkFtZTgwNDI0NTY4MDI@._V1_FMjpg_UX1200_.jpg' alt='悲兮魔兽' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n
<div class="responsive"><div class="img"><a title='The Death of Stalin' target="_blank" href='https://www.imdb.com/title/tt4686844/'>\n <img src='https://m.media-amazon.com/images/M/MV5BMTcxMDc1NjcyNl5BMl5BanBnXkFtZTgwNDU0NDYxMzI@._V1_QL75_UX380_CR0,0,380,562_.jpg' alt='The Death of Stalin' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n
"""
for i in range(1, 251, 15):
    # 加入td
    page_url = f'https://movie.douban.com/people/61283490/collect?start={i}'
    response = get(page_url, proxies={'http': '210.5.10.87:53281'}, headers={
                'User-Agent': ua})
    data = response.content.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    s = soup.findAll('div', class_="item")

    # 加入间隔
    pause_time = random.randint(5, 10)
    print(pause_time, "...")
    time.sleep(pause_time)

    # 提取数据
    for index, item in enumerate(s):
        counter = i + index + 5
        try:
            item_url = item.find("a")['href']
            img_url = item.find("img")['src']
            item_title = item.find("a")['title']
            print(f'{counter}-{item_title}')
            item_info = f"""<div class="responsive"><div class="img"><a title='{item_title}' target="_blank" href='{item_url}'>\n <img src='{img_url}' alt='{item_title}' referrerPolicy='no-referrer' width="196" height="auto" /> </a> </div> </div>\n"""
            insert_content += item_info
        except Exception as e:
            print("!!!" + counter + "error")

insert_content += """
<div class="clearfix"></div>

    <div class="footer">
      <h4>含哺而熙，鼓腹而游 @ 2025</h4>
    </div>
  </body>
</html>
"""

with open(r'index.html', 'w', encoding='utf-8') as f:
    f.seek(0)
    try:
        f.write(li)
        f.write(insert_content)
    except Exception as e:
        print(e)
