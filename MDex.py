# -*- coding: utf-8 -*-
import os
import sys
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time
import argparse
# from PIL import Image # Kept commented as it's unused currently
import inquirer
import traceback

# --- Global Configurations ---
API_BASE = "https://api.mangadex.org"
DOWNLOAD_BASE_DIR = 'Downloads'
MAX_RETRIES = 3
MAX_THREADS = 4 # Adjust cautiously
CHAPTER_DOWNLOAD_DELAY = 0.5 # Adjust cautiously
CHAPTERS_PER_BATCH = 100

# --- Language Data ---
LANGUAGE_CHOICES = [
    ("Português Brasileiro", "pt-br"),
    ("English", "en"),
    ("Español", "es"),
]

# --- String Dictionaries (Localization) ---
STRINGS = {
    "pt-br": {
        "select_language_prompt": "🌍 Selecione o idioma para download:",
        "selected_language": "Idioma selecionado: {}",
        "manga_title_prompt": "Digite o nome do mangá:",
        "manga_title_empty_error": "⚠️ O título do mangá não pode estar vazio.",
        "search_manga_error": "Erro ao buscar o mangá: {}",
        "no_manga_found": "Nenhum mangá encontrado com o nome: {}",
        "manga_found": "📚 Mangá encontrado: {}",
        "no_exact_match": "Nenhuma correspondência exata encontrada para '{}'. Resultados similares:",
        "fetching_chapters": "🔍 Buscando capítulos",
        "chapter": "capítulo",
        "search_chapters_error": "Erro ao buscar capítulos: {}",
        "unexpected_chapter_error": "Erro inesperado ao buscar capítulos: {}",
        "no_chapters_available": "⚠️ Nenhum capítulo disponível no idioma selecionado ({}).",
        "available_chapters": "\n📖 Capítulos Disponíveis:",
        "chapter_prefix": "• Capítulo {}",
        "chapters_range_prompt": "Digite os capítulos (ex: 1 5 10.5), 'all'/'todos', ou intervalo (ex: 20-25):",
        "chapter_selection_empty_error": "⚠️ A seleção de capítulos não pode estar vazia.",
        "invalid_chapter_range_error": "⚠️ Intervalo de capítulos inválido. Números >= 0 e início <= fim.",
        "no_chapters_in_range": "⚠️ Nenhum capítulo encontrado no intervalo {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido no intervalo.",
        "invalid_range_format": "⚠️ Formato de intervalo inválido ({}) Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Entrada(s) de capítulo inválida(s): {}. Digite números >= 0, 'all'/'todos' ou intervalos.",
        "chapters_not_found": "⚠️ Capítulo(s) não encontrado(s) na lista: {}.",
        "no_chapters_selected": "⚠️ Nenhum capítulo válido selecionado para download.",
        "downloading_images_chapter": "\n📥 Baixando imagens para o Capítulo {}...",
        "search_image_server_error": "Erro ao buscar o servidor de imagens: {}",
        "unexpected_image_server_error": "Erro inesperado ao obter servidor de imagens: {}",
        "image_server_api_error": "API não retornou status 'ok' para o servidor: {}",
        "image_server_incomplete_response": "Erro: Resposta da API do servidor de imagens incompleta.",
        "image_hash_files_missing": "Erro: Hash ou lista de arquivos não encontrados na API.",
        "downloading_images": "🖼️ Baixando imagens para o Capítulo {}",
        "download_successful": "✅ Imagens baixadas com sucesso para o Capítulo {} em: {}",
        "download_failed": "⚠️ Falha ao baixar {} ({}), tentativa {}/{}...",
        "download_timeout": "Timeout ao baixar {}, tentativa {}/{}...",
        "unexpected_download_error": "Erro inesperado ao baixar {}: {}",
        "final_download_failed": "⚠️ Falha final ao baixar {}",
        "empty_dir_removed": "   Diretório vazio removido: {}",
        "process_chapter_failed": "⚠️ Falha ao processar o Capítulo {}.",
        "no_new_images": "Nenhuma imagem nova para baixar neste capítulo (já existem?).",
        "no_images_downloaded": "⚠️ Nenhuma imagem baixada para o Capítulo {}.",
        "overall_download_progress": "Progresso Geral do Download",
        "waiting_next_chapter": "⏳ Aguardando {} segundos...",
        "continue_prompt": "\nO que você gostaria de fazer agora?",
        "search_again_option": "Buscar outro mangá",
        "exit_option": "Sair",
        "invalid_option": "Opção inválida.",
        "try_again_manga_not_found": "Tente novamente. Mangá não encontrado.",
        "overall_download_unit": "capítulo",
        "download_summary_title": "\n--- Resumo do Download ---",
        "summary_success": " Sucesso: {} capítulos",
        "summary_no_images": " Sem Imagens: {} capítulos",
        "summary_failed": " Falha: {} capítulos",
        "summary_footer": "---------------------------\n",
        "exiting_message": "Saindo...",
        "program_finished_message": "Programa finalizado.",
        "encoding_warning": "Aviso: Codificação do terminal pode não ser UTF-8.",
        "unexpected_error_title": "\n--- ERRO INESPERADO ---",
        "unexpected_error_message": "Erro não tratado: {}",
        "unexpected_error_footer": "-------------------------",
    },
    "en": {
        "select_language_prompt": "🌍 Select the download language:",
        "selected_language": "Selected language: {}",
        "manga_title_prompt": "Enter the manga name:",
        "manga_title_empty_error": "⚠️ Manga title cannot be empty.",
        "search_manga_error": "Error searching for manga: {}",
        "no_manga_found": "No manga found with the name: {}",
        "manga_found": "📚 Manga found: {}",
        "no_exact_match": "No exact match found for '{}'. Similar results:",
        "fetching_chapters": "🔍 Fetching chapters",
        "chapter": "chapter",
        "search_chapters_error": "Error searching for chapters: {}",
        "unexpected_chapter_error": "Unexpected error fetching chapters: {}",
        "no_chapters_available": "⚠️ No chapters available in the selected language ({}).",
        "available_chapters": "\n📖 Available Chapters:",
        "chapter_prefix": "• Chapter {}",
        "chapters_range_prompt": "Enter chapters (e.g., 1 5 10.5), 'all'/'todos', or range (e.g., 20-25):",
        "chapter_selection_empty_error": "⚠️ Chapter selection cannot be empty.",
        "invalid_chapter_range_error": "⚠️ Invalid chapter range. Numbers >= 0 and start <= end.",
        "no_chapters_in_range": "⚠️ No chapters found in range {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Invalid chapter number format in range.",
        "invalid_range_format": "⚠️ Invalid range format ({}). Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Invalid chapter input(s): {}. Enter numbers >= 0, 'all'/'todos', or ranges.",
        "chapters_not_found": "⚠️ Chapter(s) not found in list: {}.",
        "no_chapters_selected": "⚠️ No valid chapters selected for download.",
        "downloading_images_chapter": "\n📥 Downloading images for Chapter {}...",
        "search_image_server_error": "Error getting image server: {}",
        "unexpected_image_server_error": "Unexpected error getting image server: {}",
        "image_server_api_error": "API error for image server: {}",
        "image_server_incomplete_response": "Error: Incomplete image server API response.",
        "image_hash_files_missing": "Error: Hash or file list missing in API response.",
        "downloading_images": "🖼️ Downloading images for Chapter {}",
        "download_successful": "✅ Successfully downloaded images for Chapter {} to: {}",
        "download_failed": "⚠️ Failed to download {} ({}), attempt {}/{}...",
        "download_timeout": "Timeout downloading {}, attempt {}/{}...",
        "unexpected_download_error": "Unexpected error downloading {}: {}",
        "final_download_failed": "⚠️ Final fail to download {}",
        "empty_dir_removed": "   Empty directory removed: {}",
        "process_chapter_failed": "⚠️ Failed to process Chapter {}.",
        "no_new_images": "No new images to download (already exist?).",
        "no_images_downloaded": "⚠️ No images downloaded for Chapter {}.",
        "overall_download_progress": "Overall Download Progress",
        "waiting_next_chapter": "⏳ Waiting {} seconds...",
        "continue_prompt": "\nWhat would you like to do next?",
        "search_again_option": "Search another manga",
        "exit_option": "Exit",
        "invalid_option": "Invalid option.",
        "try_again_manga_not_found": "Try again. Manga not found.",
        "overall_download_unit": "chapter",
        "download_summary_title": "\n--- Download Summary ---",
        "summary_success": " Success: {} chapters",
        "summary_no_images": " No Images: {} chapters",
        "summary_failed": " Failed: {} chapters",
        "summary_footer": "------------------------\n",
        "exiting_message": "Exiting...",
        "program_finished_message": "Program finished.",
        "encoding_warning": "Warning: Terminal encoding might not be UTF-8.",
        "unexpected_error_title": "\n--- UNEXPECTED ERROR ---",
        "unexpected_error_message": "Unhandled error: {}",
        "unexpected_error_footer": "------------------------",
    },
    "es": {
        # ... (Spanish strings omitted for brevity) ...
        "select_language_prompt": "🌍 Seleccione el idioma para descargar:",
        "selected_language": "Idioma seleccionado: {}",
        # etc...
    },
}

