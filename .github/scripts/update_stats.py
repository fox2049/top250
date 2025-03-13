# from socket import SO_USELOOPBACK
from requests import get
from bs4 import BeautifulSoup
import time
import random

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'


li = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>my top250</title>
    <style>
      div.img {
        border: 1px solid #ccc;
      }

      div.img:hover {
        border: 1px solid #777;
      }

      div.img img {
        width: 100%;
        aspect-ratio: 1/1.47;
      }

      div.desc {
        padding: 15px;
        text-align: center;
      }

      * {
        box-sizing: border-box;
      }

      .responsive {
        padding: 0 6px;
        float: left;
        width: 4.99999%;
        margin: 6px 0;
      }

      @media only screen and (max-width: 2000px) {
        .responsive {
          width: 9.99999%;
          margin: 6px 0;
        }
      }

      @media only screen and (max-width: 1000px) {
        .responsive {
          width: 19.99999%;
          margin: 6px 0;
        }
      }

      @media only screen and (max-width: 500px) {
        .responsive {
          width: 24.99999%;
          margin: 6px 0;
        }
      }

      .clearfix:after {
        content: "";
        display: table;
        clear: both;
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

    <div style="padding: 6px">
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
