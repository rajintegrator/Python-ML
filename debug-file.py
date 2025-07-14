import os
import base64
import mimetypes
from typing import Any, List, Union
from datetime import datetime
import fitz  # PyMuPDF for PDF handling
from PIL import Image
import io

# LangChain message formats for multimodal input
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import your actual LLM (adjust the import if needed)
from pyeqas.langx.llm import VegasChatLLM


def convert_pdf_to_images(pdf_path: str) -> List[bytes]:
    """Convert PDF pages to image bytes"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        images.append(img_data)
    
    doc.close()
    return images


def prepare_file_content(file_path: str) -> List[tuple]:
    """
    Prepare file content for analysis. Returns list of (image_data, mime_type) tuples.
    Handles single images, multiple images, and PDFs.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        # Handle PDF
        image_bytes_list = convert_pdf_to_images(file_path)
        return [(img_bytes, "image/png") for img_bytes in image_bytes_list]
    else:
        # Handle image file
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "image/png"
        
        return [(image_data, mime_type)]


def analyze_bill_with_llm(file_paths: Union[str, List[str]], user_query: str, llm: Any) -> Any:
    """
    Enhanced analyzer that handles single image, multiple images, or PDF files.
    Returns the entire AIMessage object or an error string.
    """
    
    # Convert single file path to list for uniform processing
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    # Prepare all content
    all_content = []
    total_pages = 0
    
    for file_path in file_paths:
        try:
            content_list = prepare_file_content(file_path)
            all_content.extend(content_list)
            total_pages += len(content_list)
        except Exception as e:
            return f"Error processing {file_path}: {str(e)}"
    
    if not all_content:
        return "Error: No valid content found in provided files"
    
    # Get today's date
    current_date_str = datetime.now().strftime("%B %d, %Y")
    
    # Enhanced System Prompt for multi-page analysis
    system_prompt = SystemMessage(
        content=(
            "You are an expert analyst for Verizon's new customer promotion program.\n"
            f"The current date is {current_date_str}.\n\n"
            f"You will analyze {total_pages} page(s) of competitor bill(s) to find ALL phone lines with device loans.\n\n"
            "INSTRUCTIONS:\n"
            "1. Look across ALL pages to find every unique phone line with 'Device Loan Payoff', 'Installment History', and 'Bill Date'.\n"
            "2. For EACH qualifying line, create a separate row in your analysis table.\n"
            "3. Your final output MUST be a markdown table with columns: 'Line/Phone Number', 'Device', 'Loan Payoff Amount', 'Installment Status', 'Bill Date Status', 'Eligible Credit', 'Status'.\n"
            "4. For each line's 'Loan Payoff Amount': state the amount found. Eligible Credit = min(amount, $800). Status = ☑ if <= $800, ❌ if > $800.\n"
            "5. For 'Installment Status': state installment number (e.g., '14 of 36'). Status = ☑ if >= 4, ❌ if < 4.\n"
            "6. For 'Bill Date Status': state the 'Issue Date'. Status = ☑ if within 30 days, ❌ if not.\n"
            "7. Calculate total eligible credit by summing all qualifying lines.\n"
            "8. After the table, provide: **Total Qualified Credit: $X** and **Final Recommendation: QUALIFIED/NOT QUALIFIED**.\n"
            "9. A customer is QUALIFIED if they have at least one line that passes ALL checks.\n"
        )
    )
    
    # Create multimodal message with all images
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
    
    # Call the LLM
    print(f"---- Analyzing {total_pages} page(s) with AI Agent ----")
    response = llm.invoke([system_prompt, user_message])
    
    # Debug: Print response type and content
    print(f"Response type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    if hasattr(response, 'content'):
        print(f"Response content length: {len(response.content) if response.content else 0}")
        if response.content:
            print(f"First 200 chars: {response.content[:200]}")
    
    return response


def main():
    """
    Enhanced main function that can handle:
    - Single image: "bill.png"
    - Multiple images: ["page1.png", "page2.png", "page3.png"]
    - PDF file: "complete_bill.pdf"
    - Mixed: ["bill.pdf", "additional_page.png"]
    """
    
    # Initialize your LLM
    llm = VegasChatLLM()
    
    # ===== CONFIGURATION - UPDATE THESE PATHS =====
    
    # Option 1: Single image (your current working setup)
    bill_to_analyze = r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\7.png"
    
    # Option 2: Multiple images
    # bill_to_analyze = [
    #     r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page1.png",
    #     r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page2.png",
    #     r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page3.png"
    # ]
    
    # Option 3: PDF file
    # bill_to_analyze = r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\complete_bill.pdf"
    
    # Option 4: Mixed files
    # bill_to_analyze = [
    #     r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\bill.pdf",
    #     r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\extra_page.png"
    # ]
    
    # ===============================================
    
    query = "Please analyze all pages of this bill and provide a comprehensive eligibility report for ALL phone lines with device loans."
    
    print(f"--- Analyzing: {bill_to_analyze} ---")
    
    try:
        final_summary_object = analyze_bill_with_llm(
            file_paths=bill_to_analyze,
            user_query=query,
            llm=llm
        )
        
        print("\n--- Agent's Final Summary ---\n")
        
        # Enhanced output handling with debugging
        if hasattr(final_summary_object, "content"):
            content = final_summary_object.content
            print(f"Content type: {type(content)}")
            print(f"Content length: {len(content) if content else 0}")
            
            if content:
                print(content)
            else:
                print("Warning: Response content is empty!")
                print("Full response object:")
                print(final_summary_object)
        else:
            print(f"Response object type: {type(final_summary_object)}")
            print("Available attributes:", [attr for attr in dir(final_summary_object) if not attr.startswith('_')])
            print("Full response:")
            print(final_summary_object)
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Please check your file paths and ensure all files exist.")


if __name__ == "__main__":
    main()
