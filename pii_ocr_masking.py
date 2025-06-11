#!/usr/bin/env python3
"""
App to parse JPG/PNG document images in a directory, compare content line by line,
and generate two comparison reports: one unmasked and one with PII masked (including SSNs, emails, and phone numbers).
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import difflib
import pytesseract
from PIL import Image
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, OperatorConfig

# Custom filter to suppress Presidio language warnings
class PresidioWarningFilter(logging.Filter):
    def filter(self, record):
        return "Recognizer not added to registry" not in record.getMessage()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logging.getLogger().addFilter(PresidioWarningFilter())

class DocumentProcessor:
    """Class to process document images, compare content, and mask PII."""
    
    def __init__(self, input_dir: str, output_dir: str = "output"):
        self.input_path = Path(input_dir)
        self.output_path = Path(output_dir)
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize Presidio
        self.analyzer, self.anonymizer = self._setup_presidio()
    
    def _setup_presidio(self):
        """Setup Presidio Analyzer and Anonymizer with spaCy (en_core_web_lg) and custom patterns."""
        try:
            config = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
            }
            provider = NlpEngineProvider(nlp_configuration=config)
            nlp_engine = provider.create_engine()
            
            # Define custom regex patterns
            ssn_pattern = Pattern(
                name="SSN_PATTERN",
                regex=r'\b\d{3}-\d{2}-\d{4}\b',
                score=0.9
            )
            phone_pattern = Pattern(
                name="PHONE_PATTERN",
                regex=r'\(?\d{3}\)?[\s-]?\d{3}-\d{4}\b',
                score=0.95
            )
            email_pattern = Pattern(
                name="EMAIL_PATTERN",
                regex=r'\b[\w\.-]+[@\s@][\w\.-]+\.\w+\b',
                score=0.8
            )
            email_structured_pattern = Pattern(
                name="EMAIL_STRUCTURED_PATTERN",
                regex=r'[\[\(](?:mailto:)?\s*([\w\.-]+@[\w\.-]+\.\w+)\s*[\]\)]',
                score=1.0
            )
            name_pattern = Pattern(
                name="NAME_PATTERN",
                regex=r'Name:\s*([A-Za-z\s\.]+?)\s*(?=\n|$)',
                score=1.0
            )
            policy_pattern = Pattern(
                name="POLICY_PATTERN",
                regex=r'Insurance Policy Number:\s*(IN-\d{8})\b',
                score=1.0
            )
            
            # Create custom recognizers
            ssn_recognizer = PatternRecognizer(
                supported_entity="SSN",
                patterns=[ssn_pattern],
                context=["SSN", "Social Security", "ID"]
            )
            phone_recognizer = PatternRecognizer(
                supported_entity="PHONE_NUMBER",
                patterns=[phone_pattern],
                context=["Phone", "Contact", "Emergency", "Telephone"]
            )
            email_recognizer = PatternRecognizer(
                supported_entity="EMAIL_ADDRESS",
                patterns=[email_pattern, email_structured_pattern],
                context=["email", "e-mail", "mailto"]
            )
            name_recognizer = PatternRecognizer(
                supported_entity="PERSON",
                patterns=[name_pattern],
                context=["Name", "Patient"]
            )
            policy_recognizer = PatternRecognizer(
                supported_entity="POLICY_NUMBER",
                patterns=[policy_pattern],
                context=["Insurance", "Policy"]
            )
            
            # Initialize analyzer and add custom recognizers
            analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
            analyzer.registry.add_recognizer(ssn_recognizer)
            analyzer.registry.add_recognizer(phone_recognizer)
            analyzer.registry.add_recognizer(email_recognizer)
            analyzer.registry.add_recognizer(name_recognizer)
            analyzer.registry.add_recognizer(policy_recognizer)
            
            anonymizer = AnonymizerEngine()
            logger.info("Presidio initialized with en_core_web_lg and custom patterns")
            return analyzer, anonymizer
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            raise
    
    def mask_pii(self, text: str) -> str:
        """Mask PII in text using Presidio with custom recognizers."""
        try:
            results = self.analyzer.analyze(
                text=text,
                language="en",
                entities=[
                    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "SSN",
                    "CREDIT_CARD", "LOCATION", "ORGANIZATION", "POLICY_NUMBER"
                ],
                score_threshold=0.6
            )
            ops = {
                r.entity_type: OperatorConfig("replace", {"new_value": f"<{r.entity_type}>"})
                for r in results
            }
            masked_text = self.anonymizer.anonymize(
                text=text, analyzer_results=results, operators=ops
            ).text
            logger.info(f"Masked {len(results)} PII entities")
            return masked_text
        except Exception as e:
            logger.error(f"Error masking PII: {e}")
            return text
    
    def parse_image(self, image_path: Path) -> str:
        """Parse text from an image using Tesseract OCR."""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='eng')
            logger.info(f"Parsed {image_path.name}: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Failed to parse {image_path}: {e}")
            return ""
    
    def compare_texts(self, text1: str, text2: str, name1: str, name2: str) -> list[str]:
        """Compare two texts line by line and return differences."""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=name1, tofile=name2,
            lineterm=''
        )
        return list(diff)
    
    def process_directory(self):
        """Process images, compare content, mask PII, and save unmasked/masked results."""
        if not self.input_path.is_dir():
            logger.error(f"Invalid directory: {self.input_path}")
            sys.exit(1)
        
        # Find JPG and PNG images
        images = [
            f for f in self.input_path.glob("*")
            if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
        images.sort()
        logger.info(f"Found {len(images)} images")
        
        if len(images) < 2:
            logger.warning("Need at least 2 images to compare")
            return
        
        # Parse all images
        documents = {}
        for img in images:
            text = self.parse_image(img)
            if text:
                documents[img.name] = text
        
        # Compare documents pairwise and prepare report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unmasked_report = [f"Document Comparison Report\nGenerated: {datetime.now()}\n\n"]
        masked_report = unmasked_report.copy()
        
        for i, name1 in enumerate(documents):
            for name2 in list(documents.keys())[i + 1:]:
                logger.info(f"Comparing {name1} with {name2}")
                diff = self.compare_texts(
                    documents[name1], documents[name2], name1, name2
                )
                comparison_header = f"Comparison: {name1} vs {name2}\n{'=' * 80}\n"
                if diff:
                    diff_text = "Differences Found:\n" + "\n".join(diff) + "\n"
                else:
                    diff_text = "No Differences Found\n"
                
                unmasked_report.append(comparison_header + diff_text + f"\n{'=' * 80}\n\n")
                
                masked_diff = self.mask_pii(diff_text)
                masked_report.append(comparison_header + masked_diff + f"\n{'=' * 80}\n\n")
        
        # Save unmasked report
        unmasked_file = self.output_path / f"diff_report_{timestamp}.txt"
        with open(unmasked_file, 'w', encoding='utf-8') as f:
            f.write("".join(unmasked_report))
        logger.info(f"Unmasked report saved to {unmasked_file}")
        
        # Save masked report
        masked_file = self.output_path / f"diff_report_masked_{timestamp}.txt"
        with open(masked_file, 'w', encoding='utf-8') as f:
            f.write("".join(masked_report))
        logger.info(f"Masked report saved to {masked_file}")
        
        # Save individual masked documents
        for name, text in documents.items():
            masked_text = self.mask_pii(text)
            doc_file = self.output_path / f"masked_{name}_{timestamp}.txt"
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(masked_text)
            logger.info(f"Masked document saved to {doc_file}")

def main():
    """Main function to run the app."""
    import argparse
    parser = argparse.ArgumentParser(description="Compare document images and mask PII")
    parser.add_argument("input_dir", help="Directory with JPG/PNG document images")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    args = parser.parse_args()
    
    processor = DocumentProcessor(args.input_dir, args.output)
    processor.process_directory()
    print(f"✅ Processing complete! Check {args.output}")

if __name__ == "__main__":
    main()