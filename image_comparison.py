import os
import base64
import ollama
from pathlib import Path
from itertools import combinations

def encode_image(image_path: str) -> str:
    """Encode an image file to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""

def compare_image_pair(img1_path: str, img2_path: str, model: str = "llava:latest") -> str:
    """Compare two images using Ollama's vision model and return the comparison result."""
    try:
        base64_image1 = encode_image(img1_path)
        base64_image2 = encode_image(img2_path)

        if not base64_image1 or not base64_image2:
            return f"Comparison between {Path(img1_path).name} and {Path(img2_path).name}: Failed to encode images.\n"

        img1_name = Path(img1_path).name
        img2_name = Path(img2_path).name
        prompt = f"""
You are a helpful assistant tasked with comparing two images of IRS Form 1042 PDFs ({img1_name} and {img2_name}). Analyze the content of both images and identify 5-7 key differences in a clear, structured format. Focus on changes in fields, instructions, structure, or significant elements. Ignore minor formatting or stylistic changes. Return the differences as a numbered list, with each item describing the difference and specifying what changed between the two versions.

Example output:
1. Header Information: The first image has no website link, while the second image includes a link to www.irs.gov/form1042.
2. Identification Number: The first image uses "Taxpayer identification number," while the second image uses "Employer identification number."

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

        return f"Comparison between {img1_name} and {img2_name}:\n{response['message']['content']}\n"

    except Exception as e:
        print(f"Error comparing {img1_path} and {img2_path} with Ollama: {e}")
        return f"Error comparing {Path(img1_path).name} and {Path(img2_path).name}: {e}\n"

def process_and_compare_images(input_dir: str, output_file: str = "form_1042_image_comparison.txt"):
    """Compare all image files pairwise in the given input directory."""
    image_files = [f for f in Path(input_dir).glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png"] and "f1042" in f.name.lower()]

    if len(image_files) < 2:
        print("At least two Form 1042 image files are required for comparison.")
        return

    comparisons = []
    for img1, img2 in combinations(image_files, 2):
        print(f"Comparing {img1.name} and {img2.name}...")
        comparison = compare_image_pair(str(img1), str(img2))
        comparisons.append(comparison)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(comparisons))
        print(f"Comparison results saved to {output_file}")
    except Exception as e:
        print(f"Error saving comparison to {output_file}: {e}")

def main():
    input_dir = "/content/input_pdfs"  # Replace with your actual folder path
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return

    process_and_compare_images(input_dir)

if __name__ == "__main__":
    main()
