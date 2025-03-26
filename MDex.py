# -*- coding: utf-8 -*- # Added encoding declaration
import os
import sys # Needed for robust exit/restart logic and encoding checks
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time
import argparse
# PIL (Pillow) is imported but not used in this version. Kept for potential future use.
# from PIL import Image
import inquirer
import traceback # For better error reporting

# Global Configurations
API_BASE = "https://api.mangadex.org"
DOWNLOAD_BASE_DIR = 'Downloads' # Default base directory
MAX_RETRIES = 3
MAX_THREADS = 4
CHAPTER_DOWNLOAD_DELAY = 0.5
CHAPTERS_PER_BATCH = 100

# Language mapping and string dictionaries (Unchanged from previous version)
LANGUAGE_CHOICES = [
    ("Português Brasileiro", "pt-br"),
    ("English", "en"),
    ("Español", "es"),
]

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
        "chapters_range_prompt": "Digite os capítulos para baixar (ex: 1 5 10.5), 'todos' para todos, ou um intervalo (ex: 20-25):",
        "chapter_selection_empty_error": "⚠️ A seleção de capítulos não pode estar vazia.",
        "invalid_chapter_range_error": "⚠️ Intervalo de capítulos inválido. Os números devem ser >= 0 e o início <= fim.",
        "no_chapters_in_range": "⚠️ Nenhum capítulo encontrado no intervalo {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido no intervalo.",
        "invalid_range_format": "⚠️ Formato de intervalo inválido ({}) Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Entrada(s) de capítulo inválida(s): {}. Digite números >= 0, 'todos' ou intervalos.",
        "chapters_not_found": "⚠️ Capítulo(s) não encontrado(s) na lista fornecida: {}.",
        "no_chapters_selected": "⚠️ Nenhum capítulo válido selecionado para download.",
        "downloading_images_chapter": "\n📥 Baixando imagens para o Capítulo {}...",
        "search_image_server_error": "Erro ao buscar o servidor de imagens: {}",
        "unexpected_image_server_error": "Erro inesperado ao obter servidor de imagens: {}",
        "image_server_api_error": "API não retornou status 'ok' para o servidor: {}",
        "image_server_incomplete_response": "Erro: Resposta da API do servidor de imagens incompleta.",
        "image_hash_files_missing": "Erro: Hash ou lista de arquivos não encontrados na resposta da API.",
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
        "waiting_next_chapter": "⏳ Aguardando {} segundos antes de baixar o próximo capítulo...",
        "continue_prompt": "\nO que você gostaria de fazer agora?",
        "search_again_option": "Buscar outro mangá",
        "exit_option": "Sair",
        "invalid_option": "Opção inválida.",
        "try_again_manga_not_found": "Tente novamente. Mangá não encontrado.",
        "overall_download_unit": "capítulo",
        "download_summary_title": "\n--- Resumo do Download ---",
        "summary_success": " Sucesso: {} capítulos",
        "summary_no_images": " Sem Imagens Baixadas: {} capítulos",
        "summary_failed": " Falha no Processamento: {} capítulos",
        "summary_footer": "---------------------------\n",
        "exiting_message": "Saindo...",
        "program_finished_message": "Programa finalizado.",
        "encoding_warning": "Aviso: A codificação do terminal pode não ser UTF-8. Caracteres especiais podem não ser exibidos corretamente.",
        "unexpected_error_title": "\n--- ERRO INESPERADO ---",
        "unexpected_error_message": "Ocorreu um erro não tratado: {}",
        "unexpected_error_footer": "-------------------------",
    },
    # --- English Strings (abbreviated for brevity, assume similar keys as pt-br) ---
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
        "chapters_range_prompt": "Enter chapters to download (e.g., 1 5 10.5), 'all' for all, or a range (e.g., 20-25):",
        "chapter_selection_empty_error": "⚠️ Chapter selection cannot be empty.",
        "invalid_chapter_range_error": "⚠️ Invalid chapter range. Numbers must be >= 0 and start <= end.",
        "no_chapters_in_range": "⚠️ No chapters found in the range {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Invalid chapter number format in range.",
        "invalid_range_format": "⚠️ Invalid range format ({}). Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Invalid chapter input(s): {}. Enter numbers >= 0, 'all', or ranges.",
        "chapters_not_found": "⚠️ Chapter(s) not found in the provided list: {}.",
        "no_chapters_selected": "⚠️ No valid chapters selected for download.",
        "downloading_images_chapter": "\n📥 Downloading images for Chapter {}...",
        "search_image_server_error": "Error searching for image server: {}",
        "unexpected_image_server_error": "Unexpected error getting image server: {}",
        "image_server_api_error": "API did not return 'ok' status for server: {}",
        "image_server_incomplete_response": "Error: Incomplete image server API response.",
        "image_hash_files_missing": "Error: Hash or file list not found in API response.",
        "downloading_images": "🖼️ Downloading images for Chapter {}",
        "download_successful": "✅ Successfully downloaded images for Chapter {} to: {}",
        "download_failed": "⚠️ Failed to download {} ({}), attempt {}/{}...",
        "download_timeout": "Timeout downloading {}, attempt {}/{}...",
        "unexpected_download_error": "Unexpected error downloading {}: {}",
        "final_download_failed": "⚠️ Final fail to download {}",
        "empty_dir_removed": "   Empty directory removed: {}",
        "process_chapter_failed": "⚠️ Failed to process Chapter {}.",
        "no_new_images": "No new images to download in this chapter (already exist?).",
        "no_images_downloaded": "⚠️ No images downloaded for Chapter {}.",
        "overall_download_progress": "Overall Download Progress",
        "waiting_next_chapter": "⏳ Waiting for {} seconds before downloading the next chapter...",
        "continue_prompt": "\nWhat would you like to do next?",
        "search_again_option": "Search another manga",
        "exit_option": "Exit",
        "invalid_option": "Invalid option.",
        "try_again_manga_not_found": "Try again. Manga not found.",
        "overall_download_unit": "chapter",
        "download_summary_title": "\n--- Download Summary ---",
        "summary_success": " Success: {} chapters",
        "summary_no_images": " No Images Downloaded: {} chapters",
        "summary_failed": " Processing Failed: {} chapters",
        "summary_footer": "------------------------\n",
        "exiting_message": "Exiting...",
        "program_finished_message": "Program finished.",
        "encoding_warning": "Warning: Terminal encoding might not be UTF-8. Special characters may not display correctly.",
        "unexpected_error_title": "\n--- UNEXPECTED ERROR ---",
        "unexpected_error_message": "An unhandled error occurred: {}",
        "unexpected_error_footer": "------------------------",
    },
    # --- Spanish Strings (similar structure) ---
    "es": {
        # ... (keys similar to pt-br/en) ...
        "select_language_prompt": "🌍 Seleccione el idioma para descargar:",
        "selected_language": "Idioma seleccionado: {}",
        "manga_title_prompt": "Ingrese el nombre del manga:",
        "manga_title_empty_error": "⚠️ El título del manga no puede estar vacío.",
        "search_manga_error": "Error al buscar el manga: {}",
        "no_manga_found": "No se encontró ningún manga con el nombre: {}",
        "manga_found": "📚 Manga encontrado: {}",
        "no_exact_match": "No se encontró una coincidencia exacta para '{}'. Resultados similares:",
        "fetching_chapters": "🔍 Buscando capítulos",
        "chapter": "capítulo",
        "search_chapters_error": "Error al buscar capítulos: {}",
        "unexpected_chapter_error": "Error inesperado al buscar capítulos: {}",
        "no_chapters_available": "⚠️ No hay capítulos disponibles en el idioma seleccionado ({}).",
        "available_chapters": "\n📖 Capítulos disponibles:",
        "chapter_prefix": "• Capítulo {}",
        "chapters_range_prompt": "Ingrese los capítulos para descargar (ej: 1 5 10.5), 'todos' para todos, o un rango (ej: 20-25):",
        "chapter_selection_empty_error": "⚠️ La selección de capítulos no puede estar vacía.",
        "invalid_chapter_range_error": "⚠️ Rango de capítulos inválido. Los números deben ser >= 0 y el inicio <= fin.",
        "no_chapters_in_range": "⚠️ No se encontraron capítulos en el rango {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido en el rango.",
        "invalid_range_format": "⚠️ Formato de rango inválido ({}). Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Entrada(s) de capítulo(s) inválida(s): {}. Ingrese números >= 0, 'todos' o rangos.",
        "chapters_not_found": "⚠️ No se encontraron capítulo(s) en la lista proporcionada: {}.",
        "no_chapters_selected": "⚠️ No se seleccionaron capítulos válidos para descargar.",
        "downloading_images_chapter": "\n📥 Descargando imágenes para el Capítulo {}...",
        "search_image_server_error": "Error al buscar el servidor de imágenes: {}",
        "unexpected_image_server_error": "Error inesperado al obtener el servidor de imágenes: {}",
        "image_server_api_error": "La API no devolvió el estado 'ok' para el servidor: {}",
        "image_server_incomplete_response": "Error: Respuesta incompleta de la API del servidor de imágenes.",
        "image_hash_files_missing": "Error: Hash o lista de archivos no encontrados en la respuesta de la API.",
        "downloading_images": "🖼️ Descargando imágenes para el Capítulo {}",
        "download_successful": "✅ Imágenes descargadas exitosamente para el Capítulo {} en: {}",
        "download_failed": "⚠️ Falló la descarga de {} ({}), intento {}/{}...",
        "download_timeout": "Timeout al descargar {}, intento {}/{}...",
        "unexpected_download_error": "Error inesperado al descargar {}: {}",
        "final_download_failed": "⚠️ Fallo final al descargar {}",
        "empty_dir_removed": "   Directorio vacío eliminado: {}",
        "process_chapter_failed": "⚠️ Falló el procesamiento del Capítulo {}.",
        "no_new_images": "No hay imágenes nuevas para descargar en este capítulo (¿ya existen?).",
        "no_images_downloaded": "⚠️ No se descargaron imágenes para el Capítulo {}.",
        "overall_download_progress": "Progreso general de descarga",
        "waiting_next_chapter": "⏳ Esperando {} segundos antes de descargar el siguiente capítulo...",
        "continue_prompt": "\n¿Qué le gustaría hacer ahora?",
        "search_again_option": "Buscar otro manga",
        "exit_option": "Salir",
        "invalid_option": "Opción inválida.",
        "try_again_manga_not_found": "Intente nuevamente. Manga no encontrado.",
        "overall_download_unit": "capítulo",
        "download_summary_title": "\n--- Resumen de Descarga ---",
        "summary_success": " Éxito: {} capítulos",
        "summary_no_images": " Sin Imágenes Descargadas: {} capítulos",
        "summary_failed": " Fallo de Procesamiento: {} capítulos",
        "summary_footer": "---------------------------\n",
        "exiting_message": "Saliendo...",
        "program_finished_message": "Programa finalizado.",
        "encoding_warning": "Advertencia: La codificación del terminal puede no ser UTF-8. Los caracteres especiales pueden no mostrarse correctamente.",
        "unexpected_error_title": "\n--- ERROR INESPERADO ---",
        "unexpected_error_message": "Ocurrió un error no controlado: {}",
        "unexpected_error_footer": "-------------------------",
    },
}

