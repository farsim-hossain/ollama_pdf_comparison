# IRS Form 1042 Image Comparison

This repository contains a Python script that compares multiple IRS Form 1042 images (JPEG or PNG format) pairwise using Ollama's `llava:latest` vision model. The script identifies key differences in fields, instructions, or structure between pairs of images and saves the results to a text file (`form_1042_image_comparison.txt`). This tool is useful for tracking changes across different versions of Form 1042 (e.g., 1994, 2004, 2012).

## Prerequisites

Before running the script, ensure you have the following installed and configured on your Windows machine:
- Python 3.8 or higher
- Ollama
- Required Python packages (`ollama`)
- Image files of Form 1042 (JPEG or PNG) with "f1042" in their filenames

## Setup Instructions

Follow these steps to set up and run the script.

### 1. Install Python
1. Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/).
2. During installation, check "Add Python to PATH".
3. Verify installation:
   ```cmd
   python --version
   ```

### 2. Install Ollama
1. Download Ollama for Windows from [Ollama's official site](https://ollama.com/download).
2. Run the installer and follow the prompts.
3. Verify Ollama installation:
   ```cmd
   ollama --version
   ```

### 3. Download the Llava Model
1. Pull the `llava:latest` model using Ollama:
   ```cmd
   ollama pull llava:latest
   ```
2. Verify the model is downloaded:
   ```cmd
   ollama list
   ```

### 4. Set Up the Project
1. Clone or download this repository to your local machine:
   ```cmd
   git clone https://github.com/farsim-hossain/ollama_pdf_comparison.git
   cd your-repo-name
   ```


2. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

4. Install required Python packages:
   ```cmd
   pip install ollama
   ```

### 5. Prepare Input Images
1. Create an `input_images` directory in the project root:
   ```cmd
   mkdir input_images
   ```
2. Place your Form 1042 image files (JPEG or PNG) in the `input_images` directory. Ensure filenames include "f1042" (case-insensitive), e.g., `f1042--1994.jpg`, `f1042--2004.png`, `f1042--2012.jpg`.
   - Example: Obtain images by converting Form 1042 PDFs to JPEG/PNG using tools like Adobe Acrobat, online converters, or a script with `pdf2image`.

### 6. Start the Ollama Server
1. Open a new terminal and start the Ollama server:
   ```cmd
   ollama serve
   ```
   Keep this terminal running while executing the script.

## Running the Script

1. Ensure the virtual environment is activated:
   ```cmd
   venv\Scripts\activate
   ```

2. Run the script:
   ```cmd
   python image_comparison.py
   ```

3. The script will:
   - Scan the `input_images` directory for files with "f1042" in their names and `.jpg`, `.jpeg`, or `.png` extensions.
   - Compare all pairs of images using the `llava:latest` model.
   - Save the results to `form_1042_image_comparison.txt` in the project root.

## Expected Output
The `form_1042_image_comparison.txt` file will contain pairwise comparisons, each with a numbered list of 5-7 key differences. Example:
```
Comparison between f1042--1994.jpg and f1042--2004.png:
1. Header Information: The first image has no website link, while the second image includes a basic IRS link.
2. Identification Number: The first image uses "Taxpayer identification number," while the second image uses "Employer identification number."
3. Filing Methods: The first image supports paper and magnetic tape, while the second image introduces electronic filing options.
4. Tax Liability: The first image has simpler totals, while the second image adds monthly breakdowns.
5. Signature Section: The first image has a basic signature, while the second image includes preparer details.

Comparison between f1042--1994.jpg and f1042--2012.jpg:
...
```


## For Running PII Scripts 


---

## 📦 Installation Instructions (for Windows)

These instructions assume you already have Python installed.

---

### 🧰 1. Set Up a Virtual Environment (Optional but Recommended)

Open **Command Prompt** or **PowerShell** and run:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 📦 2. Install Python Packages

Install the required packages using `pip`:

```bash
pip install python-dotenv ollama groq pytesseract pillow presidio-analyzer presidio-anonymizer
```

Alternatively, you can create a `requirements.txt` file with:

```txt
python-dotenv
ollama
groq
pytesseract
pillow
presidio-analyzer
presidio-anonymizer
```

And install all at once:

```bash
pip install -r requirements.txt
```

---

### 🔤 3. Install Tesseract OCR (Windows)

1. **Download the installer**:

   * From the official repo: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
   * Direct installer link (latest): [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) (recommended for Windows)

2. **Run the installer**:

   * During installation, make sure the "Add to system PATH" checkbox is selected.
   * Note the install location (default: `C:\Program Files\Tesseract-OCR`).

3. **(If not added automatically)** Add Tesseract to your system PATH manually:

   * Press `Win + S` → search for "Environment Variables"
   * Edit `PATH` → Add: `C:\Program Files\Tesseract-OCR`
   * Click OK to save.

4. **Verify installation**:

   ```bash
   tesseract --version
   ```

---



