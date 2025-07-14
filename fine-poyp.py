import os
import base64
import mimetypes
from typing import Any, List, Union
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from pyeqas.langx.llm import VegasChatLLM


def convert_pdf_to_images(pdf_path: str) -> List[bytes]:
    """
    Converts PDF pages to high-resolution PNG bytes.
    Ensures each page is captured at 300dpi for OCR-friendly quality.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        matrix = fitz.Matrix(3, 3)  # 3x zoom for better quality
        pix = page.get_pixmap(matrix=matrix)
        img_data = pix.tobytes("png")
        images.append(img_data)
    doc.close()
    return images


def prepare_file_content(file_path: str) -> List[tuple]:
    """
    Returns list of (image_data, mime_type) tuples.
    Handles PDFs & image files with robust validation.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = Path(file_path).suffix.lower()

    if file_extension == ".pdf":
        # Handle PDF
        image_bytes_list = convert_pdf_to_images(file_path)
        if not image_bytes_list:
            raise ValueError("PDF contains no pages.")
        return [(img_bytes, "image/png") for img_bytes in image_bytes_list]
    elif file_extension in {".jpg", ".jpeg", ".png"}:
        # Single image
        with open(file_path, "rb") as f:
            image_data = f.read()
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "image/png"
        return [(image_data, mime_type)]
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


def analyze_bill_with_llm(file_paths: Union[str, List[str]], user_query: str, llm: Any) -> Any:
    """
    Agent that handles single/multiple images, PDFs, or mixed.
    Calls LLM with clear business rules & refined prompt.
    """

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    all_content = []
    total_pages = 0

    for file_path in file_paths:
        content_list = prepare_file_content(file_path)
        all_content.extend(content_list)
        total_pages += len(content_list)

    if not all_content:
        return "Error: No valid content found."

    current_date_str = datetime.now().strftime("%B %d, %Y")

    # 🔷 Refined System Prompt
    system_prompt = SystemMessage(
        content=(
            f"You are an expert analyst tasked with determining eligibility for Verizon’s 'Switch & Save' promotion.\n"
            f"Current date: {current_date_str}.\n"
            f"You will analyze {total_pages} page(s) of competitor bills, ensuring **nothing is missed** and each line is attributed correctly.\n\n"

            "📋 **Business Rules:**\n"
            "1️⃣ Loan Installment: Customer must have made at least 3 payments and be on or beyond the 4th installment with their current carrier.\n"
            "2️⃣ Promo Cap: If the customer owes more than $800, Verizon will cover only $800; otherwise, the owed amount.\n"
            "3️⃣ Bill Recency: Ideally, the bill date should be within 30 days, but **if rules (1) & (2) are met, and bill is older, still qualify — explicitly call this out.**\n\n"

            "💼 **Your Output:**\n"
            "➜ A detailed markdown table listing each phone line across all pages with columns:\n"
            "`Phone Number | Loan Payoff | Installment History | Bill Date | Eligible Credit | Status`\n"
            "- Loan Payoff: Actual amount found.\n"
            "- Installment: e.g., '4 of 36', status ☑ if >=4.\n"
            "- Bill Date: Actual date & status ☑ if within 30 days.\n"
            "- Eligible Credit: min(Loan Payoff, $800).\n"
            "- Status: ☑ if meets rules.\n\n"

            "➜ A short, human-readable summary explaining the findings line-by-line in simple sentences. For example:\n"
            "- Line xxx-xxx-1234: Qualifies despite older bill because loan & installment met.\n"
            "- Line xxx-xxx-5678: Does not qualify due to insufficient installment history.\n\n"

            "➜ At the end:\n"
            "**Total Qualified Credit: $X**\n"
            "**Final Recommendation: QUALIFIED / NOT QUALIFIED**\n\n"

            "⚠️ If no lines found, state explicitly: 'No eligible lines detected.'"
        )
    )

    message_content = [{"type": "text", "text": user_query}]

    for i, (image_data, mime_type) in enumerate(all_content):
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{image_base64}"
            },
        })

    user_message = HumanMessage(content=message_content)

    print(f"📄 Processing {total_pages} page(s) with refined AI Agent…")
    response = llm.invoke([system_prompt, user_message])
    return response


def main():
    """
    Entry point for the agent.
    Supports:
    - Single image
    - Multiple images
    - PDF
    - Mixed list
    """

    llm = VegasChatLLM()

    # 🔷 Example input (update here ↓↓↓)

    # Single image
    # bill_to_analyze = r"C:\path\to\bill_image.jpg"

    # Multiple images
    # bill_to_analyze = [
    #     r"C:\path\to\page1.png",
    #     r"C:\path\to\page2.png"
    # ]

    # PDF
    bill_to_analyze = r"C:\path\to\bill.pdf"

    # Mixed
    # bill_to_analyze = [
    #     r"C:\path\to\bill.pdf",
    #     r"C:\path\to\extra_page.png"
    # ]

    query = (
        "Please analyze all pages of this bill and provide a comprehensive eligibility report "
        "for all phone lines with device loans, following the business rules."
    )

    print(f"🔷 Analyzing: {bill_to_analyze}")

    try:
        final_summary_object = analyze_bill_with_llm(
            file_paths=bill_to_analyze,
            user_query=query,
            llm=llm
        )

        print("\n✅ --- Final Eligibility Report ---\n")

        if hasattr(final_summary_object, "content"):
            print(final_summary_object.content)
        else:
            print(final_summary_object)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your file paths & ensure they exist and are valid.")


if __name__ == "__main__":
    main()
