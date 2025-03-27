# MDex - MangaDex Downloader

Python script that downloads manga chapters from MangaDex (via API), automatically creates chapter PDFs, and supports both interactive and CLI operation.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Command Line Arguments](#command-line-arguments)
- [Configuration](#configuration)
- [License](#license)
- [Status](#status)
- [Contributing](#contributing)
- [Contact](#contact)


## Features

* **Manga Search**: Searches MangaDex for manga by title using fuzzy matching.
* **Similar Title Suggestions**: Lists similar manga titles if an exact match isn't found.
* **Multilingual Support**: User interface available in Portuguese (pt-br), English (en), and Spanish (es).
* **Language-Specific Downloads**: Downloads chapters in the user-selected language.
* **Chapter Listing**: Lists available chapters for the selected manga and language.
* **Flexible Chapter Selection**: Download specific chapters, a range of chapters (e.g., `10-15.5`), or all available chapters (`all`/`todos`).
* **Automatic PDF Creation**: Automatically generates a single PDF file for each successfully processed chapter.
* **Intelligent Page Orientation**: PDF pages automatically adapt orientation (Portrait/Landscape) to best fit each individual image.
* **Parallel Image Downloads**: Downloads images within a chapter concurrently using multiple threads (as an intermediate step before PDF creation).
* **Retry Mechanism**: Automatically retries failed image downloads (intermediate step).
* **Automatic Cleanup**: Removes original image files and their folders after successful PDF generation for a chapter, saving disk space.
* **Organized PDF Output**: Saves generated PDF files directly into the manga's main download folder (within the specified base directory).
* **Configurable Delay**: Includes a configurable delay between processing different chapters to respect API limits.
* **Interactive Mode**: User-friendly prompts guide the user through language selection, manga search, and chapter selection.
* **Command-Line Operation**: Supports non-interactive use via command-line arguments for scripting or batch processing.
* **Configurable Directory**: Specify a custom base download directory via command-line argument.

## Requirements

* Python 3.6+

* Required Python Libraries:
    * `requests` (for API communication)
    * `fuzzywuzzy` (for title matching)
    * `tqdm` (for progress bars)
    * `inquirer` (for interactive prompts)
    * `Pillow` (PIL Fork - imported, usage context to be verified if needed for future image processing)
    * `fpdf2` (for automatic PDF generation)
    * `python-levenshtein` (improves `fuzzywuzzy` performance significantly)

*Note: Installing `python-levenshtein` might require C build tools on some systems.*

You can install dependencies using a `requirements.txt` file (see Installation). Create a `requirements.txt` file with the package names listed above.


## Installation

1.  Clone this repository (replace URL if needed):
    ```bash
    git clone https://github.com/victorvernier/MDex.git
    ```

2.  Navigate to the project directory:
    ```bash
    cd MDex
    ```

3.  Install the required dependencies using the `requirements.txt` file you created:
    ```bash
    pip install -r requirements.txt
    ```
    *Optional: If you included `python-levenshtein` in `requirements.txt`, ensure you have the necessary build tools if installation fails.*


## Usage

### Interactive Mode

Simply run the script without any arguments:

```bash
python MDex.py
```
Follow the prompts in the terminal to select the language, search for the manga title, and choose the chapters you want to download.


## Command Line Arguments

### For non-interactive use, provide arguments directly:

```
python MDex.py [OPTIONS]
```

### Options:

* ```-m MANGA```, ```--manga MANGA```: Specifies the title of the manga to download (enclose in quotes if it contains spaces).

* ```-c CHAPTERS```, ```--chapters CHAPTERS```: Specifies the chapters to download. Use space separation for multiple chapters, hyphens for ranges, or ```all/todos``` for all chapters (e.g., ```"1 5.5 10-15 all"```).

* ```-l LANG```, ```--lang LANG```: Specifies the language code for download (e.g., ```pt-br```, ```en```, ```es```). If omitted, interactive selection will be used.

* ```-d DIR```, ```--dir DIR```: Specifies the base directory for downloads (default: ```Downloads```).

### Example:
```
python MDex.py --manga "Solo Leveling" --lang en --chapters "100-110" --dir "./MangaCollection"
```
This command will attempt to download chapters 100 through 110 of "Solo Leveling" in English into the  directory, non-interactively.```./MangaCollection```


## Configuration

Script behavior can be adjusted by modifying the global constants at the top of the `MDex.py` file:

* `API_BASE`: MangaDex API endpoint URL.
* `DOWNLOAD_BASE_DIR`: Default base directory for downloads if the `--dir` argument is not used.
* `MAX_RETRIES`: Number of times to retry a failed image download attempt.
* `MAX_THREADS`: Maximum number of concurrent image downloads within a chapter. *Adjust cautiously; higher values increase load and risk of rate-limiting.*
* `CHAPTER_DOWNLOAD_DELAY`: Delay in seconds between finishing one chapter's processing and starting the next. *Adjust cautiously; affects rate-limiting.*
* `CHAPTERS_PER_BATCH`: Number of chapters to fetch per API request when listing available chapters.
* `ASSUMED_DPI`: Assumed dots-per-inch value used for converting image pixel dimensions to points when creating PDF pages. *Affects image scaling within the PDF page.*

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/victorvernier/MDex/blob/main/LICENSE) file for details.


## Status

* Feature Complete


## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/victorvernier/MDex/issues). If you'd like to contribute code, please fork the repository and submit a pull request.

## Contact

