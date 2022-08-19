import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pathlib


start_url = 'https://www.marktstammdatenregister.de/MaStR/Datendownload'
r = requests.get(start_url)

if r.status_code != 200:
    r.raise_for_status()
    raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
else:
    doc = BeautifulSoup(r.content, 'html.parser')
    for btn in doc.find_all(name='a', class_="btn-primary"):
        if btn.get('title') == 'Download':
            r2 = requests.get(btn.get('href'), stream=True)
            if r2.status_code != 200:
                r2.raise_for_status()
                raise RuntimeError(f"Request to {url} returned status code {r2.status_code}")
            else:
                file_size = max(int(r2.headers.get('Content-Length', 0)), 100000) # roughly 1 GB in 10 mb splits
                pathlib.Path('data/').mkdir(parents=True, exist_ok=True)

            with open('data/mastr-download.zip', 'wb') as fd:
                for chunk in tqdm(r2.iter_content(chunk_size=10048), total=file_size):
                    fd.write(chunk)