import requests
from bs4 import BeautifulSoup
import re
import time
import os

BASE = "https://www.kerenkw12.com"
LIST_URL = "https://www.kerenkw12.com/2021/03/mahabharata-bahasa-indonesia-full-episod.html?m=1"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_episode_links():
    res = requests.get(LIST_URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "mahabharata-episode" in href:
            if href.startswith("/"):
                href = BASE + href

            links.append(href)

    return sorted(list(set(links)))


def extract_drive_id(url):
    match = re.search(r'/d/(.*?)/', url)
    if match:
        return match.group(1)
    return None


def get_drive_link(episode_url):
    try:
        res = requests.get(episode_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # iframe
        iframe = soup.find("iframe")
        if iframe:
            src = iframe.get("src", "")
            if "drive.google.com" in src:
                return src

        # fallback
        for a in soup.find_all("a", href=True):
            if "drive.google.com" in a["href"]:
                return a["href"]

    except:
        return None


def convert_to_stream(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def main():
    episodes = get_episode_links()
    print("Total episode:", len(episodes))

    results = []

    for i, ep in enumerate(episodes, 1):
        print(f"[{i}] {ep}")

        drive_url = get_drive_link(ep)

        if drive_url:
            file_id = extract_drive_id(drive_url)

            if file_id:
                stream = convert_to_stream(file_id)
                results.append((i, stream))
                print("  ✔ OK")
            else:
                print("  ✖ No ID")
        else:
            print("  ✖ No Drive")

        time.sleep(1)

    # buat folder output
    os.makedirs("output", exist_ok=True)

    # buat m3u
    with open("output/playlist.m3u", "w") as f:
        f.write("#EXTM3U\n")

        for ep, link in results:
            f.write(f"#EXTINF:-1, Mahabharata Episode {ep}\n")
            f.write(link + "\n")

    print("DONE → output/playlist.m3u")


if __name__ == "__main__":
    main()
