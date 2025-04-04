import requests as rq
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin, urlunsplit
import sqlite3

second = 0

def clean_url(url):
    parsed = urlsplit(url)
    clean = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))
    return clean

def start_crawling(site, old_site):
    global second
    curs.execute('''SELECT done FROM sites WHERE url = ?''', (site,))
    site_exists = curs.fetchone()
    if site_exists and site_exists[0] == 1:
        return

    blocked_extensions = (
        ".iso", ".img", ".exe", ".zip", ".tar.gz", ".wsl", ".deb", ".bin", ".tar", ".gz", ".bz2",
        ".xz", ".7z", ".rar", ".dmg", ".pkg", ".msi", ".apk", ".appimage", ".rpm", ".pdf", ".doc",
        ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp3", ".mp4", ".avi", ".mov", ".flac", ".wav",
        ".mkv", ".ogg", ".webm", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".ico"
    )

    blocked_sites = ["publishercenter.google.com", "accounts.google.com"]
    blocked_paths = ["/login", "/signup", "/register"]

    if site.endswith(blocked_extensions):
        return
    elif site.startswith("mailto:"):
        return
    elif site.startswith("https://") or site.startswith("http://"):
        parsed = urlsplit(site)
        domain = parsed.netloc
        path = parsed.path
        if domain in blocked_sites:
            return
        if path in blocked_paths:
            return
        curs.execute('''INSERT INTO sites (url, done) VALUES (?, ?)''', (site, 0))
        curs.execute('''SELECT url FROM sites WHERE url = ?''', (site,))
        site_in_db = curs.fetchone()
        print(site_in_db[0])
        try:
            r = rq.get(site)

            if r.status_code >= 400:
                return

            curs.execute('''UPDATE last_site SET url = ? WHERE id = ?''', (site, 1))

            if second == 1:
                curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, old_site))
                conn.commit()
            else:
                second = 1

            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title').string
            curs.execute('''UPDATE sites SET title = ? WHERE url = ?''', (title, site))
            curs.execute('''SELECT title FROM sites WHERE title = ?''', (title,))
            title_in_db = curs.fetchone()
            print(title_in_db[0])
            conn.commit()
            for link in soup.find_all('a'):
                href = link.get('href')
                if not href:
                    return
                else:
                    parsed = urlsplit(site)
                    if href.startswith('/'):
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = f"{parsed.scheme}://{parsed.netloc}" + href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif href.startswith("#"):
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif ".php" in href:
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = f"{parsed.scheme}://{parsed.netloc}" + "/" + href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif href.startswith("http://") or href.startswith("https://"):
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    else:
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
        except Exception as e:
            print("error: site doesn't exist")
    else:
        site = "http://" + site
        parsed = urlsplit(site)
        domain = parsed.netloc
        path = parsed.path
        if domain in blocked_sites:
            return
        if path in blocked_paths:
            return
        curs.execute('''INSERT INTO sites (url, done) VALUES (?, ?)''', (site, 0))
        curs.execute('''SELECT url FROM sites WHERE url = ?''', (site,))
        site_in_db = curs.fetchone()
        print(site_in_db[0])
        try:
            r = rq.get(site)

            if r.status_code >= 400:
                return

            curs.execute('''UPDATE last_site SET url = ? WHERE id = ?''', (site, 1))

            if second == 1:
                curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, old_site))
                conn.commit()
            else:
                second = 1

            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title').string
            curs.execute('''UPDATE sites SET title = ? WHERE url = ?''', (title, site))
            curs.execute('''SELECT title FROM sites WHERE title = ?''', (title,))
            title_in_db = curs.fetchone()
            print(title_in_db[0])
            conn.commit()
            for link in soup.find_all('a'):
                href = link.get('href')
                if not href:
                    return
                else:
                    parsed = urlsplit(site)
                    if href.startswith('/'):
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = f"{parsed.scheme}://{parsed.netloc}" + href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif href.startswith("#"):
                        new_site = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif ".php" in href:
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = f"{parsed.scheme}://{parsed.netloc}" + "/" + href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    elif href.startswith("http://") or href.startswith("https://"):
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
                    else:
                        if "?" in href:
                            href = href.split("?", 1)[0]
                        new_site = href
                        curs.execute('''UPDATE sites SET done = ? WHERE url = ?''', (1, site))
                        conn.commit()
                        start_crawling(new_site, site)
        except Exception as e:
            print(f"error: site doesn't exist")

conn = sqlite3.connect("data.db")
curs = conn.cursor()
curs.execute('''CREATE TABLE IF NOT EXISTS sites (url TEXT, title TEXT, done INTEGER)''')
curs.execute('''CREATE TABLE IF NOT EXISTS last_site (url TEXT, id INTEGER)''')
conn.commit()

curs.execute('''INSERT INTO last_site (id) VALUES (?)''', (1,))

print("Welcome!")
curs.execute('''SELECT url FROM last_site WHERE id = ?''', (1,))
last_url_exists = curs.fetchone()
print(last_url_exists[0])
if last_url_exists and last_url_exists[0]:
    start_crawling(last_url_exists[0], 0)
else:
    ask = input("Which site?")
    start_crawling(ask, None)
conn.close()
