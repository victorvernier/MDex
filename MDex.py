import os
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time

API_BASE = "https://api.mangadex.org"
DOWNLOAD_DIR = 'Downloads'
MAX_RETRIES = 3

def search_manga(title):
    """Searches for the manga by title and returns the ID of the best result."""
    params = {"title": title, "limit": 10}
    resp = requests.get(f"{API_BASE}/manga", params=params)
    resp.raise_for_status()
    data = resp.json()

    if data["data"]:
        best_match = None
        best_score = 0
        similar_matches = []
        for manga in data["data"]:
            for title_lang in manga["attributes"]["title"].values():
                score = fuzz.ratio(title.lower(), title_lang.lower())
                if score > best_score:
                    best_score = score
                    best_match = manga
                if score >= 60:  # Lists similar results
                    similar_matches.append((score, manga["attributes"]["title"]["en"]))

        if best_match and best_score >= 60:
            print(f"Manga found: {best_match['attributes']['title']['en']}")
            return best_match["id"]
        elif similar_matches:
            print(f"No manga found with the exact name '{title}'. Similar results:")
            for score, manga_title in sorted(similar_matches, reverse=True):
                print(f"- {manga_title} (similarity: {score}%)")
            return None

    print(f"No manga found with the name: {title}")
    return None

def get_chapters(manga_id, lang="pt-br"):
    """Gets the list of available chapters for the manga in a specific language."""
    chapters = []
    offset = 0
    limit = 100
    while True:
        params = {
            "manga": manga_id,
            "translatedLanguage[]": lang,
            "order[chapter]": "asc",
            "limit": limit,
            "offset": offset
        }
        resp = requests.get(f"{API_BASE}/chapter", params=params)
        resp.raise_for_status()
        data = resp.json()

        if not data["data"]:
            break
        for item in data["data"]:
            chap_id = item["id"]
            chap_number = item["attributes"].get("chapter", "N/A")
            chapters.append({"id": chap_id, "number": chap_number})

        offset += limit
    return chapters

def download_image(img_url, img_path):
    """Downloads an image from a URL and saves it to the specified path with retry."""
    for attempt in range(MAX_RETRIES):
        try:
            img_resp = requests.get(img_url, stream=True)
            img_resp.raise_for_status()
            with open(img_path, 'wb') as f:
                for chunk in img_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Error downloading {img_url}, trying again ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(2)
            else:
                print(f"Failed to download {img_url} after {MAX_RETRIES} attempts: {e}")
                return False
    return False

def download_chapter_images(chapter_id, save_folder, chapter_number):
    """Downloads all images from a specific chapter."""
    server_resp = requests.get(f"{API_BASE}/at-home/server/{chapter_id}")
    server_resp.raise_for_status()
    server_data = server_resp.json()
    base_url = server_data["baseUrl"]
    chapter = server_data["chapter"]
    hash_val = chapter["hash"]
    data_files = chapter["data"]

    chapter_path = os.path.join(save_folder, f"Capítulo {chapter_number}")
    os.makedirs(chapter_path, exist_ok=True)

    img_paths = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for idx, img_file in enumerate(data_files):
            if img_file.lower().endswith(('.jpg', '.jpeg')):
                img_path = os.path.join(chapter_path, f"{idx+1:03d}.jpg")
                if not os.path.exists(img_path):
                    img_url = f"{base_url}/data/{hash_val}/{img_file}"
                    futures.append(executor.submit(download_image, img_url, img_path))
                    img_paths.append(img_path)
                else:
                    img_paths.append(img_path)
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Downloading images"):
            pass
    return img_paths, chapter_path

def main():
    """Main function that executes the manga search and download process."""
    while True:
        title = input("Enter the manga name: ").strip()
        manga_id = search_manga(title)
        if manga_id:
            chapters = get_chapters(manga_id)
            if not chapters:
                print("No chapters available in Portuguese.")
                continue

            print("\nAvailable Chapters:")
            for chap in chapters:
                print(f"Chapter {chap['number']}")

            choice = input("Enter the chapter number(s) to download (separated by spaces, or 'all' for all): ").strip()

            selected = []
            if choice.lower() == 'all':
                selected = chapters
            else:
                try:
                    chapter_numbers = choice.split()
                    selected = [chap for chap in chapters if chap['number'] in chapter_numbers]
                    if not selected:
                        raise ValueError("Chapter(s) not found.")
                except ValueError as e:
                    print(f"Invalid selection: {e}")
                    continue

            os.makedirs(DOWNLOAD_DIR, exist_ok=True)

            for chap in selected:
                print(f"\nDownloading Chapter {chap['number']}")
                try:
                    download_chapter_images(chap["id"], DOWNLOAD_DIR, chap["number"])
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading chapter {chap['number']}: {e}")

            while True:
                option = input("\nSearch again (1) or Close Program (2)? ")
                if option == '1':
                    break
                elif option == '2':
                    return
                else:
                    print("Invalid option. Enter 1 or 2.")
        else:
            print("Try again. Manga not found.")

if __name__ == "__main__":
    main()
