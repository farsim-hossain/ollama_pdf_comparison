# IRS Form 1042 Image Comparison

This repository contains a Python script (`compare_form_1042_images.py`) that compares multiple IRS Form 1042 images (JPEG or PNG format) pairwise using Ollama's `llava:latest` vision model. The script identifies key differences in fields, instructions, or structure between pairs of images and saves the results to a text file (`form_1042_image_comparison.txt`). This tool is useful for tracking changes across different versions of Form 1042 (e.g., 1994, 2004, 2012).

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
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```
   Replace `your-username` and `your-repo-name` with your GitHub username and repository name.

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
   python compare_form_1042_images.py
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

## Troubleshooting
- **Ollama Server Not Running**:
  - Ensure `ollama serve` is active in a separate terminal.
  - Check if `llava:latest` is listed:
    ```cmd
    ollama list
    ```
- **No Images Found**:
  - Verify that `input_images` contains at least two image files with "f1042" in their names and `.jpg`, `.jpeg`, or `.png` extensions.
- **Memory Issues**:
  - The vision model requires significant RAM (8GB+ recommended). Close other applications if the script crashes.
- **Image Quality**:
  - Ensure images are clear and readable. Low-quality or scanned images may reduce model accuracy.
- **Python Package Errors**:
  - Reinstall dependencies:
    ```cmd
    pip install ollama
    ```

## Notes
- **Image-Based Comparison**: The script compares images directly, not PDFs. Convert PDFs to images using tools like `pdf2image` if needed.
- **Single Page Comparison**: Each image is assumed to represent one page (e.g., the first page of a Form 1042 PDF).
- **Local Processing**: Ollama runs locally, requiring sufficient CPU/GPU resources but no internet-based API calls.
- **Customizations**:
  - To use a different Ollama model, modify the `model` parameter in `compare_image_pair` (e.g., `granite3.2-vision:latest`).
  - To output results in Excel, modify the script to parse the numbered lists into a `pandas` DataFrame.
  - To focus on specific form sections, adjust the prompt in `compare_image_pair`.

## License
[Add your preferred license, e.g., MIT License]

## Contact
For issues or contributions, open an issue or pull request on this repository.