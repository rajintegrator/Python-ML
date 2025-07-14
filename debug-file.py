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
    
    # Test with a very simple prompt first
    system_prompt = SystemMessage(
        content="You are an AI assistant. Describe what you see in this image."
    )
    
    # Create the multimodal user message
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    user_message = HumanMessage(
        content=[
            {"type": "text", "text": "What do you see in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}"
                },
            },
        ]
    )
    
    # Call the LLM
    print(f"---- Testing AI Agent with simple prompt for page {page_num} ----")
    try:
        response = llm.invoke([system_prompt, user_message])
        
        # Comprehensive debugging
        print(f"Response object: {response}")
        print(f"Response type: {type(response)}")
        print(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        if hasattr(response, 'content'):
            print(f"Content: '{response.content}'")
            print(f"Content type: {type(response.content)}")
            print(f"Content length: {len(response.content) if response.content else 0}")
        
        # Try different possible attributes
        for attr in ['content', 'text', 'message', 'response', 'output']:
            if hasattr(response, attr):
                value = getattr(response, attr)
                print(f"Found {attr}: {value}")
        
        return response
    except Exception as e:
        print(f"Error analyzing page {page_num}: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Test LLM first
    print("=== Testing LLM Configuration ===")
    try:
        test_response = llm.invoke([SystemMessage(content="Hello"), HumanMessage(content="Say hello back")])
        print(f"LLM test response: {test_response}")
        print(f"LLM test response type: {type(test_response)}")
        if hasattr(test_response, 'content'):
            print(f"LLM test content: '{test_response.content}'")
    except Exception as e:
        print(f"LLM test failed: {e}")
        return
    
    # ===== CONFIGURATION - UPDATE THESE PATHS =====
    
    # Option 1: Single image (your current working setup)
    bill_to_analyze = r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\7.png"
    
    # Test file existence
    if isinstance(bill_to_analyze, str):
        if not os.path.exists(bill_to_analyze):
            print(f"Error: File not found: {bill_to_analyze}")
            return
    elif isinstance(bill_to_analyze, list):
        for file_path in bill_to_analyze:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}")
                return
    
    # ===============================================
    
    query = "Please analyze this bill."
    
    print(f"--- Analyzing: {bill_to_analyze} ---")
    
    try:
        final_summary_object = analyze_bill_with_llm(
            file_paths=bill_to_analyze,
            user_query=query,
            llm=llm
        )
        
        print("\n--- Agent's Final Summary ---\n")
        
        # Enhanced output handling with debugging
        if final_summary_object is None:
            print("ERROR: Got None response from analyze_bill_with_llm")
            return
        
        print(f"Final summary type: {type(final_summary_object)}")
        print(f"Final summary object: {final_summary_object}")
        
        if hasattr(final_summary_object, "content"):
            content = final_summary_object.content
            print(f"Content type: {type(content)}")
            print(f"Content length: {len(content) if content else 0}")
            
            if content:
                print("=== CONTENT ===")
                print(content)
                print("=== END CONTENT ===")
            else:
                print("WARNING: Response content is empty!")
                
                # Try to extract from other attributes
                for attr in dir(final_summary_object):
                    if not attr.startswith('_'):
                        value = getattr(final_summary_object, attr)
                        if isinstance(value, str) and value.strip():
                            print(f"Found text in {attr}: {value}")
        else:
            print("No 'content' attribute found")
            print(f"Available attributes: {[attr for attr in dir(final_summary_object) if not attr.startswith('_')]}")
            
            # Try to convert to string
            str_response = str(final_summary_object)
            if str_response and str_response != "None":
                print(f"String representation: {str_response}")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
