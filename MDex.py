import os
import requests
from fuzzywuzzy import fuzz
import concurrent.futures
from tqdm import tqdm
import time
import argparse
from PIL import Image
import inquirer

# Global Configurations
API_BASE = "https://api.mangadex.org"
DOWNLOAD_BASE_DIR = 'Downloads'
MAX_RETRIES = 3
MAX_THREADS = 4
CHAPTER_DOWNLOAD_DELAY = 0.5
CHAPTERS_PER_BATCH = 100

# Language mapping and string dictionaries
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
        "no_chapters_available": "⚠️ Nenhum capítulo disponível no idioma selecionado ({}).",
        "available_chapters": "\n📖 Capítulos Disponíveis:",
        "chapter_prefix": "• Capítulo {}",
        "chapter_selection_mode_prompt": "Selecione o modo de seleção de capítulos:",
        "enter_range_option": "Inserir intervalo (ex: 1-10, todos)",
        "chapters_range_prompt": "Digite os capítulos para baixar (separados por espaço, 'all' ou intervalo como XX-YY):",
        "chapter_selection_empty_error": "⚠️ A seleção de capítulos não pode estar vazia.",
        "invalid_chapter_range_error": "⚠️ Intervalo de capítulos inválido. Os números devem ser positivos e o início <= fim.",
        "no_chapters_in_range": "⚠️ Nenhum capítulo encontrado no intervalo {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido no intervalo.",
        "invalid_range_format": "⚠️ Formato de intervalo inválido. Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Número(s) de capítulo inválido(s) fornecidos: {}. Digite números positivos ou 'all'.",
        "chapters_not_found": "⚠️ Capítulo(s) não encontrado(s) na lista fornecida.",
        "no_chapters_selected": "⚠️ Nenhum capítulo selecionado para download.",
        "downloading_images_chapter": "\n📥 Baixando imagens para o Capítulo {}...",
        "search_image_server_error": "Erro ao buscar o servidor de imagens: {}",
        "downloading_images": "🖼️ Baixando imagens para o Capítulo {}",
        "download_successful": "✅ Imagens baixadas com sucesso para o Capítulo {} em: {}",
        "download_failed": "⚠️ Falha ao baixar {}",
        "no_images_downloaded": "⚠️ Nenhuma imagem baixada para o Capítulo {}.",
        "overall_download_progress": "Progresso Geral do Download",
        "waiting_next_chapter": "⏳ Aguardando {} segundos antes de baixar o próximo capítulo...",
        "continue_prompt": "\nO que você gostaria de fazer agora?",
        "search_again_option": "Buscar outro mangá",
        "exit_option": "Sair",
        "invalid_option": "Opção inválida.",
        "try_again_manga_not_found": "Tente novamente. Mangá não encontrado.",
        "overall_download_unit": "capítulo",
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
        "no_chapters_available": "⚠️ No chapters available in the selected language ({}).",
        "available_chapters": "\n📖 Available Chapters:",
        "chapter_prefix": "• Chapter {}",
        "chapter_selection_mode_prompt": "Select chapter selection mode:",
        "enter_range_option": "Enter range (e.g., 1-10, all)",
        "chapters_range_prompt": "Enter the chapters to download (separated by space, 'all', or range like XX-YY):",
        "chapter_selection_empty_error": "⚠️ Chapter selection cannot be empty.",
        "invalid_chapter_range_error": "⚠️ Invalid chapter range. Numbers must be positive and start <= end.",
        "no_chapters_in_range": "⚠️ No chapters found in the range {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Invalid chapter number format in range.",
        "invalid_range_format": "⚠️ Invalid range format. Please use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Invalid chapter number(s) provided: {}. Please enter positive numbers or 'all'.",
        "chapters_not_found": "⚠️ Chapter(s) not found in the provided list.",
        "no_chapters_selected": "⚠️ No chapters selected for download.",
        "downloading_images_chapter": "\n📥 Downloading images for Chapter {}...",
        "search_image_server_error": "Error searching for image server: {}",
        "downloading_images": "🖼️ Downloading images for Chapter {}",
        "download_successful": "✅ Successfully downloaded images for Chapter {} to: {}",
        "download_failed": "⚠️ Failed to download {}",
        "no_images_downloaded": "⚠️ No images downloaded for Chapter {}.",
        "overall_download_progress": "Overall Download Progress",
        "waiting_next_chapter": "⏳ Waiting for {} seconds before downloading the next chapter...",
        "continue_prompt": "\nWhat would you like to do next?",
        "search_again_option": "Search another manga",
        "exit_option": "Exit",
        "invalid_option": "Invalid option.",
        "try_again_manga_not_found": "Try again. Manga not found.",
        "overall_download_unit": "chapter",
    },
    "es": {
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
        "no_chapters_available": "⚠️ No hay capítulos disponibles en el idioma seleccionado ({}).",
        "available_chapters": "\n📖 Capítulos disponibles:",
        "chapter_prefix": "• Capítulo {}",
        "chapter_selection_mode_prompt": "Seleccione el modo de selección de capítulos:",
        "enter_range_option": "Ingrese el rango (ej: 1-10, todos)",
        "chapters_range_prompt": "Ingrese los capítulos para descargar (separados por espacio, 'all' o rango como XX-YY):",
        "chapter_selection_empty_error": "⚠️ La selección de capítulos no puede estar vacía.",
        "invalid_chapter_range_error": "⚠️ Rango de capítulos inválido. Los números deben ser positivos y el inicio <= fin.",
        "no_chapters_in_range": "⚠️ No se encontraron capítulos en el rango {}-{}.",
        "invalid_chapter_number_format_range": "⚠️ Formato de número de capítulo inválido en el rango.",
        "invalid_range_format": "⚠️ Formato de rango inválido. Use XX-YY.",
        "invalid_chapter_number_provided": "⚠️ Número(s) de capítulo(s) inválido(s) proporcionados: {}. Ingrese números positivos o 'all'.",
        "chapters_not_found": "⚠️ No se encontraron capítulo(s) en la lista proporcionada.",
        "no_chapters_selected": "⚠️ No se seleccionaron capítulos para descargar.",
        "downloading_images_chapter": "\n📥 Descargando imágenes para el Capítulo {}...",
        "search_image_server_error": "Error al buscar el servidor de imágenes: {}",
        "downloading_images": "🖼️ Descargando imágenes para el Capítulo {}",
        "download_successful": "✅ Imágenes descargadas exitosamente para el Capítulo {} en: {}",
        "download_failed": "⚠️ Falló la descarga de {}",
        "no_images_downloaded": "⚠️ No se descargaron imágenes para el Capítulo {}.",
        "overall_download_progress": "Progreso general de descarga",
        "waiting_next_chapter": "⏳ Esperando {} segundos antes de descargar el siguiente capítulo...",
        "continue_prompt": "\n¿Qué le gustaría hacer ahora?",
        "search_again_option": "Buscar otro manga",
        "exit_option": "Salir",
        "invalid_option": "Opción inválida.",
        "try_again_manga_not_found": "Intente nuevamente. Manga no encontrado.",
        "overall_download_unit": "capítulo",
    },
}