# Global variable to hold the selected language strings
selected_strings = STRINGS["pt-br"]  # Default to Portuguese

# --- Function Definitions (select_language, search_manga, etc.) ---
# Functions are mostly unchanged from the previous version, incorporating minor
# error handling improvements and using the localized strings properly.

def select_language():
    """Prompts the user to select a language and sets the global string dictionary."""
    global selected_strings
    questions = [
        inquirer.List(
            'language_code',
            message=STRINGS["en"]["select_language_prompt"],
            choices=LANGUAGE_CHOICES,
            carousel=True,
        ),
    ]
    try:
        answers = inquirer.prompt(questions)
        if not answers:
             print(f"\n{STRINGS['en']['exiting_message']}")
             sys.exit(0)
        language_code = answers['language_code']
    except KeyboardInterrupt:
        print(f"\n{STRINGS['en']['exiting_message']}")
        sys.exit(0)

    selected_strings = STRINGS.get(language_code, STRINGS["en"])
    language_name = next((item[0] for item in LANGUAGE_CHOICES if item[1] == language_code), "Unknown")
    print(selected_strings["selected_language"].format(language_name))
    return language_code

def search_manga(title, session):
    """Searches for a manga by title and returns the ID and formatted name for saving."""
    params = {"title": title, "limit": 10, "order[relevance]": "desc"}
    try:
        resp = session.get(f"{API_BASE}/manga", params=params, timeout=15) # Slightly longer timeout
        resp.raise_for_status()
    except requests.RequestException as e:
        print(selected_strings["search_manga_error"].format(e))
        return None, None

    data = resp.json()
    if not data["data"]:
        print(selected_strings["no_manga_found"].format(title))
        return None, None

    best_match = None
    best_score = 0
    similar_matches = []

    # Exact match check (improved)
    title_lower = title.lower()
    for manga in data["data"]:
        titles = manga["attributes"]["title"]
        if any(t.lower() == title_lower for t in titles.values()):
            best_match = manga
            best_score = 100
            break

    # Fuzzy match if no exact found
    if not best_match:
        for manga in data["data"]:
            for title_lang, manga_title_text in manga["attributes"]["title"].items():
                score = fuzz.ratio(title_lower, manga_title_text.lower())
                if score > best_score:
                    best_score = score
                    best_match = manga
                if score >= 60 and not any(m[1]['id'] == manga['id'] for m in similar_matches):
                    display_title = manga["attributes"]["title"].get("en", manga_title_text)
                    similar_matches.append((score, manga, display_title))

    if best_match and best_score >= 75:
        manga_display_title = best_match["attributes"]["title"].get("en") or \
                              next(iter(best_match["attributes"]["title"].values()), "Unknown_Title")
        print(selected_strings["manga_found"].format(manga_display_title))
        sanitized_title = "".join(c for c in manga_display_title if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        return best_match["id"], sanitized_title

    print(selected_strings["no_exact_match"].format(title))
    similar_matches.sort(key=lambda x: x[0], reverse=True)
    for score, _, display_title in similar_matches[:5]:
        print(f"🔹 {display_title} (similaridade: {score}%)") # Corrected "similaridade"

    return None, None

def sort_key(chap):
    """Helper function to sort chapters numerically."""
    try:
        return float(chap['number']) if chap['number'] is not None else float('inf')
    except (ValueError, TypeError):
        return float('inf') # Place non-numeric chapters at the end

def get_chapters(manga_id, lang, session):
    """Returns a list of available chapters in the specified language."""
    chapters = []
    offset = 0
    limit = CHAPTERS_PER_BATCH
    total_chapters = None
    fetched_count = 0

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
                if not current_batch:
                    break

                batch_size = len(current_batch)
                for item in current_batch:
                    chap_id = item["id"]
                    attributes = item["attributes"]
                    chap_number = attributes.get("chapter")
                    chap_title = attributes.get("title")
                    display_number = str(chap_number) if chap_number is not None else chap_title if chap_title else "N/A"
                    # Add volume info if needed: vol = attributes.get("volume")

                    chapters.append({"id": chap_id, "number": chap_number, "display": display_number})
                    fetched_count += 1
                    pbar.update(1)

                offset += batch_size
                if total_chapters is not None and offset >= total_chapters:
                     break # Exit if we fetched expected total or more

            except requests.RequestException as e:
                print(f"\n{selected_strings['search_chapters_error'].format(e)}")
                return []
            except Exception as e:
                 print(f"\n{selected_strings['unexpected_chapter_error'].format(e)}")
                 return []

    chapters.sort(key=sort_key)
    print(f"\n{selected_strings['fetching_chapters']} - Concluído. {len(chapters)} capítulos encontrados.")
    return chapters


def download_image(img_url, img_path, session):
    """Downloads an image with retry attempts in case of error."""
    img_filename = os.path.basename(img_path) # For logging
    for attempt in range(MAX_RETRIES):
        try:
            img_resp = session.get(img_url, stream=True, timeout=25) # Longer timeout
            img_resp.raise_for_status()
            with open(img_path, 'wb') as f:
                for chunk in img_resp.iter_content(chunk_size=16384): # Larger chunk size
                    f.write(chunk)
            # Basic check for empty file
            if os.path.getsize(img_path) > 0:
                 return True
            else:
                 print(f"\nArquivo baixado vazio: {img_filename}, tentativa {attempt + 1}/{MAX_RETRIES}...")
                 os.remove(img_path) # Remove empty file
                 time.sleep(1) # Short pause before retry

        except requests.exceptions.Timeout:
             print(f"\n{selected_strings['download_timeout'].format(img_filename, attempt + 1, MAX_RETRIES)}")
             time.sleep(3)
        except requests.RequestException as e:
            print(f"\n{selected_strings['download_failed'].format(img_filename, e, attempt + 1, MAX_RETRIES)}")
            time.sleep(2)
        except Exception as e:
             print(f"\n{selected_strings['unexpected_download_error'].format(img_filename, e)}")
             break # Don't retry on unexpected errors

    print(f"\n{selected_strings['final_download_failed'].format(img_filename)}")
    if os.path.exists(img_path):
        try:
            os.remove(img_path) # Clean up failed attempt
        except OSError: pass
    return False

def download_chapter_images(chapter_id, save_folder, chapter_display, session):
    """Downloads all images from a chapter and returns the list of downloaded image paths."""
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
    data_files = chapter_meta.get("data") # Quality mode data
    if not hash_val or not data_files:
         print(f"\n{selected_strings['image_hash_files_missing']}")
         return [], None

    image_filenames = data_files

    safe_chapter_display = "".join(c for c in chapter_display if c.isalnum() or c in (' ', '_', '.', '-')).rstrip().replace(' ', '_')
    chapter_path = os.path.join(save_folder, f"Capitulo_{safe_chapter_display}")
    os.makedirs(chapter_path, exist_ok=True)

    img_paths_to_check = [] # Store all potential paths for verification later
    download_tasks = []

    for idx, img_file in enumerate(image_filenames):
        try:
            # Attempt to keep original extension, default to .jpg if error
             img_extension = os.path.splitext(img_file)[1] if '.' in img_file else '.jpg'
        except Exception:
             img_extension = '.jpg'
        img_filename = f"{idx + 1:03d}{img_extension}"
        img_path = os.path.join(chapter_path, img_filename)
        img_paths_to_check.append(img_path)

        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0: # Re-download if exists but empty
            if os.path.exists(img_path): # Remove empty file before attempting download
                 try: os.remove(img_path)
                 except OSError: pass
            img_url = f"{base_url}/data/{hash_val}/{img_file}"
            download_tasks.append((img_url, img_path))

    download_successful_count = 0
    if download_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(download_image, url, path, session) for url, path in download_tasks]
            with tqdm(total=len(futures), desc=selected_strings["downloading_images"].format(chapter_display), leave=False) as pbar:
                 for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        download_successful_count += 1
                    pbar.update(1)
    else:
         # Check if existing files are valid
         existing_files = [p for p in img_paths_to_check if os.path.exists(p) and os.path.getsize(p) > 0]
         if len(existing_files) == len(img_paths_to_check):
              print(selected_strings["no_new_images"])
         else:
              print("Algumas imagens podem estar faltando ou corrompidas.") # More informative message

    # Return sorted list of paths that actually exist and are not empty
    actual_downloaded_paths = [p for p in img_paths_to_check if os.path.exists(p) and os.path.getsize(p) > 0]
    actual_downloaded_paths.sort(key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))

    return actual_downloaded_paths, chapter_path


