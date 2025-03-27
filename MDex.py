# -*- coding: utf-8 -*-
import os
import sys
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time
import argparse
from PIL import Image
from fpdf import FPDF
import inquirer
import traceback

# --- Global Configurations ---
API_BASE = "https://api.mangadex.org"
DOWNLOAD_BASE_DIR = 'Downloads'
MAX_RETRIES = 3
MAX_THREADS = 4
CHAPTER_DOWNLOAD_DELAY = 0.5
CHAPTERS_PER_BATCH = 100
ASSUMED_DPI = 72

# --- Language Data ---
LANGUAGE_CHOICES = [
    ("Português Brasileiro", "pt-br"),
    ("English", "en"),
    ("Español", "es"),
]

# --- String Dictionaries (Localization) ---
STRINGS = {
    "pt-br": {
        # ... (outras strings inalteradas) ...
        "creating_pdf": "📄 Criando PDF para o Capítulo {}...",
        "pdf_creation_success": "✅ PDF criado com sucesso: {}",
        "pdf_creation_error": "⚠️ Erro ao criar PDF para o Capítulo {}: {}",
        "deleting_images": "🗑️ Removendo imagens originais para o Capítulo {}...",
        "delete_img_error": "   ⚠️ Erro ao remover imagem {}: {}",
        "delete_dir_error": "   ⚠️ Erro ao remover diretório {}: {}",
        "download_summary_title": "\n--- Resumo da Criação de PDF ---", # Title updated
        "summary_pdf_created": " PDF Criados: {}",             # New/Renamed
        "summary_pdf_failed": " Falha na Criação de PDF: {}", # New/Renamed
        "summary_skipped": " Capítulos Ignorados: {}",       # New key
        "summary_footer": "--------------------------------\n", # Adjusted length
        # ... (restante das strings) ...
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
        "overall_download_progress": "Progresso Geral do Processamento", # Renamed progress bar title slightly
        "waiting_next_chapter": "⏳ Aguardando {} segundos...",
        "continue_prompt": "\nO que você gostaria de fazer agora?",
        "search_again_option": "Buscar outro mangá",
        "exit_option": "Sair",
        "invalid_option": "Opção inválida.",
        "try_again_manga_not_found": "Tente novamente. Mangá não encontrado.",
        "overall_download_unit": "capítulo",
        "exiting_message": "Saindo...",
        "program_finished_message": "Programa finalizado.",
        "encoding_warning": "Aviso: Codificação do terminal pode não ser UTF-8.",
        "unexpected_error_title": "\n--- ERRO INESPERADO ---",
        "unexpected_error_message": "Erro não tratado: {}",
        "unexpected_error_footer": "-------------------------",
    },
    "en": {
        # --- Full English Strings with updated summary keys ---
        "download_summary_title": "\n--- PDF Creation Summary ---",
        "summary_pdf_created": " PDFs Created: {}",
        "summary_pdf_failed": " PDF Creation Failed: {}",
        "summary_skipped": " Chapters Skipped: {}",
        "summary_footer": "--------------------------\n",
        "overall_download_progress": "Overall Processing Progress",
        # ... (rest of English strings) ...
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
        "creating_pdf": "📄 Creating PDF for Chapter {}...",
        "pdf_creation_success": "✅ PDF created successfully: {}",
        "pdf_creation_error": "⚠️ Error creating PDF for Chapter {}: {}",
        "deleting_images": "🗑️ Removing original images for Chapter {}...",
        "delete_img_error": "   ⚠️ Error removing image {}: {}",
        "delete_dir_error": "   ⚠️ Error removing directory {}: {}",
        "waiting_next_chapter": "⏳ Waiting {} seconds...",
        "continue_prompt": "\nWhat would you like to do next?",
        "search_again_option": "Search another manga",
        "exit_option": "Exit",
        "invalid_option": "Invalid option.",
        "try_again_manga_not_found": "Try again. Manga not found.",
        "overall_download_unit": "chapter",
        "exiting_message": "Exiting...",
        "program_finished_message": "Program finished.",
        "encoding_warning": "Warning: Terminal encoding might not be UTF-8.",
        "unexpected_error_title": "\n--- UNEXPECTED ERROR ---",
        "unexpected_error_message": "Unhandled error: {}",
        "unexpected_error_footer": "------------------------",
    },
    "es": {
        # --- Full Spanish Strings with updated summary keys ---
        "download_summary_title": "\n--- Resumen de Creación de PDF ---",
        "summary_pdf_created": " PDFs Creados: {}",
        "summary_pdf_failed": " Fallo Creación PDF: {}",
        "summary_skipped": " Capítulos Omitidos: {}",
        "summary_footer": "----------------------------\n",
        "overall_download_progress": "Progreso General Procesamiento",
        # ... (rest of Spanish strings) ...
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
        "chapters_range_prompt": "Ingrese los capítulos (ej: 1 5 10.5), 'all'/'todos', o rango (ej: 20-25):",
        "chapter_selection_empty_error": "⚠️ La selección de capítulos no puede estar vacía.",
        "invalid_chapter_range_error": "⚠️ Rango de capítulos inválido. Números >= 0 y inicio <= fin.",
        "no_chapters_in_range": "⚠️ No se encontraron capítulos en el rango {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido en el rango.",
        "invalid_range_format": "⚠️ Formato de rango inválido ({}). Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Entrada(s) de capítulo(s) inválida(s): {}. Ingrese números >= 0, 'all'/'todos' o rangos.",
        "chapters_not_found": "⚠️ No se encontraron capítulo(s) en la lista: {}.",
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
        "creating_pdf": "📄 Creando PDF para el Capítulo {}...",
        "pdf_creation_success": "✅ PDF creado con éxito: {}",
        "pdf_creation_error": "⚠️ Error al crear PDF para el Capítulo {}: {}",
        "deleting_images": "🗑️ Eliminando imágenes originales para el Capítulo {}...",
        "delete_img_error": "   ⚠️ Error al eliminar imagen {}: {}",
        "delete_dir_error": "   ⚠️ Error al eliminar directorio {}: {}",
        "waiting_next_chapter": "⏳ Esperando {} segundos...",
        "continue_prompt": "\n¿Qué le gustaría hacer ahora?",
        "search_again_option": "Buscar otro manga",
        "exit_option": "Salir",
        "invalid_option": "Opción inválida.",
        "try_again_manga_not_found": "Intente nuevamente. Manga no encontrado.",
        "overall_download_unit": "capítulo",
        "exiting_message": "Saliendo...",
        "program_finished_message": "Programa finalizado.",
        "encoding_warning": "Advertencia: Codificación del terminal puede no ser UTF-8.",
        "unexpected_error_title": "\n--- ERROR INESPERADO ---",
        "unexpected_error_message": "Error no controlado: {}",
        "unexpected_error_footer": "-------------------------",
    },
}

