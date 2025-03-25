#MDex.py
import os
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time
import argparse
from PIL import Image
from fpdf import FPDF

# Global Configurations
API_BASE = "https://api.mangadex.org"
DOWNLOAD_BASE_DIR = 'Downloads'
MAX_RETRIES = 3
MAX_THREADS = 4  # Valor padrão mais conservador para respeitar os limites
CHAPTER_DOWNLOAD_DELAY = 0.5 # Delay entre o download de capítulos (em segundos)

def search_manga(title):
    """Searches for a manga by title and returns the ID and formatted name for saving."""
    params = {"title": title, "limit": 10}
    try:
        resp = requests.get(f"{API_BASE}/manga", params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error searching for manga: {e}")
        return None, None

    data = resp.json()
    if not data["data"]:
        print(f"No manga found with the name: {title}")
        return None, None

    best_match = None
    best_score = 0
    similar_matches = []

    for manga in data["data"]:
        for title_lang in manga["attributes"]["title"].values():
            score = fuzz.ratio(title.lower(), title_lang.lower())
            if score > best_score:
                best_score = score
                best_match = manga
            if score >= 60:
                similar_matches.append((score, manga["attributes"]["title"].get("en", "Unknown"), manga["id"]))

    if best_match and best_score >= 60:
        manga_title = best_match["attributes"]["title"].get("en", "Unknown")
        print(f"📚 Manga found: {manga_title}")
        return best_match["id"], manga_title.replace(' ', '_').replace(':', '')

    print(f"No exact match found for '{title}'. Similar results:")
    for score, manga_title, manga_id in sorted(similar_matches, reverse=True):
        print(f"🔹 {manga_title} (similarity: {score}%)")

    return None, None

def get_chapters(manga_id, lang="pt-br"):
    """Returns a list of available chapters in the specified language."""
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
        try:
            resp = requests.get(f"{API_BASE}/chapter", params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error searching for chapters: {e}")
            return []

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
    """Downloads an image with retry attempts in case of error."""
    for attempt in range(MAX_RETRIES):
        try:
            img_resp = requests.get(img_url, stream=True, timeout=15)
            img_resp.raise_for_status()
            with open(img_path, 'wb') as f:
                for chunk in img_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.RequestException as e:
            print(f"Error downloading {img_url}, attempt {attempt + 1}/{MAX_RETRIES}...")
            time.sleep(2)
    print(f"⚠️ Failed to download {img_url}")
    return False

def download_chapter_images(chapter_id, save_folder, chapter_number):
    """Downloads all images from a chapter and returns the list of image paths."""
    try:
        server_resp = requests.get(f"{API_BASE}/at-home/server/{chapter_id}", timeout=10)
        server_resp.raise_for_status()
        server_data = server_resp.json()
    except requests.RequestException as e:
        print(f"Error searching for image server: {e}")
        return []

    base_url = server_data["baseUrl"]
    chapter = server_data["chapter"]
    hash_val = chapter["hash"]
    data_files = chapter["data"]

    chapter_path = os.path.join(save_folder, f"Chapter_{chapter_number}_images") # Temporary folder for images
    os.makedirs(chapter_path, exist_ok=True)

    img_paths = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for idx, img_file in enumerate(data_files):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(chapter_path, f"{idx+1:03d}.jpg")
                if not os.path.exists(img_path):
                    img_url = f"{base_url}/data/{hash_val}/{img_file}"
                    futures.append(executor.submit(download_image, img_url, img_path))
                img_paths.append(img_path)

        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"🖼️ Downloading images for Chapter {chapter_number}"):
            pass
    return sorted(img_paths), chapter_path

def create_pdf(image_paths, output_path):
    """Cria um PDF com orientação automática por página e ajusta a largura da imagem."""
    if not image_paths:
        return False
    try:
        pdf = FPDF()

        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                width, height = img.size

                # Determina a orientação com base na proporção da imagem
                orientation = 'P' if height > width else 'L'
                pdf.add_page(orientation=orientation)

                # Ajusta a largura da imagem para a largura da página, mantendo a proporção
                page_width = pdf.w_pt
                img_ratio = width / height
                new_width = page_width
                new_height = new_width / img_ratio

                # Se a nova altura for maior que a altura da página, ajusta pela altura
                page_height = pdf.h_pt
                if new_height > page_height:
                    new_height = page_height
                    new_width = new_height * img_ratio

                # Centraliza a imagem na página
                x_pos = (page_width - new_width) / 2
                y_pos = (page_height - new_height) / 2

                pdf.image(img_path, x=x_pos, y=y_pos, w=new_width, h=new_height)

            except Exception as e:
                print(f"Erro ao adicionar imagem {img_path} ao PDF: {e}")

        pdf.output(output_path, "F")
        return True
    except Exception as e:
        print(f"Erro ao criar PDF {output_path}: {e}")
        return False

def select_chapters_by_range(chapters, start_chapter, end_chapter):
    """Selects chapters within a specified range."""
    selected_chapters = []
    for chap in chapters:
        try:
            chapter_num = float(chap['number'])
            if start_chapter <= chapter_num <= end_chapter:
                selected_chapters.append(chap)
        except ValueError:
            pass
    return selected_chapters

def is_valid_chapter_number(chapter_str):
    """Checks if a chapter string is a valid positive number or 'all'."""
    if chapter_str.lower() == 'all':
        return True
    try:
        num = float(chapter_str)
        return num > 0
    except ValueError:
        return False

def main():
    """Executes the manga search and download."""
    parser = argparse.ArgumentParser(description="Downloads manga chapters from MangaDex.")
    parser.add_argument("--manga", "-m", type=str, help="The name of the manga to download.")
    parser.add_argument("--chapters", "-c", type=str, help="The chapters to download (e.g., '1 5 10', 'all', '20-25').")
    args = parser.parse_args()

    if args.manga:
        title = args.manga.strip()
        if not title:
            print("⚠️ Manga title cannot be empty.")
            return
    else:
        title = input("Enter the manga name: ").strip()
        if not title:
            print("⚠️ Manga title cannot be empty.")
            return

    manga_id, manga_title_sanitized = search_manga(title)

    if manga_id:
        chapters = get_chapters(manga_id)
        if not chapters:
            print("⚠️ No chapters available in Portuguese.")
            return

        print("\n📖 Available Chapters:")
        for chap in chapters:
            print(f"• Chapter {chap['number']}")

        if args.chapters:
            choice = args.chapters.strip()
            if not choice:
                print("⚠️ Chapter selection cannot be empty.")
                return
        else:
            choice = input("\nEnter the chapters to download (separated by space, 'all', or range like XX-YY): ").strip()
            if not choice:
                print("⚠️ Chapter selection cannot be empty.")
                return

        selected = []
        is_range = False
        if choice.lower() == 'all':
            selected = chapters
        elif '-' in choice:
            is_range = True
            try:
                start_str, end_str = choice.split('-')
                if start_str and end_str:
                    try:
                        start_chapter = float(start_str.strip())
                        end_chapter = float(end_str.strip())
                        if start_chapter <= 0 or end_chapter <= 0 or start_chapter > end_chapter:
                            print("⚠️ Invalid chapter range. Numbers must be positive and start <= end.")
                        else:
                            selected = select_chapters_by_range(chapters, start_chapter, end_chapter)
                            if not selected:
                                print(f"⚠️ No chapters found in the range {start_chapter}-{end_chapter}.")
                                return
                    except ValueError:
                        print("⚠️ Invalid chapter number format in range.")
                        return
                else:
                    raise ValueError("⚠️ Invalid range format.")
            except ValueError:
                print("⚠️ Invalid range format. Please use XX-YY.")
                return
        else:
            chapter_numbers = choice.split()
            invalid_numbers = [num for num in chapter_numbers if not is_valid_chapter_number(num)]
            if invalid_numbers:
                print(f"⚠️ Invalid chapter number(s) provided: {', '.join(invalid_numbers)}. Please enter positive numbers or 'all'.")
                return
            selected = [chap for chap in chapters if chap['number'] in chapter_numbers]
            if not selected and choice.lower() != 'all':
                print("⚠️ Chapter(s) not found in the provided list.")
                return

        if selected:
            manga_download_dir = os.path.join(DOWNLOAD_BASE_DIR, manga_title_sanitized)
            os.makedirs(manga_download_dir, exist_ok=True)

            print("\n⚠️ Atenção: O valor padrão de MAX_THREADS foi definido para 4 para respeitar os limites do MangaDex.")
            print("Você pode ajustar a variável MAX_THREADS no início do script, mas faça isso com cautela.")
            print(f"Um pequeno delay de {CHAPTER_DOWNLOAD_DELAY} segundos será adicionado entre o download de cada capítulo.")

            for i, chap in enumerate(selected):
                print(f"\n📥 Downloading Chapter {chap['number']} and creating PDF...")
                image_paths, temp_dir = download_chapter_images(chap["id"], manga_download_dir, chap["number"])
                if image_paths:
                    pdf_filename = f"Chapter_{chap['number']}.pdf"
                    pdf_output_path = os.path.join(manga_download_dir, pdf_filename)
                    if create_pdf(image_paths, pdf_output_path):
                        print(f"✅ Chapter {chap['number']} saved as {pdf_filename}")
                    else:
                        print(f"❌ Error creating PDF for Chapter {chap['number']}.")
                    # Clean up temporary image directory
                    for img_path in image_paths:
                        try:
                            os.remove(img_path)
                        except OSError as e:
                            print(f"Error deleting temporary image {img_path}: {e}")
                    try:
                        os.rmdir(temp_dir)
                    except OSError as e:
                        print(f"Error deleting temporary directory {temp_dir}: {e}")
                else:
                    print(f"⚠️ No images downloaded for Chapter {chap['number']}.")

                if i < len(selected) - 1: # Adiciona delay entre os capítulos
                    print(f"⏳ Aguardando {CHAPTER_DOWNLOAD_DELAY} segundos antes de baixar o próximo capítulo...")
                    time.sleep(CHAPTER_DOWNLOAD_DELAY)

            if not args.manga: # Only ask to search again if not run from CLI
                while True:
                    option = input("\n(1) Search another manga | (2) Exit: ")
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