def parse_chapter_selection(chapters, selection_string):
    """Parses the user's chapter selection string ('all', numbers, range)."""
    if selection_string.lower() == 'all':
        return chapters

    selected_chapters_final = []
    potential_numbers_str = set()
    invalid_inputs = []
    found_ids_in_ranges = set() # Keep track of chapters added via ranges

    parts = selection_string.split()

    for part in parts:
        part = part.strip()
        if not part: continue

        if '-' in part and part.count('-') == 1: # Ensure only one hyphen for range
            try:
                start_str, end_str = part.split('-', 1)
                start_str = start_str.strip()
                end_str = end_str.strip()
                if start_str and end_str:
                     start_chapter = float(start_str)
                     end_chapter = float(end_str)
                     # Allow chapter 0
                     if start_chapter < 0 or end_chapter < 0 or start_chapter > end_chapter:
                         print(selected_strings["invalid_chapter_range_error"])
                         invalid_inputs.append(part)
                     else:
                          chapters_in_range = select_chapters_by_range(chapters, start_chapter, end_chapter)
                          if not chapters_in_range:
                               print(selected_strings["no_chapters_in_range"].format(start_chapter, end_chapter))
                          for chap in chapters_in_range:
                               if chap['id'] not in found_ids_in_ranges:
                                    selected_chapters_final.append(chap)
                                    found_ids_in_ranges.add(chap['id'])
                else:
                     raise ValueError("Incomplete range")
            except (ValueError, TypeError):
                 print(selected_strings["invalid_range_format"].format(part))
                 invalid_inputs.append(part)
        elif is_valid_chapter_number_string(part):
             potential_numbers_str.add(part)
        else:
             invalid_inputs.append(part)

    # Match individual numbers, only adding if not already added by a range
    found_by_number = []
    processed_numbers = set()
    for chap in chapters:
        chap_num_str = chap.get('number')
        if chap_num_str is not None and chap_num_str in potential_numbers_str:
            processed_numbers.add(chap_num_str) # Mark this number as processed
            if chap['id'] not in found_ids_in_ranges: # Check if already added by range
                found_by_number.append(chap)
                # Add ID here too to prevent duplicates if listed multiple times
                found_ids_in_ranges.add(chap['id'])

    selected_chapters_final.extend(found_by_number)

    # Report issues
    unmatched_numbers = potential_numbers_str - processed_numbers
    if unmatched_numbers:
         print(selected_strings["chapters_not_found"].format(', '.join(sorted(list(unmatched_numbers)))))
    if invalid_inputs:
        print(selected_strings["invalid_chapter_number_provided"].format(', '.join(invalid_inputs)))

    # Final sort
    selected_chapters_final.sort(key=sort_key)
    return selected_chapters_final