# Global variable to hold the selected language strings
selected_strings = STRINGS["pt-br"]  # Default to Portuguese

def select_language():
    """Prompts the user to select a language and sets the global string dictionary."""
    global selected_strings
    questions = [
        inquirer.List(
            'language_code',
            message=STRINGS["en"]["select_language_prompt"],  # Default prompt in English
            choices=LANGUAGE_CHOICES,
            carousel=True,
        ),
    ]
    answers = inquirer.prompt(questions)
    language_code = answers['language_code']
    selected_strings = STRINGS.get(language_code, STRINGS["en"])  # Fallback to English
    language_name = next((item[0] for item in LANGUAGE_CHOICES if item[1] == language_code), "Unknown")
    print(selected_strings["selected_language"].format(language_name))
    return language_code

def search_manga(title, session):
    """Searches for a manga by title and returns the ID and formatted name for saving."""
    params = {"title": title, "limit": 10}
    try:
        resp = session.get(f"{API_BASE}/manga", params=params, timeout=10)
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
        print(selected_strings["manga_found"].format(manga_title))
        return best_match["id"], manga_title.replace(' ', '_').replace(':', '')

    print(selected_strings["no_exact_match"].format(title))
    for score, manga_title, manga_id in sorted(similar_matches, reverse=True):
        print(f"🔹 {manga_title} (similarity: {score}%)")

    return None, None