selected_strings = STRINGS["pt-br"]

# --- Function Definitions ---
# (select_language, search_manga, sort_key, get_chapters, download_image,
#  download_chapter_images, is_valid_chapter_number_string, select_chapters_by_range,
#  parse_chapter_selection - unchanged from previous version)

def select_language():
    """Prompts the user to select a language."""
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
                if score >= 60 and not any(m[1]['id'] == manga['id'] for m in similar_matches):
                    display_title = manga["attributes"]["title"].get("en", manga_title_text)
                    similar_matches.append((score, manga, display_title))

    if best_match and best_score >= 75:
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
        return float('inf')

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
            img_resp.raise_for_status()
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

    image_filenames = data_files

    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.() ')
    safe_chapter_display = "".join(c for c in chapter_display if c in safe_chars).strip().replace(' ', '_')
    if not safe_chapter_display:
         safe_chapter_display = f"id_{chapter_id}"
    chapter_path = os.path.join(save_folder, f"Capitulo_{safe_chapter_display}")
    os.makedirs(chapter_path, exist_ok=True)

    img_paths_to_check = []
    download_tasks = []

    for idx, img_file in enumerate(image_filenames):
        try:
             img_extension = os.path.splitext(img_file)[1] if '.' in os.path.basename(img_file) else '.jpg'
        except Exception: img_extension = '.jpg'
        img_filename = f"{idx + 1:03d}{img_extension}"
        img_path = os.path.join(chapter_path, img_filename)
        img_paths_to_check.append(img_path)

        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
            if os.path.exists(img_path):
                 try: os.remove(img_path)
                 except OSError: pass
            img_url = f"{base_url}/data/{hash_val}/{img_file}"
            download_tasks.append((img_url, img_path))

    if download_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(download_image, url, path, session): path for url, path in download_tasks}
            with tqdm(total=len(futures), desc=selected_strings["downloading_images"].format(chapter_display), leave=False) as pbar:
                 for future in concurrent.futures.as_completed(futures):
                    img_path_completed = futures[future]
                    try:
                         future.result()
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
                pass
    return selected_chapters

