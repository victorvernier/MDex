# MDex - MangaDex Downloader

A Python script to search for and download manga chapters from MangaDex via its API, using an interactive command-line interface or direct command-line arguments.


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

* **Flexible Chapter Selection**: Download specific chapters, a range of chapters (e.g., `10-15.5`), or all available chapters (`all`).

* **Parallel Downloads**: Downloads images within a chapter concurrently using multiple threads for potentially faster speeds.

* **Organized Output**: Creates a dedicated folder for each manga (within the specified download directory), with subfolders for each chapter containing the downloaded images.

* **Retry Mechanism**: Automatically retries failed image downloads a configurable number of times.

* **Configurable Delay**: Includes a configurable delay between downloading different chapters to respect MangaDex API limits.

* **Interactive Mode**: User-friendly prompts guide the user through language selection, manga search, and chapter selection if no command-line arguments are provided.

* **Command-Line Operation**: Supports non-interactive use via command-line arguments for batch processing or scripting.

* **Configurable Directory**: Specify a custom base download directory via command-line argument.

## Requirements

* Python 3.6+

* Required Python Libraries:
    * `requests` (for API communication)
    * `fuzzywuzzy` (for title matching)
    * `tqdm` (for progress bars)
    * `inquirer` (for interactive prompts)
    * `Pillow` (PIL Fork - imported, usage context to be verified if needed for future image processing)

* Optional Library (Recommended):
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

* ```-c CHAPTERS```, ```--chapters CHAPTERS```: Specifies the chapters to download. Use space separation for multiple chapters, hyphens for ranges, or ```all``` for all chapters (e.g., ```"1 5.5 10-15 all"```).

* ```-l LANG```, ```--lang LANG```: Specifies the language code for download (e.g., ```pt-br```, ```en```, ```es```). If omitted, interactive selection will be used.

* ```-d DIR```, ```--dir DIR```: Specifies the base directory for downloads (default: ```Downloads```).

### Example:
```
python MDex.py --manga "Solo Leveling" --lang en --chapters "100-110" --dir "./MangaCollection"
```
This command will attempt to download chapters 100 through 110 of "Solo Leveling" in English into the  directory, non-interactively.```./MangaCollection```


## Configuration

Script behavior can be adjusted by modifying the global constants at the top of the ```MDex.py``` file:

* ```API_BASE```: MangaDex API endpoint.

* ```DOWNLOAD_BASE_DIR```: Default download directory if ```--dir``` is not used.

* ```MAX_RETRIES```: Number of times to retry a failed image download.

* ```MAX_THREADS```: Maximum number of concurrent image downloads within a chapter. *Adjust cautiously*.

* ```CHAPTER_DOWNLOAD_DELAY```: Delay in seconds between finishing one chapter and starting the next. *Adjust cautiously*.

* ```CHAPTERS_PER_BATCH```: Number of chapters to fetch per API request when listing chapters.

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/victorvernier/MDex/blob/main/LICENSE) file for details.


## Status

* Feature Complete


## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/victorvernier/MDex/issues). If you'd like to contribute code, please fork the repository and submit a pull request.

## Contact

