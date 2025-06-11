#!/usr/bin/env python3
"""
Script to process a masked diff report and generate a human-readable comparison report using Grok API.
Loads API key from .env file.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import re
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class DiffReportProcessor:
    """Class to process masked diff report and generate readable summary using Grok API."""
    
    def __init__(self, input_file: str, output_dir: str = "output"):
        self.input_path = Path(input_file)
        self.output_path = Path(output_dir)
        self.output_path.mkdir(exist_ok=True)
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        if not self.client.api_key:
            logger.error("GROQ_API_KEY not found in environment variables or .env file")
            sys.exit(1)
    
    def read_diff_file(self) -> list[dict]:
        """Read the masked diff file and extract comparison sections."""
        if not self.input_path.is_file():
            logger.error(f"Input file not found: {self.input_path}")
            sys.exit(1)
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into comparison sections
        sections = []
        current_section = None
        diff_lines = []
        header = []
        
        for line in content.splitlines():
            if line.startswith("Comparison:"):
                if current_section:
                    current_section["diff"] = "\n".join(diff_lines)
                    sections.append(current_section)
                current_section = {
                    "comparison": line,
                    "header": header[-2:] if header else [],
                    "diff": ""
                }
                diff_lines = []
            elif line.startswith("Document Comparison Report") or line.startswith("Generated:"):
                header.append(line)
            elif current_section and line.strip():
                diff_lines.append(line)
        
        if current_section and diff_lines:
            current_section["diff"] = "\n".join(diff_lines)
            sections.append(current_section)
        
        logger.info(f"Extracted {len(sections)} comparison sections")
        return sections
    
    def generate_readable_diff(self, diff_text: str, comparison: str) -> str:
        """Use Grok API to convert diff text into a readable summary."""
        prompt = f"""
You are an expert in summarizing document differences in a clear, human-readable format. Below is a unified diff from a masked comparison report of patient registration forms, showing changes between two documents ({comparison}). The PII has been masked (e.g., <PERSON>, <PHONE_NUMBER>). Your task is to convert this diff into a concise, natural language summary, focusing on meaningful field changes (e.g., Date of Birth, Address, Diagnosis). Use bullet points to list each change, and group by field where possible. Ignore minor formatting differences (e.g., extra spaces) unless they affect meaning. If no significant changes exist, state that clearly.

Diff:
```
{diff_text}
```

Example output:
- **Date of Birth**: Changed from <DATE_TIME> to <DATE_TIME>.
- **Address**: Updated from <LOCATION> to <LOCATION>.
- **Diagnosis**: Changed from Hypertension to Asthma.

Provide only the bullet-point summary, no additional commentary.
"""
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a precise summarizer of document differences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for {comparison}")
            return summary
        except Exception as e:
            logger.error(f"Failed to generate summary for {comparison}: {e}")
            return "Error generating summary."
    
    def process_report(self):
        """Process the diff file and generate a readable report."""
        sections = self.read_diff_file()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_path / f"readable_diff_report_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Readable Comparison Report\nGenerated: {datetime.now()}\n\n")
            
            for section in sections:
                comparison = section["comparison"]
                diff_text = section["diff"]
                f.write(f"{comparison}\n{'=' * 80}\n")
                
                if "No Differences Found" in diff_text:
                    f.write("No significant differences detected.\n")
                else:
                    summary = self.generate_readable_diff(diff_text, comparison)
                    f.write(f"{summary}\n")
                f.write(f"\n{'=' * 80}\n\n")
        
        logger.info(f"Readable report saved to {output_file}")
        print(f"✅ Readable report generated! Check {output_file}")

def main():
    """Main function to run the script."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate readable comparison report from masked diff file")
    parser.add_argument("input_file", help="Path to masked diff report file")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    args = parser.parse_args()
    
    processor = DiffReportProcessor(args.input_file, args.output)
    processor.process_report()

if __name__ == "__main__":
    main()