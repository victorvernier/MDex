# MDex - Manga Downloader

**A Python script for downloading manga chapters from MangaDex, with the option to convert them to PDF files for easier reading.**

## Overview

MDex is a command-line tool written in Python that simplifies downloading manga chapters from the MangaDex API, offering features like manga searching, chapter selection, organized downloads, and optional PDF conversion for convenient reading on various devices.

## Features

* **Manga Search:**
    * Fuzzy matching allows you to find manga even with slight variations in the title.
    * Displays similar manga titles when an exact match isn't found, improving search accuracy.
* **Chapter Management:**
    * Lists available chapters in the selected language.
    * Download specific chapters, a range (e.g., 1-10), or all available chapters.
* **High-Quality Downloads:**
    * Downloads manga chapter images in high resolution.
* **Organized File Structure:**
    * Creates a dedicated folder for each manga in the `Downloads` directory.
    * Each chapter is placed in its own subfolder, keeping your downloads organized.
* **PDF Generation (Optional):**
    * Generates a PDF file for each downloaded chapter.
    * PDFs are optimized for reading on mobile devices and computers.
    * Automatic page orientation and image fitting for a better reading experience.
* **Language Selection:**
    * Choose the download language.
* **MangaDex Respect:**
    * Includes a delay between chapter downloads to comply with MangaDex API limits.
* **Post-Download Options:**
    * Option to search for another manga or exit the program after completing a download.

## Requirements

* Python 3.6 or higher
* Python Libraries:
    * `requests`
    * `fuzzywuzzy`
    * `tqdm`
    * `fpdf2`
    * `Pillow` (PIL Fork)
    * `inquirer`

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/victorvernier/MDex.git](https://github.com/victorvernier/MDex.git)
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd MDex
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the script:**

    ```bash
    python MDex.py
    ```

2.  **Follow the prompts in the terminal to search for and download manga.**

## Command Line Arguments

You can also use command-line arguments to automate manga selection and chapter downloads:

```bash
python MDex.py --manga "Manga Title" --chapters "1 5 10-12 all"

## Okay, let's refine the "Features" and "Contribution" sections to be more polished and informative in English.

Here's a revised version:

## Features
* Manga Search: Effortlessly find manga by title using intelligent fuzzy matching.
* Chapter List: Displays a clear list of available chapters in the selected language.
* High-Resolution Downloads: Obtain manga chapter images in their original, high-resolution quality.
* Flexible Chapter Selection: Choose to download specific chapters, define a range (e.g., 1-10), or download all available chapters.
* Organized Downloads: Manga are neatly organized into dedicated folders within the Downloads directory, with each chapter residing in its own subfolder containing the downloaded images.
* PDF Generation (Optional): Generate a single PDF file for each downloaded chapter, optimized for comfortable reading on mobile devices and computers with automatic page orientation and image fitting.
* Similar Manga Suggestions: If an exact manga title match isn't found, a list of similar titles is provided to aid your search.
* Respectful Download Practices: Implements a delay between chapter downloads to adhere to MangaDex server rate limits.
* Post-Download Actions: Offers the choice to search for another manga or exit the application upon completion of a download.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests to suggest improvements, report bugs, or add new 1  features. Please ensure your code follows the project's coding style and includes appropriate tests if you are adding new functionality.
