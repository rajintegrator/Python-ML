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
    
    # If multiple pages, process them sequentially and combine results
    if total_pages > 1:
        print(f"Processing {total_pages} pages sequentially...")
        all_results = []
        
        for i, (image_data, mime_type) in enumerate(all_content):
            print(f"Processing page {i+1}/{total_pages}...")
            
            # Process each page individually
            page_result = analyze_single_page(image_data, mime_type, i+1, total_pages, llm)
            if page_result and hasattr(page_result, 'content') and page_result.content:
                all_results.append(page_result.content)
        
        # Combine results
        if all_results:
            combined_content = combine_page_results(all_results, current_date_str)
            # Create a mock response object
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            return MockResponse(combined_content)
        else:
            return "Error: No valid content extracted from any page"
    
    else:
        # Single page - use original logic
        image_data, mime_type = all_content[0]
        return analyze_single_page(image_data, mime_type, 1, 1, llm)


def analyze_single_page(image_data: bytes, mime_type: str, page_num: int, total_pages: int, llm: Any) -> Any:
    """Analyze a single page/image"""
    current_date_str = datetime.now().strftime("%B %d, %Y")
    
    # Use your original system prompt for single page
    system_prompt = SystemMessage(
        content=(
            "You are an expert analyst for Verizon's new customer promotion program.\n"
            f"The current date is {current_date_str}.\n\n"
            f"You are analyzing page {page_num} of {total_pages} from a competitor's bill.\n\n"
            "INSTRUCTIONS:\n"
            "1. Analyze the image to find the 'Device Loan Payoff', 'Installment History', and 'Bill Date'.\n"
            "2. Your final output MUST be a markdown table with three columns: 'Criteria Check', 'Details Found in Bill', and 'Status'.\n"
            "3. For the 'Loan Payoff Amount' row, state the found amount in the details column. In the 'Status' column, use ☑ if the amount is <= $800, otherwise ❌.\n"
            "4. For the 'Installment History', state the installment number (e.g., '14 of 36') in the details column. In the 'Status' column, use ☑ if the installment is 4 or greater, ❌ if not.\n"
            "5. For the 'Bill Date', state the 'Issue Date' in the details column. Use ☑ if within 30 days of today, ❌ if not.\n"
            "6. If any information cannot be found, note it in the 'Details' column and use ❌ in the 'Status' column.\n"
            "7. After the table, on a new line, you MUST provide a Final Recommendation: either **Final Recommendation: QUALIFIED** if all checks pass, or **Final Recommendation: NOT QUALIFIED** if any check fails.\n"
        )
    )
    
    # Create the multimodal user message
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    user_message = HumanMessage(
        content=[
            {"type": "text", "text": f"Please analyze this bill page {page_num} and provide a structured eligibility report."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}"
                },
            },
        ]
    )
    
    # Call the LLM
    print(f"---- Invoking AI Agent for page {page_num} ----")
    try:
        response = llm.invoke([system_prompt, user_message])
        
        # Debug info
        print(f"Page {page_num} response type: {type(response)}")
        if hasattr(response, 'content'):
            print(f"Page {page_num} content length: {len(response.content) if response.content else 0}")
        
        return response
    except Exception as e:
        print(f"Error analyzing page {page_num}: {e}")
        return None


def combine_page_results(page_results: List[str], current_date_str: str) -> str:
    """Combine results from multiple pages into a single report"""
    
    combined_report = []
    combined_report.append("# Multi-Page Bill Analysis Report")
    combined_report.append(f"Analysis Date: {current_date_str}")
    combined_report.append("")
    
    total_qualified_credit = 0
    overall_qualified = False
    
    for i, result in enumerate(page_results, 1):
        combined_report.append(f"## Page {i} Analysis")
        combined_report.append(result)
        combined_report.append("")
        
        # Simple parsing to extract qualification status
        if "QUALIFIED" in result and "NOT QUALIFIED" not in result:
            overall_qualified = True
        
        # Try to extract any dollar amounts (basic parsing)
        import re
        amounts = re.findall(r'\$(\d+(?:\.\d{2})?)', result)
        if amounts:
            try:
                # Take the first amount found as potential credit
                amount = float(amounts[0])
                if amount <= 800:
                    total_qualified_credit += amount
            except:
                pass
    
    # Add summary
    combined_report.append("## Overall Summary")
    combined_report.append(f"**Total Estimated Credit: ${total_qualified_credit:.2f}**")
    combined_report.append(f"**Final Recommendation: {'QUALIFIED' if overall_qualified else 'NOT QUALIFIED'}**")
    
    return "\n".join(combined_report)


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