def get_chapters(manga_id, lang, session):
    """Returns a list of available chapters in the specified language."""
    chapters = []
    offset = 0
    limit = CHAPTERS_PER_BATCH
    total_chapters = None

    with tqdm(total=total_chapters, desc=selected_strings["fetching_chapters"],
              unit=selected_strings["chapter"]) as pbar:
        while True:
            params = {
                "manga": manga_id,
                "translatedLanguage[]": lang,
                "order[chapter]": "asc",
                "limit": limit,
                "offset": offset
            }
            try:
                resp = session.get(f"{API_BASE}/chapter", params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if total_chapters is None:
                    total_chapters = data["total"]
                    pbar.total = total_chapters
            except requests.RequestException as e:
                print(selected_strings["search_chapters_error"].format(e))
                return []

            if not data["data"]:
                break

            for item in data["data"]:
                chap_id = item["id"]
                chap_number = item["attributes"].get("chapter", "N/A")
                chapters.append({"id": chap_id, "number": chap_number})
                pbar.update(1)

            offset += limit
            if offset >= total_chapters:
                break
    return chapters

def download_image(img_url, img_path, session):
    """Downloads an image with retry attempts in case of error."""
    for attempt in range(MAX_RETRIES):
        try:
            img_resp = session.get(img_url, stream=True, timeout=15)
            img_resp.raise_for_status()
            with open(img_path, 'wb') as f:
                for chunk in img_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.RequestException as e:
            print(selected_strings["download_failed"].format(img_url) +
                  f", attempt {attempt + 1}/{MAX_RETRIES}...")
            time.sleep(2)
    print(selected_strings["download_failed"].format(img_url))
    return False

def download_chapter_images(chapter_id, save_folder, chapter_number, session):
    """Downloads all images from a chapter and returns the list of image paths."""
    try:
        server_resp = session.get(f"{API_BASE}/at-home/server/{chapter_id}", timeout=10)
        server_resp.raise_for_status()
        server_data = server_resp.json()
    except requests.RequestException as e:
        print(selected_strings["search_image_server_error"].format(e))
        return [], None

    base_url = server_data["baseUrl"]
    chapter = server_data["chapter"]
    hash_val = chapter["hash"]
    data_files = chapter["data"]

    chapter_path = os.path.join(save_folder, f"Chapter_{chapter_number}_images")
    os.makedirs(chapter_path, exist_ok=True)

    img_paths = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for idx, img_file in enumerate(data_files):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(chapter_path, f"{idx + 1:03d}.jpg")
                if not os.path.exists(img_path):
                    img_url = f"{base_url}/data/{hash_val}/{img_file}"
                    futures.append(executor.submit(download_image, img_url, img_path, session))
                img_paths.append(img_path)

        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                      desc=selected_strings["downloading_images"].format(chapter_number)):
            pass
    return sorted(img_paths), chapter_path

