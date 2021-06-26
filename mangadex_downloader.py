from typing import Optional
import requests
import json
from time import sleep
from pathlib import Path
import logging
import argparse
import os
import glob

from volumes_to_cbz import folder_to_cbz

BASE_URI = "https://api.mangadex.org"
QUALITY_MODE = "data"

def get_chapters(manga_id, limit=500):
    res = requests.get(f"https://api.mangadex.org/manga/{manga_id}/feed?limit={limit}&translatedLanguage[]=en").json()
    return res

def download_single_image(source_filename, at_home_url, chapter_hash, dest_filename, attempts = 0):
    try:
        with open(f"{dest_filename}", "wb") as dest_file:
            res = requests.get(f"{at_home_url}/{QUALITY_MODE}/{chapter_hash}/{source_filename}")
            dest_file.write(res.content)
            sleep(0.5)
            return True
    except Exception:
        sleep(10)
        attempts += 1
        if attempts > 5:
            logging.error("couldn't download image, skipping")
            return False
        return download_single_image(source_filename, at_home_url, chapter_hash, dest_filename, attempts)

def download_single_chapter(chapter_id, destination_path):
    chapter = requests.get(f"{BASE_URI}/chapter/{chapter_id}").json()
    logging.debug(chapter)
    at_home_id = chapter["data"]["id"]
    files = chapter["data"]["attributes"]["data"]
    chapter_hash = chapter["data"]["attributes"]["hash"]
    server = requests.get(f"{BASE_URI}/at-home/server/{chapter_id}").json()
    logging.debug(server)
    at_home_url = server["baseUrl"]
    for index, filename in enumerate(files):
        if f"{destination_path}_{index}.png" in glob.glob(destination_path + '*.png'):
            print("file already in place, skipping")
        else:
            download_single_image(filename, at_home_url, chapter_hash, f"{destination_path}_{index}.png")
            

    
def download_chapter(id):
    return requests.get(f"{BASE_URI}/{id}")

def get_title(manga_id):
    res = requests.get(f"{BASE_URI}/manga/{manga_id}")
    return res.json()['data']['attributes']['title']['en']

def clean_string(string):
    symbols = [" ", ",", "'", "\""]
    for symbol in symbols:
        string = string.replace(symbol, "")
    return string

def get_volumes_in_folder(folder):
    pass

def download_all_chapters(manga_id, fpath, limit_volumes = [], start_chapter=None, end_chapter=None):
    manga_title = clean_string(get_title(manga_id))
    chapters_response = get_chapters(manga_id)["results"]
    logging.debug(chapters_response)
    chapters = {}
    for chapter in chapters_response:
        logging.debug(chapter)
        chapter_data = chapter['data']
        chapter_id = chapter_data['id']
        volume = chapter_data["attributes"]["volume"]
        chapter = chapter_data["attributes"]["chapter"]
        title = chapter_data["attributes"]["title"]
        chapters[chapter_id] = {
            'volume' : volume,
            'chapter' : chapter,
            'title' : title,
            'id' : chapter_id,
            'manga_title' : manga_title
        }
        
        if limit_volumes and volume not in limit_volumes:
            continue
        if start_chapter and int(float(chapter)) < int(start_chapter):
            continue
        if end_chapter and int(float(chapter)) > int(end_chapter):
            continue

        volume = volume or "oneshot"
        dest = f"{fpath}/{manga_title}/volume_{volume}"
        Path(dest).mkdir(parents=True, exist_ok=True)
        destination = f"{dest}/{chapter}"
        if not glob.glob(destination + '*.png'):
            with open(f"{dest}/chapter_{chapter}_metadata.json", "w") as metadata:
                metadata.write(json.dumps(chapters[chapter_id]))
            download_single_chapter(chapter_id, destination)
        print(f"downloaded chapter Vol. {volume}, chapter: {chapter}")
    folder_to_cbz(fpath)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a full manga from MangaDex")
    parser.add_argument('--manga_id', help="the id part of the manga", required=True)
    parser.add_argument('--path', help="output directory", required=True)
    parser.add_argument('--volumes', nargs="+", help="download only these volumes (format 1 2 3 4)", required=False)
    parser.add_argument('--start_chapter', help="download starting from this chapter", required=False)
    parser.add_argument('--end_chapter', help="download up to this chapter", required=False)
    parser.add_argument('--quality', help="data saver mode", default="data")
    args = parser.parse_args()
    if args.quality == "datasaver":
        QUALITY_MODE = "data-saver"
    download_all_chapters(args.manga_id, args.path, args.volumes or [], args.start_chapter or None, args.end_chapter or None)
