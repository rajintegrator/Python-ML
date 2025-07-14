import os
import base64
import mimetypes
from typing import Any, List, Dict
from datetime import datetime
from pathlib import Path
import tempfile
import json
import argparse
import shutil

from langchain_core.messages import HumanMessage, SystemMessage
from pyeqas.langx.llm import VegasChatLLM

from pdf2image import convert_from_path
from PIL import Image

from concurrent.futures import ThreadPoolExecutor, as_completed

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png"}
PDF_EXT = ".pdf"


def encode_image(file_path: str) -> (str, str):
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    return encoded, mime_type


def extract_pdf_pages(pdf_path: str) -> List[str]:
    pages = convert_from_path(pdf_path)
    tmp_dir = tempfile.mkdtemp()
    paths = []
    for idx, page in enumerate(pages):
        out = os.path.join(tmp_dir, f"page_{idx+1}.png")
        page.save(out, "PNG")
        paths.append(out)
    return paths


def build_system_prompt() -> SystemMessage:
    current_date = datetime.now().strftime("%B %d, %Y")
    return SystemMessage(
        content=(
            "You are an expert Verizon promotions analyst.\n"
            f"Today’s date: {current_date}.\n"
            "You will receive an image of a bill. Extract **all phone lines**, each with:\n"
            "• Phone Number\n• Loan Payoff\n• Installment (e.g., 5/36)\n• Bill Date\n"
            "Then apply rules:\n"
            "- Bill Date > 30 days → NOT ELIGIBLE\n"
            "- Installment < 4 → NOT ELIGIBLE\n"
            "- Loan Payoff > $800 → Eligible Credit = $800, else Eligible Credit = Loan Payoff\n"
            "Return TWO sections:\n"
            "1️⃣ Markdown table with: Phone Number | Loan Payoff | Installment | Bill Date | Eligible Credit\n"
            "2️⃣ JSON block listing all lines as list of dicts with above fields + ‘Status: Qualified/Not Qualified’\n"
            "If no lines found, clearly state that."
        )
    )


def analyze_page(page_path: str, llm: Any) -> Dict:
    encoded_img, mime_type = encode_image(page_path)
    user_message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyze this bill page for eligibility as per the rules."},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded_img}"}}
        ]
    )
    response = llm.invoke([build_system_prompt(), user_message])
    output = response.content if hasattr(response, "content") else str(response)
    # Extract JSON block from LLM output
    json_block = extract_json(output)
    return {"page": page_path, "markdown": output, "json": json_block}


def extract_json(text: str) -> List[Dict]:
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start:end])
            return data.get("lines", [])
        except Exception as e:
            print(f"Error parsing JSON from LLM: {e}")
    return []


def consolidate_lines(all_lines: List[List[Dict]]) -> (str, float, str):
    merged = {}
    total_credit = 0.0
    for lines in all_lines:
        for line in lines:
            phone = line.get("Phone Number", "Unknown")
            if phone in merged:
                continue  # already added
            credit = float(str(line.get("Eligible Credit", "0")).replace("$", ""))
            merged[phone] = line
            total_credit += credit

    qualified = any(l.get("Status") == "Qualified" for l in merged.values())
    final_status = "QUALIFIED" if qualified else "NOT QUALIFIED"

    summary = "\n\n--- Consolidated Summary ---\n"
    summary += f"Total Eligible Credit: ${total_credit}\n"
    summary += f"Final Recommendation: **{final_status}**\n"
    return summary, total_credit, final_status


def clean_temp_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


def process_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return

    suffix = Path(file_path).suffix.lower()
    llm = VegasChatLLM()

    if suffix == PDF_EXT:
        print("📄 Detected PDF → Extracting pages...")
        pages = extract_pdf_pages(file_path)
        tmp_dir = os.path.dirname(pages[0])
    elif suffix in ALLOWED_IMAGE_EXT:
        print("🖼️ Detected Image.")
        pages = [file_path]
        tmp_dir = None
    else:
        print("❌ Unsupported file type.")
        return

    results = []
    all_json_lines = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(analyze_page, p, llm): p for p in pages}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            all_json_lines.append(res["json"])

    final_report = ""
    for res in results:
        final_report += f"\n\n=== Page: {res['page']} ===\n\n"
        final_report += res["markdown"]

    summary, total_credit, final_status = consolidate_lines(all_json_lines)
    final_report += summary

    print("\n\n===== FINAL ELIGIBILITY REPORT =====\n")
    print(final_report)

    if tmp_dir:
        clean_temp_dir(tmp_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-page Eligibility Agent")
    parser.add_argument("file", help="Path to PDF or Image")
    args = parser.parse_args()

    process_file(args.file)