def parse_chapter_selection(chapters, selection_string):
    """Parses the user's chapter selection string ('all', 'todos', numbers, range)."""
    if selection_string.lower() in ('all', 'todos'):
        return chapters

    selected_chapters_final = []
    potential_inputs = set()
    invalid_inputs = []
    processed_ids = set()

    parts = selection_string.split()

    for part in parts:
        part = part.strip()
        if not part: continue

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
        else:
             potential_inputs.add(part)

    matched_inputs = set()
    for chap in chapters:
        num_str = chap.get('number')
        display_str = chap.get('display')
        matched = False
        if num_str is not None and num_str in potential_inputs:
             matched = True
             matched_inputs.add(num_str)
        elif display_str in potential_inputs:
             if not (num_str is not None and num_str == display_str and matched):
                  matched = True
                  matched_inputs.add(display_str)

        if matched and chap['id'] not in processed_ids:
            selected_chapters_final.append(chap)
            processed_ids.add(chap['id'])

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
    """Executes the main workflow: setup, search, select, download, and PDF creation."""
    parser = argparse.ArgumentParser(description="Downloads manga chapters from MangaDex and creates PDFs.")
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
    session.headers.update({'User-Agent': 'Python-MangaDex-Downloader/1.3-pdf-auto'})

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

    cli_mode = bool(args.manga)
    run_once_cli = False

    while True: # Outer loop allows searching again
        title = None
        if cli_mode:
            if not run_once_cli:
                 title = args.manga.strip()
                 run_once_cli = True
            else: break
        else:
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
                continue

        manga_id, manga_title_sanitized = search_manga(title, session)
        if not manga_id:
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
             for i in range(limit_display // 2): print(selected_strings["chapter_prefix"].format(chapters[i]['display']))
             print(f"    ... ({len(chapters) - limit_display} more chapters) ...")
             for i in range(len(chapters) - (limit_display // 2), len(chapters)): print(selected_strings["chapter_prefix"].format(chapters[i]['display']))
        else:
             for chap in chapters: print(selected_strings["chapter_prefix"].format(chap['display']))

        choice = None
        if cli_mode and args.chapters:
             choice = args.chapters.strip()
             args.chapters = None
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

        chapters_to_download = parse_chapter_selection(chapters, choice)
        if not chapters_to_download:
            print(selected_strings["no_chapters_selected"])
            if cli_mode: break
            else: continue

        manga_download_dir = os.path.join(base_download_dir, manga_title_sanitized)
        try:
            os.makedirs(manga_download_dir, exist_ok=True)
        except OSError as e:
             print(f"Error creating manga directory '{manga_download_dir}': {e}")
             if cli_mode: break
             else: continue

        print(f"\n⚠️ Notice: MAX_THREADS={MAX_THREADS}, Delay={CHAPTER_DOWNLOAD_DELAY}s.")

        total_chapters_to_download = len(chapters_to_download)
        # --- Updated Summary Dictionary ---
        download_summary = {"pdf_created": 0, "pdf_failed": 0, "skipped": 0}

        with tqdm(total=total_chapters_to_download, desc=selected_strings["overall_download_progress"],
                  unit=selected_strings["overall_download_unit"], leave=True) as overall_pbar:
            for i, chap in enumerate(chapters_to_download):
                pdf_created_successfully = False
                image_paths = []
                chapter_dir_path = None
                try:
                     print(selected_strings["downloading_images_chapter"].format(chap['display']))
                     image_paths, chapter_dir_path = download_chapter_images(chap["id"], manga_download_dir, chap["display"], session)

                     if chapter_dir_path:
                         if image_paths: # Images were downloaded/found successfully
                              # Don't print image success, only PDF status if applicable
                              # print(selected_strings["download_successful"].format(chap['display'], chapter_dir_path))

                              # --- START Automatic PDF Creation Logic ---
                              safe_chapter_display_pdf = "".join(c for c in chap['display'] if c.isalnum() or c in (' ', '_', '.', '-')).rstrip().replace(' ', '_')
                              if not safe_chapter_display_pdf: safe_chapter_display_pdf = f"id_{chap['id']}"
                              pdf_filename = os.path.join(manga_download_dir, f"Capitulo_{safe_chapter_display_pdf}.pdf")

                              try:
                                  print(selected_strings["creating_pdf"].format(chap['display']))
                                  pdf = FPDF(unit="pt")

                                  for image_path in image_paths:
                                      try:
                                          with Image.open(image_path) as img:
                                              width_px, height_px = img.size
                                              if width_px <= 0 or height_px <= 0:
                                                  print(f"⚠️ Skipping invalid image (zero dimension): {os.path.basename(image_path)}")
                                                  continue
                                              img_dpi = img.info.get('dpi', (ASSUMED_DPI, ASSUMED_DPI))
                                              if not isinstance(img_dpi, (tuple, list)) or len(img_dpi) < 2: img_dpi = (ASSUMED_DPI, ASSUMED_DPI)
                                              dpi_x = img_dpi[0] if img_dpi[0] > 0 else ASSUMED_DPI
                                              dpi_y = img_dpi[1] if img_dpi[1] > 0 else ASSUMED_DPI
                                              width_pt = width_px * 72.0 / dpi_x
                                              height_pt = height_px * 72.0 / dpi_y

                                              orientation = 'L' if width_pt > height_pt else 'P'
                                              pdf.add_page(orientation=orientation)
                                              page_w_pt = pdf.w
                                              page_h_pt = pdf.h

                                              scale = 1
                                              if width_pt > 0 and height_pt > 0:
                                                  scale = min(page_w_pt / width_pt, page_h_pt / height_pt)
                                              img_w_pt = width_pt * scale
                                              img_h_pt = height_pt * scale

                                              x_pos = (page_w_pt - img_w_pt) / 2
                                              y_pos = (page_h_pt - img_h_pt) / 2

                                              pdf.image(image_path, x=x_pos, y=y_pos, w=img_w_pt, h=img_h_pt)
                                      except Exception as img_err:
                                          print(f"⚠️ Error processing image {os.path.basename(image_path)} for PDF: {img_err}")

                                  pdf.output(pdf_filename)
                                  print(selected_strings["pdf_creation_success"].format(os.path.basename(pdf_filename)))
                                  download_summary["pdf_created"] += 1 # Increment PDF created count
                                  pdf_created_successfully = True

                              except Exception as pdf_err:
                                  print(selected_strings["pdf_creation_error"].format(chap['display'], pdf_err))
                                  download_summary["pdf_failed"] += 1 # Increment PDF failed count
                                  if os.path.exists(pdf_filename):
                                      try: os.remove(pdf_filename)
                                      except OSError: pass
                              # --- END Automatic PDF Creation Logic ---

                         else: # No images downloaded/found for this chapter
                              print(selected_strings["no_images_downloaded"].format(chap['display']))
                              download_summary["skipped"] += 1 # Increment skipped count
                              # Attempt to remove empty dir if created
                              try:
                                   if chapter_dir_path and os.path.exists(chapter_dir_path) and not os.listdir(chapter_dir_path):
                                        os.rmdir(chapter_dir_path)
                                        print(selected_strings["empty_dir_removed"].format(os.path.basename(chapter_dir_path)))
                              except OSError: pass
                     else: # Failed before creating directory (e.g., server API error)
                          print(selected_strings["process_chapter_failed"].format(chap['display']))
                          download_summary["skipped"] += 1 # Increment skipped count

                     # --- START Automatic Image Deletion Logic ---
                     if pdf_created_successfully:
                         print(selected_strings["deleting_images"].format(chap['display']))
                         try:
                             for img_path in image_paths:
                                 try:
                                     if os.path.exists(img_path):
                                         os.remove(img_path)
                                 except OSError as e:
                                     print(selected_strings["delete_img_error"].format(os.path.basename(img_path), e))
                             try:
                                 if chapter_dir_path and os.path.exists(chapter_dir_path):
                                     os.rmdir(chapter_dir_path)
                             except OSError as e:
                                 print(selected_strings["delete_dir_error"].format(os.path.basename(chapter_dir_path), e))
                         except Exception as del_err:
                             print(f"⚠️ Unexpected error during image/folder deletion for chapter {chap['display']}: {del_err}")
                     # --- END Automatic Image Deletion Logic ---

                except Exception as chap_err:
                     print(f"Unexpected error processing chapter {chap.get('display', 'N/A')}: {chap_err}")
                     download_summary["skipped"] += 1 # Increment skipped count for unexpected errors too
                     traceback.print_exc()

                finally:
                     overall_pbar.update(1)
                     if i < len(chapters_to_download) - 1:
                         time.sleep(CHAPTER_DOWNLOAD_DELAY)

        # --- Print Updated Summary ---
        print(selected_strings["download_summary_title"])
        print(selected_strings["summary_pdf_created"].format(download_summary['pdf_created']))
        print(selected_strings["summary_pdf_failed"].format(download_summary['pdf_failed']))
        print(selected_strings["summary_skipped"].format(download_summary['skipped'])) # Use new key
        print(selected_strings["summary_footer"])

        # --- Ask to Continue ---
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
                    break
            except KeyboardInterrupt:
                 print(f"\n{selected_strings['exiting_message']}")
                 break
        else:
            break

    print(selected_strings["program_finished_message"])

# --- Script Entry Point ---
if __name__ == "__main__":
    if sys.stdout.encoding is None or sys.stdout.encoding.lower().replace('-', '') != 'utf8':
        print(STRINGS['en']['encoding_warning'])

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{STRINGS['en']['exiting_message']}")
        sys.exit(0)
    except Exception as e:
        print(STRINGS['en']['unexpected_error_title'])
        print(STRINGS['en']['unexpected_error_message'].format(e))
        traceback.print_exc()
        print(STRINGS['en']['unexpected_error_footer'])
        sys.exit(1)