def is_valid_chapter_number_string(chapter_str):
    """Checks if a chapter string is a valid number >= 0."""
    try:
        return float(chapter_str) >= 0
    except ValueError:
        return False

def select_chapters_by_range(chapters, start_chapter, end_chapter):
    """Seleciona capítulos dentro de um intervalo numérico especificado (número >= 0)."""
    selected_chapters = []
    for chap in chapters:
        chap_num_str = chap.get('number')
        if chap_num_str is not None: # Garante que a chave 'number' existe e não é None
            try:
                num = float(chap_num_str)
                # Verifica se o número está dentro do intervalo desejado
                if start_chapter <= num <= end_chapter:
                    selected_chapters.append(chap)
            except (ValueError, TypeError):
                # Ignora silenciosamente capítulos onde 'number' não é um float válido
                pass
    return selected_chapters

# --- Main Execution ---
def main():
    """Executes the manga search and download."""
    parser = argparse.ArgumentParser(description="Baixa capítulos de mangá do MangaDex.")
    parser.add_argument("--manga", "-m", type=str, help="O nome do mangá para baixar.")
    parser.add_argument("--lang", "-l", type=str, help="Código do idioma para baixar (ex: pt-br, en, es).")
    parser.add_argument("--chapters", "-c", type=str,
                        help="Capítulos para baixar (ex: '1 5 10', 'all', '20-25').")
    parser.add_argument("--dir", "-d", type=str, default=DOWNLOAD_BASE_DIR,
                         help=f"Diretório base para downloads (padrão: {DOWNLOAD_BASE_DIR})")

    args = parser.parse_args()

    # Use args.dir directly, ensure it exists. No global modification needed here.
    try:
        os.makedirs(args.dir, exist_ok=True)
    except OSError as e:
         print(f"Erro ao criar diretório base '{args.dir}': {e}")
         sys.exit(1)
    base_download_dir = args.dir # Use this variable locally

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
            print(f"Código de idioma inválido: {args.lang}. Usando seleção interativa.")
            language_code = select_language()
    else:
        language_code = select_language()

    # --- Main Application Loop ---
    cli_mode = bool(args.manga)
    run_once = False

    while True: # OUTER LOOP START
        title = None
        if cli_mode:
            if not run_once:
                 title = args.manga.strip()
                 run_once = True
            else:
                 break
        else:
            questions = [inquirer.Text('manga_title', message=selected_strings["manga_title_prompt"])]
            try:
                answers = inquirer.prompt(questions)
                if not answers: raise KeyboardInterrupt # Treat closing prompt as Ctrl+C
                title = answers.get('manga_title', '').strip()
            except KeyboardInterrupt:
                 print(f"\n{selected_strings['exiting_message']}")
                 break
            if not title:
                print(selected_strings["manga_title_empty_error"])
                continue

        manga_id, manga_title_sanitized = search_manga(title, session)
        if not manga_id:
            # search_manga already prints messages
            if cli_mode: break
            else: continue

        chapters = get_chapters(manga_id, language_code, session)
        if not chapters:
            lang_name = dict(LANGUAGE_CHOICES).get(language_code, language_code)
            print(selected_strings["no_chapters_available"].format(lang_name))
            if cli_mode: break
            else: continue

        print(selected_strings["available_chapters"])
        limit_display = 20
        if len(chapters) > limit_display:
             for i, chap in enumerate(chapters):
                 if i < limit_display // 2 or i >= len(chapters) - (limit_display // 2):
                      print(selected_strings["chapter_prefix"].format(chap['display']))
                 elif i == limit_display // 2:
                      print(f"    ... ({len(chapters) - limit_display} mais capítulos) ...")
        else:
             for chap in chapters:
                  print(selected_strings["chapter_prefix"].format(chap['display']))

        choice = None
        # Use CLI chapters only if in CLI mode and it's the first run
        if cli_mode and args.chapters:
             choice = args.chapters.strip()
        elif not cli_mode: # Always ask interactively if not in CLI mode
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

        chapters_to_download = parse_chapter_selection(chapters, choice)
        if not chapters_to_download:
            # parse_chapter_selection prints specific errors
            print(selected_strings["no_chapters_selected"])
            if cli_mode: break
            else: continue

        # Use the base directory from args
        manga_download_dir = os.path.join(base_download_dir, manga_title_sanitized)
        try:
            os.makedirs(manga_download_dir, exist_ok=True)
        except OSError as e:
             print(f"Erro ao criar diretório do mangá '{manga_download_dir}': {e}")
             if cli_mode: break
             else: continue # Allow trying another manga

        print(f"\n⚠️ Atenção: MAX_THREADS={MAX_THREADS}, Atraso={CHAPTER_DOWNLOAD_DELAY}s.")

        total_chapters_to_download = len(chapters_to_download)
        download_summary = {"success": 0, "failed": 0, "no_images": 0}

        with tqdm(total=total_chapters_to_download, desc=selected_strings["overall_download_progress"],
                  unit=selected_strings["overall_download_unit"], leave=True) as overall_pbar:
            for i, chap in enumerate(chapters_to_download):
                # Chapter specific messages moved inside try block
                try:
                     print(selected_strings["downloading_images_chapter"].format(chap['display']))
                     image_paths, chapter_dir_path = download_chapter_images(chap["id"], manga_download_dir, chap["display"], session)

                     if chapter_dir_path: # Check if processing started
                         if image_paths: # Check if any images were successfully downloaded/found
                              print(selected_strings["download_successful"].format(chap['display'], chapter_dir_path))
                              download_summary["success"] += 1
                         else:
                              print(selected_strings["no_images_downloaded"].format(chap['display']))
                              download_summary["no_images"] += 1
                              try: # Attempt to remove empty dir
                                   if chapter_dir_path and not os.listdir(chapter_dir_path):
                                        os.rmdir(chapter_dir_path)
                                        print(selected_strings["empty_dir_removed"].format(os.path.basename(chapter_dir_path)))
                              except OSError: pass # Ignore removal error
                     else: # download_chapter_images returned None for path, indicating early failure
                          print(selected_strings["process_chapter_failed"].format(chap['display']))
                          download_summary["failed"] += 1

                except Exception as chap_err: # Catch unexpected errors during chapter processing/download
                     print(f"Erro inesperado processando capítulo {chap.get('display', 'N/A')}: {chap_err}")
                     download_summary["failed"] += 1
                     traceback.print_exc() # Print traceback for debugging

                finally: # Ensure progress bar updates and delay happens
                     overall_pbar.update(1)
                     if i < len(chapters_to_download) - 1:
                         # print(selected_strings["waiting_next_chapter"].format(CHAPTER_DOWNLOAD_DELAY)) # Reduce verbosity
                         time.sleep(CHAPTER_DOWNLOAD_DELAY)


        print(selected_strings["download_summary_title"])
        print(selected_strings["summary_success"].format(download_summary['success']))
        print(selected_strings["summary_no_images"].format(download_summary['no_images']))
        print(selected_strings["summary_failed"].format(download_summary['failed']))
        print(selected_strings["summary_footer"])

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
                    break # Exit outer loop
                # If 'search_again', loop continues automatically
            except KeyboardInterrupt:
                 print(f"\n{selected_strings['exiting_message']}")
                 break # Exit outer loop
        else:
            break # Exit outer loop after CLI run

    # OUTER LOOP END
    print(selected_strings["program_finished_message"])


# --- Script Entry Point ---
if __name__ == "__main__":
    # Check terminal encoding
    if sys.stdout.encoding is None or sys.stdout.encoding.lower().replace('-', '') != 'utf8':
        print(STRINGS['en']['encoding_warning']) # Use English for this warning as encoding might be broken

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{STRINGS['en']['exiting_message']}")
        sys.exit(0)
    except Exception as e:
        # Generic fallback error reporting
        print(STRINGS['en']['unexpected_error_title'])
        print(STRINGS['en']['unexpected_error_message'].format(e))
        traceback.print_exc()
        print(STRINGS['en']['unexpected_error_footer'])
        sys.exit(1)
