import random
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
import requests
import random

import aiohttp
import datetime
import logging

from bs4 import BeautifulSoup as BS

def random_ip():
    ips = ['46.227.123.', '37.110.212.', '46.255.69.', '62.209.128.', '37.110.214.', '31.135.209.', '37.110.213.']
    prefix = random.choice(ips)
    return prefix + str(random.randint(1, 255))


app = FastAPI()


@app.get("/instagram/", response_model=dict)
async def instagram(url: str):
    result = []
    data = {'q': url, 'vt': 'home'}
    headers = {
        'origin': 'https://snapinsta.io',
        'referer': 'https://snapinsta.io/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'X-Forwarded-For': random_ip(),
        'X-Client-IP': random_ip(),
        'X-Real-IP': random_ip(),
        'X-Forwarded-Host': 'snapinsta.io'
    }
    base_url = 'https://snapinsta.io/api/ajaxSearch'
    response = requests.post(base_url, data=data, headers=headers)
    jsonn = response.json()
    try:

        if jsonn['status'] == 'ok':
            data = jsonn['data']
            soup = BS(data, 'html.parser')
            for i in soup.find_all('div', class_='download-items__btn'):
                url = i.find('a')['href']
                type_text = i.get_text().strip()
                if 'Download Video' in type_text:
                    result.append({'url': url, "type": 'Video'})
                elif 'Download Image' in type_text:
                    result.append({'url': url, "type": 'Image'})
            RES = {'status': True, 'result': result}
            return jsonable_encoder(RES)
        else:
            raise HTTPException(status_code=404, detail='Error')
    except Exception as err:
        return {"error": "This video is private"}


@app.post("/pinterest/")
async def get_pinterest_info(link: str):
    try:
        url = 'https://ssspinterest.com/'
        header = {
            'Origin': 'https://ssspinterest.com',
            'Referer': 'https://ssspinterest.com/',
            'Sec-Ch-Ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit'/537.36 (KHTML, like Gecko) Chrome'/112.0.0.0 Mobile Safari'/537.36"
        }
        d = {
            'url': link
        }

        r = requests.post(url, headers=header, data=d)
        r.raise_for_status()  # Raise exception for HTTP errors
        soup = BS(r.text, 'html.parser')
        b = soup.select_one("#quality_1 > option:nth-child(2)")
        a = soup.find("div", class_="download-items")
        if a is not None:
            test = a.text
            i = a.a.get("href")
        else:
            raise HTTPException(status_code=404, detail="Data not found on the page")

        if b is not None:
            result = b["value"]
        else:
            result = i

        return {"result": result}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error in the external request")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_mp3_url_yt(youtube_url):
    api_url = 'https://yt5s.io/api/ajaxSearch'
    data = {
        'q': youtube_url,
        'vt': 'mp3'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, data=data, headers={'X-Requested-With': 'XMLHttpRequest'}) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"Xatolik yuz berdi: {response.status}")


async def get_all_mp3_urls(data):
    base_url = 'https://ve44.aadika.xyz/download/'
    video_id = data['vid']
    time_expires = data['timeExpires']
    token = data['token']
    mp3_info_dict = {}

    for index, (quality, info) in enumerate(data['links']['mp3'].items(), start=1):
        if info['f'] == 'mp3':
            mp3_info = {
                'title': data['title'],
                'format': info['k'],
                'q': info['q'],
                'size': info['size'],
                'key': info['key'],
                'url': f"{base_url}{video_id}/mp3/{info['k']}/{time_expires}/{token}/{index}?f=yt5s.io"
            }
            mp3_info_dict[index] = mp3_info

    return mp3_info_dict


@app.get("/youtube/download/audio/", status_code=status.HTTP_200_OK, description="Download audio from Youtube",
         tags=['youtube'])
async def youtube_audio_url(url: str):
    if not url:
        logging.error(f"{datetime.datetime.now()} - No url provided")
        return {"status": False, "message": "No url provided"}
    else:
        try:
            result = await get_mp3_url_yt(url)
            if result['mess'] == "":
                res = await get_all_mp3_urls(result)
                return {"status": True, "result": res}
            else:
                return {"status": False, "message": "Something went wrong"}

        except Exception as e:
            logging.error(f"{datetime.datetime.now()} - {e}")
            return {"status": False, "message": "Something went wrong"}