def select_chapters_interactive(chapters):
    """Allows the user to interactively select chapters to download."""
    if not chapters:
        print(selected_strings["no_chapters_available"])
        return []

    choices = [(f"{selected_strings['chapter_prefix'].format(chap['number'])}", chap) for chap in
                chapters]
    questions = [
        inquirer.Checkbox(
            'selected_chapters',
            message=selected_strings["chapter_selection_mode_prompt"],
            choices=choices,
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers['selected_chapters']

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
    parser.add_argument("--chapters", "-c", type=str,
                        help="The chapters to download (e.g., '1 5 10', 'all', '20-25').")
    args = parser.parse_args()

    session = requests.Session()

    language_code = select_language()

    if args.manga:
        title = args.manga.strip()
        if not title:
            print(selected_strings["manga_title_empty_error"])
            return
    else:
        questions = [
            inquirer.Text('manga_title', message=selected_strings["manga_title_prompt"]),
        ]
        answers = inquirer.prompt(questions)
        if not answers or not answers['manga_title']:
            print(selected_strings["manga_title_empty_error"])
            return
        title = answers['manga_title'].strip()

    manga_id, manga_title_sanitized = search_manga(title, session)

    if manga_id:
        chapters = get_chapters(manga_id, language_code, session)
        if not chapters:
            print(selected_strings["no_chapters_available"].format(
                dict(LANGUAGE_CHOICES).get(language_code, "Unknown")))
            return

        print(selected_strings["available_chapters"])
        for chap in chapters:
            print(selected_strings["chapter_prefix"].format(chap['number']))

        if args.chapters:
            choice = args.chapters.strip()
            if not choice:
                print(selected_strings["chapter_selection_empty_error"])
                return
        else:
            questions = [
                inquirer.List('chapter_selection_mode',
                             message=selected_strings["chapter_selection_mode_prompt"],
                             choices=[
                                 (selected_strings["enter_range_option"], 'range'),
                             ]),
            ]
            selection_mode_answer = inquirer.prompt(questions)

            if selection_mode_answer['chapter_selection_mode'] == 'range':
                questions_range = [
                    inquirer.Text('chapters_range',
                                  message=selected_strings["chapters_range_prompt"]),
                ]
                range_answer = inquirer.prompt(questions_range)
                if not range_answer or not range_answer['chapters_range']:
                    print(selected_strings["chapter_selection_empty_error"])
                    return
                choice = range_answer['chapters_range'].strip()
            else:
                selected = select_chapters_interactive(chapters)
                chapters_to_download = selected
                choice = None  # To skip the range/single logic later

        chapters_to_download = []
        if choice is not None:
            if choice.lower() == 'all':
                chapters_to_download = chapters
            elif '-' in choice:
                try:
                    start_str, end_str = choice.split('-')
                    if start_str and end_str:
                        try:
                            start_chapter = float(start_str.strip())
                            end_chapter = float(end_str.strip())
                            if start_chapter <= 0 or end_chapter <= 0 or start_chapter > end_chapter:
                                print(selected_strings["invalid_chapter_range_error"])
                                return
                            else:
                                chapters_to_download = select_chapters_by_range(chapters, start_chapter,
                                                                                end_chapter)
                                if not chapters_to_download:
                                    print(selected_strings["no_chapters_in_range"].format(start_chapter,
                                                                                            end_chapter))
                                    return
                        except ValueError:
                            print(selected_strings["invalid_chapter_number_format_range"])
                            return
                    else:
                        raise ValueError(selected_strings["invalid_range_format"])
                except ValueError:
                    print(selected_strings["invalid_range_format"])
                    return
            else:
                chapter_numbers = choice.split()
                invalid_numbers = [num for num in chapter_numbers if
                                   not is_valid_chapter_number(num)]
                if invalid_numbers:
                    print(selected_strings["invalid_chapter_number_provided"].format(
                        ', '.join(invalid_numbers)))
                    return
                chapters_to_download = [chap for chap in chapters if
                                         chap['number'] in chapter_numbers]
                if not chapters_to_download and choice.lower() != 'all':
                    print(selected_strings["chapters_not_found"])
                    return
        elif not chapters_to_download:
            # If interactive selection was used and no chapters were selected
            if not args.chapters:
                print(selected_strings["no_chapters_selected"])
                return
            else:
                # If chapters were provided via CLI but interactive selection resulted in none
                pass  # Should have been handled by range/single logic

        if chapters_to_download:
            manga_download_dir = os.path.join(DOWNLOAD_BASE_DIR, manga_title_sanitized)
            os.makedirs(manga_download_dir, exist_ok=True)

            print("\n⚠️ Attention: The default value of MAX_THREADS has been set to 4 to respect MangaDex limits.")
            print("You can adjust the MAX_THREADS variable at the beginning of the script, but do so with caution.")
            print(f"A small delay of {CHAPTER_DOWNLOAD_DELAY} seconds will be added between downloading each chapter.")

            total_chapters_to_download = len(chapters_to_download)
            with tqdm(total=total_chapters_to_download, desc=selected_strings["overall_download_progress"],
                      unit=selected_strings["overall_download_unit"]) as overall_pbar:
                for i, chap in enumerate(chapters_to_download):
                    print(selected_strings["downloading_images_chapter"].format(chap['number']))
                    image_paths, temp_dir = download_chapter_images(chap["id"], manga_download_dir,
                                                                    chap["number"], session)
                    if image_paths:
                        print(selected_strings["download_successful"].format(chap['number'], temp_dir))
                        # Clean up temporary image directory (optional)
                        # for img_path in image_paths:
                        #     try:
                        #         os.remove(img_path)
                        #     except OSError as e:
                        #         print(f"Error deleting temporary image {img_path}: {e}")
                        # try:
                        #     os.rmdir(temp_dir)
                        # except OSError as e:
                        #     print(f"Error deleting temporary directory {temp_dir}: {e}")
                    else:
                        print(selected_strings["no_images_downloaded"].format(chap['number']))

                    overall_pbar.update(1)

                    if i < len(chapters_to_download) - 1:  # Add delay between chapters
                        print(selected_strings["waiting_next_chapter"].format(CHAPTER_DOWNLOAD_DELAY))
                        time.sleep(CHAPTER_DOWNLOAD_DELAY)

            if not args.manga:  # Only ask to search again if not run from CLI
                while True:
                    questions_again = [
                        inquirer.List('continue_option',
                                      message=selected_strings["continue_prompt"],
                                      choices=[
                                          (selected_strings["search_again_option"], 'search_again'),
                                          (selected_strings["exit_option"], 'exit')
                                      ]),
                    ]
                    continue_answer = inquirer.prompt(questions_again)
                    if continue_answer['continue_option'] == 'search_again':
                        break
                    elif continue_answer['continue_option'] == 'exit':
                        return
                    else:
                        print(selected_strings["invalid_option"])

    else:
        print(selected_strings["try_again_manga_not_found"])

if __name__ == "__main__":
    main()
