import requests as rq
from bs4 import BeautifulSoup
import time
from urllib.parse import urlsplit
import sqlite3

def start_crawling(site):
    blocked_extensions = (
        ".iso", ".img", ".exe", ".zip", ".tar.gz", ".wsl", ".deb", ".bin", ".tar", ".gz", ".bz2",
        ".xz", ".7z", ".rar", ".dmg", ".pkg", ".msi", ".apk", ".appimage", ".rpm", ".pdf", ".doc",
        ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp3", ".mp4", ".avi", ".mov", ".flac", ".wav",
        ".mkv", ".ogg", ".webm", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".ico"
    )

    if site.endswith(blocked_extensions):
        return
    elif site.startswith("mailto:"):
        return
    elif site.startswith("https://") or site.startswith("http://"):
        curs.execute('''SELECT url FROM sites WHERE url = ?''', (site,))
        site_exists = curs.fetchone()
        if site_exists:
            return
        print(site)
        try:
            r = rq.get(site)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title').string
            curs.execute('''INSERT INTO sites (url, title) VALUES (?, ?)''', (site, title))
            conn.commit()
            print(title)
            for link in soup.find_all('a'):
                if link.get('href').startswith('/'):
                    parsed = urlsplit(site)
                    new_site = f"{parsed.scheme}://{parsed.netloc}" + link.get('href')
                    start_crawling(new_site)
                    #time.sleep(0.05)
                else:
                    start_crawling(link.get('href'))
                    #time.sleep(0.05)
        except Exception as e:
            print("error: site doesn't exist")
    else:
        site = "http://" + site
        curs.execute('''SELECT url FROM sites WHERE url = ?''', (site,))
        site_exists = curs.fetchone()
        if site_exists:
            return
        print(site)
        try:
            r = rq.get(site)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title').string
            curs.execute('''INSERT INTO sites (url, title) VALUES (?, ?)''', (site, title))
            conn.commit()
            print(title)
            for link in soup.find_all('a'):
                if link.get('href').startswith('/'):
                    parsed = urlsplit(site)
                    new_site = f"{parsed.scheme}://{parsed.netloc}" + link.get('href')
                    start_crawling(new_site)
                    #time.sleep(0.05)
                else:
                    start_crawling(link.get('href'))
                    #time.sleep(0.05)
        except Exception as e:
            print(f"error: site doesn't exist")

conn = sqlite3.connect("data.db")
curs = conn.cursor()
curs.execute('''CREATE TABLE IF NOT EXISTS sites (url TEXT, title TEXT)''')
conn.commit()

print("Welcome!")
ask = input("Which site?")
start_crawling(ask)