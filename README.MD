# **MDex - Manga Downloader** 📖  

> A Python script for downloading manga chapters from **MangaDex**, with an option to convert them into PDF files for easier reading.  

## **📌 Overview**  

**MDex** is a command-line tool written in Python that simplifies downloading manga chapters from the **MangaDex API**.  
It offers features such as **intelligent search**, **custom chapter selection**, **automatic download organization**, and an **optional PDF conversion** for an enhanced reading experience.  

---

## **✨ Features**  

✅ **Intelligent Manga Search**  
- Uses **fuzzy matching** to find manga titles even with minor variations.  
- Suggests similar titles when an exact match isn't found.  

✅ **Chapter Management**  
- Lists all available chapters in the selected language.  
- Allows downloading specific chapters, a custom range (e.g., `1-10`), or all available chapters.  

✅ **High-Quality Downloads**  
- Downloads chapter images in **original high resolution**, preserving image quality.  

✅ **Organized File Structure**  
- Creates a dedicated folder for each manga inside the `Downloads` directory.  
- Each chapter is stored in its own subfolder, ensuring an organized collection.  

✅ **PDF Generation (Optional)**  
- Creates a **single PDF file** for each downloaded chapter.  
- PDFs are optimized for mobile and desktop reading, with **automatic page orientation and image fitting**.  

✅ **Language Selection**  
- Allows choosing the preferred language before downloading.  

✅ **MangaDex API Compliance**  
- Implements a delay between downloads to **respect API rate limits and prevent bans**.  

✅ **Post-Download Actions**  
- After a download is completed, you can either search for another manga or exit the program.  

---

## **📦 Requirements**  

✔ **Python 3.6 or later**  
✔ Required Python Libraries:  

```bash
pip install -r requirements.txt


## **📦 List of Dependencies**  

- `requests`  
- `fuzzywuzzy`  
- `tqdm`  
- `fpdf2`  
- `Pillow` (PIL Fork)  
- `inquirer`  

---

## **⚙ Installation**  

### 1️⃣ Clone the repository:  

```bash
git clone https://github.com/victorvernier/MDex.git

## **⚙ Installation**  

### 2️⃣ Navigate to the project directory:  

```bash
cd MDex

###3️⃣ Install dependencies:

pip install -r requirements.txt

## **🚀 Usage**  

### 2️⃣ Follow the prompts in the terminal to search and download manga.  

---

## **🔹 Command Line Arguments**  

You can automate manga selection and chapter downloads using command-line arguments:  

```bash
python MDex.py --manga "Manga Title" --chapters "1 5 10-12 all"

## **💡 Contribution**  

Contributions are welcome! Feel free to open **issues** or submit **pull requests** to suggest improvements, report bugs, or add new features.  
Please ensure your code follows the project's style and includes appropriate tests for new functionalities.  

📩 **Questions? Suggestions? Feel free to reach out!**  
