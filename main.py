import os
from pathlib import Path
from pdf2image import convert_from_path
import base64
import ollama
from itertools import combinations

def encode_image(image_path: str) -> str:
    """Encode an image file to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""

def pdf_to_images(pdf_path: str, output_dir: str, max_pages: int = 1) -> list:
    """Convert PDF pages to images and return their paths."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
        image_paths = []
        pdf_name = Path(pdf_path).stem
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"{pdf_name}_page_{i+1}.jpg")
            image.save(image_path, "JPEG")
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        print(f"Error converting PDF {pdf_path} to images: {e}")
        return []

def compare_pdf_pair(pdf1_path: str, pdf2_path: str, model: str = "llava:latest") -> str:
    """Compare two PDFs using Ollama's vision model and return the comparison result."""
    try:
        temp_dir = "temp_images"
        pdf1_images = pdf_to_images(pdf1_path, temp_dir, max_pages=1)
        pdf2_images = pdf_to_images(pdf2_path, temp_dir, max_pages=1)

        if not pdf1_images or not pdf2_images:
            print(f"Failed to convert one or both PDFs: {pdf1_path}, {pdf2_path}")
            return f"Comparison between {Path(pdf1_path).name} and {Path(pdf2_path).name}: Failed to process images.\n"

        base64_image1 = encode_image(pdf1_images[0])
        base64_image2 = encode_image(pdf2_images[0])

        if not base64_image1 or not base64_image2:
            print(f"Failed to encode images for {pdf1_path} or {pdf2_path}")
            return f"Comparison between {Path(pdf1_path).name} and {Path(pdf2_path).name}: Failed to encode images.\n"

        pdf1_name = Path(pdf1_path).name
        pdf2_name = Path(pdf2_path).name
        prompt = f"""
You are a helpful assistant tasked with comparing two images of IRS Form 1042 PDFs ({pdf1_name} and {pdf2_name}). Analyze the content of both images and identify 5-7 key differences in a clear, structured format. Focus on changes in fields, instructions, structure, or significant elements. Ignore minor formatting or stylistic changes. Return the differences as a numbered list, with each item describing the difference and specifying what changed between the two versions.

Example output:
1. Header Information: The first PDF has no website link, while the second PDF includes a link to www.irs.gov/form1042.
2. Identification Number: The first PDF uses "Taxpayer identification number," while the second PDF uses "Employer identification number."

Provide only the numbered list, without additional explanation.
"""

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64_image1, base64_image2]
                }
            ]
        )

        return f"Comparison between {pdf1_name} and {pdf2_name}:\n{response['message']['content']}\n"

    except Exception as e:
        print(f"Error comparing {pdf1_path} and {pdf2_path} with Ollama: {e}")
        return f"Error comparing {Path(pdf1_path).name} and {Path(pdf2_path).name}: {e}\n"

def process_and_compare_pdfs(input_dir: str, output_file: str = "form_1042_vision_comparison.txt"):
    """Process all Form 1042 PDFs in the input directory and compare them pairwise."""
    pdf_files = [f for f in Path(input_dir).glob("*.pdf") if "f1042" in f.name.lower()]

    if len(pdf_files) < 2:
        print("At least two Form 1042 PDFs are required for comparison.")
        return

    comparisons = []
    for pdf1, pdf2 in combinations(pdf_files, 2):
        pdf1_path = str(pdf1)
        pdf2_path = str(pdf2)
        print(f"Comparing {pdf1.name} and {pdf2.name}...")
        comparison = compare_pdf_pair(pdf1_path, pdf2_path)
        comparisons.append(comparison)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(comparisons))
        print(f"Comparison results saved to {output_file}")
    except Exception as e:
        print(f"Error saving comparison to {output_file}: {e}")

def main():
    input_dir = "/content/input_pdfs"
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return

    process_and_compare_pdfs(input_dir)

if __name__ == "__main__":
    main()
