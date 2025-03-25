# MDex - Manga Downloader

This is a Python script that allows you to download manga chapters from MangaDex and optionally convert them to PDF files for easier reading.

## Requirements

* Python 3.6+
* Python Libraries:
    * `requests`
    * `fuzzywuzzy`
    * `tqdm`
    * `fpdf2` (for PDF creation)
    * `Pillow` (PIL Fork)

## Installation

1.  Clone this repository:

    ```
    git clone https://github.com/victorvernier/MDex.git
    ```

2.  Navigate to the project directory:

    ```
    cd MDex
    ```

3.  Install the dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

1.  Run the script:

    ```
    python MDex.py
    ```

2.  Follow the instructions in the terminal to search and download manga.

## Command Line Arguments:

    python MDex.py --manga "Manga Title" --chapters "1 5 10-12 all" 

## Features

* Manga Search: Searches for manga by title using fuzzy matching.
* Chapter List: Lists the available chapters in English.
* High-Resolution Downloads: Downloads manga chapter images in high resolution.
* Specific Chapter Download: Option to download specific chapters, a range of chapters, or all available chapters.
* Organized Folders: Creates a dedicated folder for each manga in the Downloads directory, with a subfolder for each chapter containing the downloaded images.
* PDF Generation: (New) Generates a PDF file for each downloaded chapter, optimized for reading on mobile devices and computers with automatic page orientation and image fitting.
* Similar Manga Titles: Lists similar manga titles if an exact match is not found.
* Download Delay: Includes a delay between chapter downloads to respect MangaDex server limits.
* Search Again: Option to search for another manga or exit the program after downloading.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests to suggest improvements, report bugs, or add new 1  features. Please ensure your code follows the project's coding style and includes appropriate tests if you are adding new functionality.