selected_strings = STRINGS["pt-br"]

# --- Function Definitions ---

def select_language():
    """Prompts the user to select a language."""
    global selected_strings
    questions = [
        inquirer.List(
            'language_code',
            message=STRINGS["en"]["select_language_prompt"], # Initial prompt always in English
            choices=LANGUAGE_CHOICES,
            carousel=True,
        ),
    ]
    try:
        answers = inquirer.prompt(questions)
        if not answers: raise KeyboardInterrupt
        language_code = answers['language_code']
    except KeyboardInterrupt:
        print(f"\n{STRINGS['en']['exiting_message']}")
        sys.exit(0)

    selected_strings = STRINGS.get(language_code, STRINGS["en"])
    language_name = next((item[0] for item in LANGUAGE_CHOICES if item[1] == language_code), "Unknown")
    print(selected_strings["selected_language"].format(language_name))
    return language_code

def search_manga(title, session):
    """Searches for a manga by title via MangaDex API."""
    params = {"title": title, "limit": 10, "order[relevance]": "desc"}
    try:
        resp = session.get(f"{API_BASE}/manga", params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(selected_strings["search_manga_error"].format(e))
        return None, None

    data = resp.json()
    if not data.get("data"):
        print(selected_strings["no_manga_found"].format(title))
        return None, None

    best_match = None
    best_score = 0
    similar_matches = []
    title_lower = title.lower()

    for manga in data["data"]:
        if any(t.lower() == title_lower for t in manga["attributes"]["title"].values()):
            best_match = manga
            best_score = 100
            break

    if not best_match:
        for manga in data["data"]:
            for manga_title_text in manga["attributes"]["title"].values():
                score = fuzz.ratio(title_lower, manga_title_text.lower())
                if score > best_score:
                    best_score = score
                    best_match = manga
                # Avoid adding duplicates to similar matches suggestions
                if score >= 60 and not any(m[1]['id'] == manga['id'] for m in similar_matches):
                    display_title = manga["attributes"]["title"].get("en", manga_title_text)
                    similar_matches.append((score, manga, display_title))

    if best_match and best_score >= 75: # Require a reasonably high score
        manga_display_title = best_match["attributes"]["title"].get("en") or \
                              next(iter(best_match["attributes"]["title"].values()), "Unknown_Title")
        print(selected_strings["manga_found"].format(manga_display_title))
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.() ')
        sanitized_title = "".join(c for c in manga_display_title if c in safe_chars).strip().replace(' ', '_')
        return best_match["id"], sanitized_title

    print(selected_strings["no_exact_match"].format(title))
    similar_matches.sort(key=lambda x: x[0], reverse=True)
    for score, _, display_title in similar_matches[:5]:
        print(f"🔹 {display_title} (Similarity: {score}%)")

    return None, None

def sort_key(chap):
    """Sorts chapters numerically, placing non-numeric ones at the end."""
    try:
        return float(chap['number']) if chap['number'] is not None else float('inf')
    except (ValueError, TypeError):
        return float('inf') # Place non-numeric chapters like 'Oneshot' last

def get_chapters(manga_id, lang, session):
    """Fetches and returns a sorted list of available chapters."""
    chapters = []
    offset = 0
    limit = CHAPTERS_PER_BATCH
    total_chapters = None

    print(f"{selected_strings['fetching_chapters']} ({lang})...")
    with tqdm(total=None, desc=selected_strings["fetching_chapters"], unit=selected_strings["chapter"], leave=False) as pbar:
        while True:
            params = {
                "manga": manga_id,
                "translatedLanguage[]": lang,
                "includes[]": "scanlation_group",
                "order[volume]": "asc",
                "order[chapter]": "asc",
                "limit": limit,
                "offset": offset,
                "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"]
            }
            try:
                resp = session.get(f"{API_BASE}/chapter", params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()

                if total_chapters is None:
                    total_chapters = data.get("total", 0)
                    pbar.total = total_chapters

                current_batch = data.get("data", [])
                if not current_batch: break

                for item in current_batch:
                    attributes = item["attributes"]
                    chap_number = attributes.get("chapter")
                    chap_title = attributes.get("title")
                    display_str = str(chap_number) if chap_number is not None else chap_title if chap_title else "N/A"
                    chapters.append({"id": item["id"], "number": chap_number, "display": display_str})
                    pbar.update(1)

                offset += len(current_batch)
                if total_chapters is not None and offset >= total_chapters: break

            except requests.RequestException as e:
                print(f"\n{selected_strings['search_chapters_error'].format(e)}")
                return []
            except Exception as e:
                 print(f"\n{selected_strings['unexpected_chapter_error'].format(e)}")
                 return []

    chapters.sort(key=sort_key)
    print(f"\n{selected_strings['fetching_chapters']} - Done. {len(chapters)} chapters found.")
    return chapters

def download_image(img_url, img_path, session):
    """Downloads a single image with retries."""
    img_filename = os.path.basename(img_path)
    for attempt in range(MAX_RETRIES):
        img_resp = None
        try:
            img_resp = session.get(img_url, stream=True, timeout=25)
            img_resp.raise_for_status() # Raise exception for bad status codes
            with open(img_path, 'wb') as f:
                for chunk in img_resp.iter_content(chunk_size=16384):
                    f.write(chunk)
            if os.path.getsize(img_path) > 0:
                 return True
            else:
                 print(f"\nEmpty file downloaded: {img_filename}, attempt {attempt + 1}/{MAX_RETRIES}...")
                 try: os.remove(img_path)
                 except OSError: pass
                 time.sleep(1)

        except requests.exceptions.Timeout:
             print(f"\n{selected_strings['download_timeout'].format(img_filename, attempt + 1, MAX_RETRIES)}")
             time.sleep(3 + attempt)
        except requests.RequestException as e:
            # Don't retry client errors (e.g., 404 Not Found)
            if img_resp is not None and 400 <= img_resp.status_code < 500:
                 print(f"\n{selected_strings['download_failed'].format(img_filename, e, attempt + 1, MAX_RETRIES)} (Client Error {img_resp.status_code} - Not retrying)")
                 break
            print(f"\n{selected_strings['download_failed'].format(img_filename, e, attempt + 1, MAX_RETRIES)}")
            time.sleep(2 + attempt)
        except Exception as e:
             print(f"\n{selected_strings['unexpected_download_error'].format(img_filename, e)}")
             break

    print(f"\n{selected_strings['final_download_failed'].format(img_filename)}")
    if os.path.exists(img_path):
        try: os.remove(img_path)
        except OSError: pass
    return False

def download_chapter_images(chapter_id, save_folder, chapter_display, session):
    """Downloads all images for a given chapter."""
    try:
        server_resp = session.get(f"{API_BASE}/at-home/server/{chapter_id}?forcePort443=false", timeout=15)
        server_resp.raise_for_status()
        server_data = server_resp.json()
        if server_data.get("result") != "ok":
             raise requests.RequestException(selected_strings["image_server_api_error"].format(server_data.get('result')))
    except requests.RequestException as e:
        print(f"\n{selected_strings['search_image_server_error'].format(e)}")
        return [], None
    except Exception as e:
         print(f"\n{selected_strings['unexpected_image_server_error'].format(e)}")
         return [], None

    base_url = server_data.get("baseUrl")
    chapter_meta = server_data.get("chapter")
    if not base_url or not chapter_meta:
         print(f"\n{selected_strings['image_server_incomplete_response']}")
         return [], None

    hash_val = chapter_meta.get("hash")
    data_files = chapter_meta.get("data")
    if not hash_val or not data_files:
         print(f"\n{selected_strings['image_hash_files_missing']}")
         return [], None

    # --- FIX: Assign data_files to image_filenames ---
    image_filenames = data_files
    # --- End of FIX ---

    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.() ')
    safe_chapter_display = "".join(c for c in chapter_display if c in safe_chars).strip().replace(' ', '_')
    if not safe_chapter_display: # Use chapter ID as fallback folder name
         safe_chapter_display = f"id_{chapter_id}"
    chapter_path = os.path.join(save_folder, f"Capitulo_{safe_chapter_display}")
    os.makedirs(chapter_path, exist_ok=True)

    img_paths_to_check = []
    download_tasks = []

    for idx, img_file in enumerate(image_filenames):
        try: # Attempt to keep original extension
             img_extension = os.path.splitext(img_file)[1] if '.' in os.path.basename(img_file) else '.jpg'
        except Exception: img_extension = '.jpg'
        img_filename = f"{idx + 1:03d}{img_extension}" # Pad with zeros (001, 002, ...)
        img_path = os.path.join(chapter_path, img_filename)
        img_paths_to_check.append(img_path)

        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
            if os.path.exists(img_path):
                 try: os.remove(img_path)
                 except OSError: pass
            img_url = f"{base_url}/data/{hash_val}/{img_file}" # Use high quality URL
            download_tasks.append((img_url, img_path))

    if download_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Map futures to paths for potential error logging
            futures = {executor.submit(download_image, url, path, session): path for url, path in download_tasks}
            with tqdm(total=len(futures), desc=selected_strings["downloading_images"].format(chapter_display), leave=False) as pbar:
                 for future in concurrent.futures.as_completed(futures):
                    img_path_completed = futures[future]
                    try:
                         future.result() # Check for exceptions
                    except Exception as exc:
                         print(f"\nError in download future {os.path.basename(img_path_completed)}: {exc}")
                    finally:
                         pbar.update(1)
    else:
         existing_files = [p for p in img_paths_to_check if os.path.exists(p) and os.path.getsize(p) > 0]
         if len(existing_files) == len(img_paths_to_check) and len(existing_files) > 0:
              print(selected_strings["no_new_images"])

    actual_downloaded_paths = [p for p in img_paths_to_check if os.path.exists(p) and os.path.getsize(p) > 0]
    actual_downloaded_paths.sort(key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    return actual_downloaded_paths, chapter_path

def is_valid_chapter_number_string(chapter_str):
    """Checks if a string represents a valid number >= 0."""
    try:
        return float(chapter_str) >= 0
    except ValueError:
        return False

def select_chapters_by_range(chapters, start_chapter, end_chapter):
    """Selects chapters within a specified numerical range."""
    selected_chapters = []
    for chap in chapters:
        chap_num_str = chap.get('number')
        if chap_num_str is not None:
            try:
                num = float(chap_num_str)
                if start_chapter <= num <= end_chapter:
                    selected_chapters.append(chap)
            except (ValueError, TypeError):
                pass # Ignore if 'number' isn't a valid float
    return selected_chapters

def parse_chapter_selection(chapters, selection_string):
    """Parses the user's chapter selection string ('all', 'todos', numbers, range)."""
    if selection_string.lower() in ('all', 'todos'): # Handle both 'all' and 'todos'
        return chapters

    selected_chapters_final = []
    potential_inputs = set()
    invalid_inputs = []
    processed_ids = set() # Track chapter IDs to ensure uniqueness

    parts = selection_string.split()

    for part in parts:
        part = part.strip()
        if not part: continue

        # Range check XX-YY
        if '-' in part and part.count('-') == 1:
            try:
                start_str, end_str = part.split('-', 1)
                start_str, end_str = start_str.strip(), end_str.strip()
                if start_str and end_str:
                     start_chapter = float(start_str)
                     end_chapter = float(end_str)
                     if start_chapter < 0 or end_chapter < 0 or start_chapter > end_chapter:
                         print(selected_strings["invalid_chapter_range_error"])
                         invalid_inputs.append(part)
                     else:
                          chapters_in_range = select_chapters_by_range(chapters, start_chapter, end_chapter)
                          if not chapters_in_range:
                               print(selected_strings["no_chapters_in_range"].format(start_chapter, end_chapter))
                          for chap in chapters_in_range:
                               if chap['id'] not in processed_ids:
                                    selected_chapters_final.append(chap)
                                    processed_ids.add(chap['id'])
                else: raise ValueError("Incomplete range")
            except (ValueError, TypeError):
                 print(selected_strings["invalid_range_format"].format(part))
                 invalid_inputs.append(part)
        # Otherwise, potential individual chapter number/name
        else:
             potential_inputs.add(part)

    # Match individual inputs (numbers or names like 'Oneshot')
    matched_inputs = set()
    for chap in chapters:
        num_str = chap.get('number')
        display_str = chap.get('display')
        matched = False
        # Check if 'number' string or 'display' string matches user input
        if num_str is not None and num_str in potential_inputs:
             matched = True
             matched_inputs.add(num_str)
        elif display_str in potential_inputs:
             # Avoid double match if num_str and display_str are the same
             if not (num_str is not None and num_str == display_str and matched):
                  matched = True
                  matched_inputs.add(display_str)

        if matched and chap['id'] not in processed_ids:
            selected_chapters_final.append(chap)
            processed_ids.add(chap['id'])

    # Report any inputs that weren't matched or were invalid
    unmatched = potential_inputs - matched_inputs
    unmatched_but_valid_format = {inp for inp in unmatched if is_valid_chapter_number_string(inp) or '-' not in inp}
    invalid_numerics = {inp for inp in unmatched if not is_valid_chapter_number_string(inp) and '-' not in inp}

    if unmatched_but_valid_format:
         print(selected_strings["chapters_not_found"].format(', '.join(sorted(list(unmatched_but_valid_format)))))

    all_invalid = invalid_inputs + sorted(list(invalid_numerics))
    if all_invalid:
        print(selected_strings["invalid_chapter_number_provided"].format(', '.join(all_invalid)))

    selected_chapters_final.sort(key=sort_key)
    return selected_chapters_final

# --- Main Execution ---
def main():
    """Executes the main workflow: setup, search, select, download."""
    parser = argparse.ArgumentParser(description="Downloads manga chapters from MangaDex.")
    parser.add_argument("--manga", "-m", type=str, help="The name of the manga to download.")
    parser.add_argument("--lang", "-l", type=str, help="Language code for chapters (e.g., pt-br, en, es).")
    parser.add_argument("--chapters", "-c", type=str,
                        help="Chapters to download (e.g., '1 5 10', 'all'/'todos', '20-25').")
    parser.add_argument("--dir", "-d", type=str, default=DOWNLOAD_BASE_DIR,
                         help=f"Base download directory (default: {DOWNLOAD_BASE_DIR})")

    args = parser.parse_args()

    try:
        os.makedirs(args.dir, exist_ok=True)
    except OSError as e:
         print(f"Error creating base directory '{args.dir}': {e}")
         sys.exit(1)
    base_download_dir = args.dir

    session = requests.Session()
    session.headers.update({'User-Agent': 'Python-MangaDex-Downloader/1.1'})

    # --- Language Selection ---
    language_code = None
    if args.lang:
        valid_codes = [code for _, code in LANGUAGE_CHOICES]
        if args.lang in valid_codes:
            language_code = args.lang
            global selected_strings
            selected_strings = STRINGS.get(language_code, STRINGS["en"])
            language_name = next((item[0] for item in LANGUAGE_CHOICES if item[1] == language_code), language_code)
            print(selected_strings["selected_language"].format(language_name))
        else:
            print(f"Invalid language code: {args.lang}. Using interactive selection.")
            language_code = select_language()
    else:
        language_code = select_language()

    # --- Main Application Loop ---
    cli_mode = bool(args.manga)
    run_once_cli = False

    # Outer loop to allow searching again in interactive mode
    while True:
        title = None
        if cli_mode:
            if not run_once_cli:
                 title = args.manga.strip()
                 run_once_cli = True
            else: break # Exit loop after first CLI execution
        else: # Interactive mode
            questions = [inquirer.Text('manga_title', message=selected_strings["manga_title_prompt"])]
            try:
                answers = inquirer.prompt(questions)
                if not answers: raise KeyboardInterrupt
                title = answers.get('manga_title', '').strip()
            except KeyboardInterrupt:
                 print(f"\n{selected_strings['exiting_message']}")
                 break
            if not title:
                print(selected_strings["manga_title_empty_error"])
                continue # Ask for title again

        # --- Manga Search ---
        manga_id, manga_title_sanitized = search_manga(title, session)
        if not manga_id:
            if cli_mode: break
            else: continue

        # --- Chapter Fetching ---
        chapters = get_chapters(manga_id, language_code, session)
        if not chapters:
            lang_name = dict(LANGUAGE_CHOICES).get(language_code, language_code)
            print(selected_strings["no_chapters_available"].format(lang_name))
            if cli_mode: break
            else: continue

        # --- Display Available Chapters ---
        print(selected_strings["available_chapters"])
        limit_display = 20
        if len(chapters) > limit_display:
             for i in range(limit_display // 2): print(selected_strings["chapter_prefix"].format(chapters[i]['display']))
             print(f"    ... ({len(chapters) - limit_display} more chapters) ...")
             for i in range(len(chapters) - (limit_display // 2), len(chapters)): print(selected_strings["chapter_prefix"].format(chapters[i]['display']))
        else:
             for chap in chapters: print(selected_strings["chapter_prefix"].format(chap['display']))

        # --- Chapter Selection ---
        choice = None
        if cli_mode and args.chapters:
             choice = args.chapters.strip()
             args.chapters = None # Clear CLI arg after first use
        elif not cli_mode:
            questions_range = [inquirer.Text('chapters_range', message=selected_strings["chapters_range_prompt"])]
            try:
                 range_answer = inquirer.prompt(questions_range)
                 if not range_answer: raise KeyboardInterrupt
                 choice = range_answer.get('chapters_range', '').strip()
            except KeyboardInterrupt:
                  print(f"\n{selected_strings['exiting_message']}")
                  break

        if not choice:
            print(selected_strings["chapter_selection_empty_error"])
            if cli_mode: break
            else: continue

        # --- Parse Selection ---
        chapters_to_download = parse_chapter_selection(chapters, choice)
        if not chapters_to_download:
            print(selected_strings["no_chapters_selected"])
            if cli_mode: break
            else: continue

        # --- Download Process ---
        manga_download_dir = os.path.join(base_download_dir, manga_title_sanitized)
        try:
            os.makedirs(manga_download_dir, exist_ok=True)
        except OSError as e:
             print(f"Error creating manga directory '{manga_download_dir}': {e}")
             if cli_mode: break
             else: continue

        print(f"\n⚠️ Notice: MAX_THREADS={MAX_THREADS}, Delay={CHAPTER_DOWNLOAD_DELAY}s.")

        total_chapters_to_download = len(chapters_to_download)
        download_summary = {"success": 0, "failed": 0, "no_images": 0}

        with tqdm(total=total_chapters_to_download, desc=selected_strings["overall_download_progress"],
                  unit=selected_strings["overall_download_unit"], leave=True) as overall_pbar:
            for i, chap in enumerate(chapters_to_download):
                # Ensure progress bar updates even if chapter download fails
                try:
                     print(selected_strings["downloading_images_chapter"].format(chap['display']))
                     image_paths, chapter_dir_path = download_chapter_images(chap["id"], manga_download_dir, chap["display"], session)

                     if chapter_dir_path:
                         if image_paths: # Success
                              print(selected_strings["download_successful"].format(chap['display'], chapter_dir_path))
                              download_summary["success"] += 1
                         else: # Directory created/exists, but no valid images downloaded/found
                              print(selected_strings["no_images_downloaded"].format(chap['display']))
                              download_summary["no_images"] += 1
                              try: # Attempt to remove empty dir
                                   if chapter_dir_path and not os.listdir(chapter_dir_path):
                                        os.rmdir(chapter_dir_path)
                                        print(selected_strings["empty_dir_removed"].format(os.path.basename(chapter_dir_path)))
                              except OSError: pass
                     else: # Failed before creating directory (e.g., server API error)
                          print(selected_strings["process_chapter_failed"].format(chap['display']))
                          download_summary["failed"] += 1

                except Exception as chap_err: # Catch unexpected errors during chapter processing
                     print(f"Unexpected error processing chapter {chap.get('display', 'N/A')}: {chap_err}")
                     download_summary["failed"] += 1
                     traceback.print_exc()

                finally:
                     overall_pbar.update(1)
                     if i < len(chapters_to_download) - 1:
                         # print(selected_strings["waiting_next_chapter"].format(CHAPTER_DOWNLOAD_DELAY)) # Optional: Reduce verbosity
                         time.sleep(CHAPTER_DOWNLOAD_DELAY)

        # --- Print Summary ---
        print(selected_strings["download_summary_title"])
        print(selected_strings["summary_success"].format(download_summary['success']))
        print(selected_strings["summary_no_images"].format(download_summary['no_images']))
        print(selected_strings["summary_failed"].format(download_summary['failed']))
        print(selected_strings["summary_footer"])

        # --- Ask to Continue (Interactive Mode Only) ---
        if not cli_mode:
            questions_again = [
                inquirer.List('continue_option',
                              message=selected_strings["continue_prompt"],
                              choices=[
                                  (selected_strings["search_again_option"], 'search_again'),
                                  (selected_strings["exit_option"], 'exit')
                              ],
                              carousel=True),
            ]
            try:
                continue_answer = inquirer.prompt(questions_again)
                if not continue_answer or continue_answer['continue_option'] == 'exit':
                    print(selected_strings["exiting_message"])
                    break # Exit the main application loop
                # If 'search_again', the loop simply continues
            except KeyboardInterrupt:
                 print(f"\n{selected_strings['exiting_message']}")
                 break # Exit loop on Ctrl+C
        else:
            break # Exit loop after single CLI run

    print(selected_strings["program_finished_message"])

# --- Script Entry Point ---
if __name__ == "__main__":
    # Encoding check warning
    if sys.stdout.encoding is None or sys.stdout.encoding.lower().replace('-', '') != 'utf8':
        print(STRINGS['en']['encoding_warning']) # Use English for this warning

    try:
        main()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print(f"\n{STRINGS['en']['exiting_message']}")
        sys.exit(0)
    except Exception as e:
        # Fallback for any unexpected error during execution
        print(STRINGS['en']['unexpected_error_title'])
        print(STRINGS['en']['unexpected_error_message'].format(e))
        traceback.print_exc()
        print(STRINGS['en']['unexpected_error_footer'])
        sys.exit(1)
