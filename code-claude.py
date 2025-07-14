import os
import base64
import mimetypes
import json
from typing import Any, List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import logging

# LangChain message formats for multimodal input
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import your actual LLM (adjust the import if needed)
from pyeqas.langx.llm import VegasChatLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LineEligibility:
    """Data class to store eligibility information for a single line"""
    line_number: str
    phone_number: Optional[str]
    device_name: Optional[str]
    loan_payoff_amount: Optional[float]
    installment_info: Optional[str]
    installment_number: Optional[int]
    total_installments: Optional[int]
    bill_date: Optional[str]
    is_recent_bill: bool
    is_mature_loan: bool
    is_within_cap: bool
    eligible_credit: float
    qualification_status: str
    details: Dict[str, Any]

@dataclass
class BillAnalysisResult:
    """Consolidated result for entire bill analysis"""
    total_qualified_credit: float
    total_lines_analyzed: int
    qualified_lines: int
    bill_date: Optional[str]
    is_bill_recent: bool
    line_eligibilities: List[LineEligibility]
    overall_status: str
    analysis_summary: str

class MultiPageBillAnalyzer:
    """
    Advanced multi-page bill analyzer that can handle complete bills
    across multiple pages/images for Verizon's Switch and Save promotion.
    """
    
    def __init__(self, llm: Any, max_credit_per_line: float = 800.0, bill_recency_days: int = 30):
        self.llm = llm
        self.max_credit_per_line = max_credit_per_line
        self.bill_recency_days = bill_recency_days
        self.current_date = datetime.now()
        
    def encode_image_to_base64(self, file_path: str) -> Tuple[str, str]:
        """Encode image file to base64 and determine MIME type"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
            
        with open(file_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
            
        return image_base64, mime_type
    
    def analyze_single_page(self, file_path: str, page_number: int, total_pages: int) -> Dict[str, Any]:
        """
        Analyze a single page of the bill to extract line-specific information
        """
        image_base64, mime_type = self.encode_image_to_base64(file_path)
        current_date_str = self.current_date.strftime("%B %d, %Y")
        
        # Enhanced system prompt for multi-line analysis
        system_prompt = SystemMessage(
            content=(
                "You are an expert analyst for Verizon's Switch and Save promotion program.\n"
                f"The current date is {current_date_str}.\n"
                f"You are analyzing page {page_number} of {total_pages} from a competitor's bill.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. Find ALL unique phone lines with device loans on this page.\n"
                "2. For each line, extract:\n"
                "   - Line identifier (phone number or line name)\n"
                "   - Device name/model\n"
                "   - Device loan payoff amount (remaining balance)\n"
                "   - Installment information (e.g., '14 of 36')\n"
                "   - Any device payment history\n"
                "3. Also find the bill issue date if present on this page.\n"
                "4. Look for section headers like 'Device Payments', 'Equipment Installments', 'Phone Plans', etc.\n"
                "5. Pay attention to different line numbers, phone numbers, or account sections.\n\n"
                "RESPONSE FORMAT:\n"
                "Respond with a JSON object containing:\n"
                "{\n"
                "  'page_number': int,\n"
                "  'bill_date': 'YYYY-MM-DD or null',\n"
                "  'lines_found': [\n"
                "    {\n"
                "      'line_identifier': 'phone number or line name',\n"
                "      'device_name': 'device model',\n"
                "      'loan_payoff_amount': float or null,\n"
                "      'installment_info': 'X of Y format',\n"
                "      'installment_current': int or null,\n"
                "      'installment_total': int or null,\n"
                "      'additional_details': 'any other relevant info'\n"
                "    }\n"
                "  ],\n"
                "  'page_summary': 'brief summary of what was found on this page'\n"
                "}\n\n"
                "If no device loans are found, return an empty 'lines_found' array.\n"
                "Be thorough and don't miss any lines that might have device payments."
            )
        )
        
        user_message = HumanMessage(
            content=[
                {"type": "text", "text": f"Analyze this bill page {page_number} and extract all device loan information for each line. Return the response as JSON."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    },
                },
            ]
        )
        
        logger.info(f"Analyzing page {page_number}...")
        response = self.llm.invoke([system_prompt, user_message])
        
        try:
            # Parse the JSON response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
                
            # Clean up the response to extract JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            page_data = json.loads(content)
            logger.info(f"Successfully parsed page {page_number}: {len(page_data.get('lines_found', []))} lines found")
            return page_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from page {page_number}: {e}")
            logger.error(f"Raw content: {content}")
            return {
                'page_number': page_number,
                'bill_date': None,
                'lines_found': [],
                'page_summary': f'Error parsing page {page_number}',
                'error': str(e)
            }
    
    def consolidate_line_data(self, all_page_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Consolidate line information from all pages, removing duplicates and merging data
        """
        consolidated_lines = {}
        bill_date = None
        
        # Find bill date from any page
        for page_data in all_page_data:
            if page_data.get('bill_date'):
                bill_date = page_data['bill_date']
                break
        
        # Consolidate lines
        for page_data in all_page_data:
            for line in page_data.get('lines_found', []):
                line_id = line.get('line_identifier', '')
                
                if line_id in consolidated_lines:
                    # Merge data for existing line
                    existing = consolidated_lines[line_id]
                    for key, value in line.items():
                        if value and not existing.get(key):
                            existing[key] = value
                else:
                    # Add new line
                    consolidated_lines[line_id] = line.copy()
        
        # Convert to list and add bill date to each line
        consolidated_list = []
        for line_id, line_data in consolidated_lines.items():
            line_data['bill_date'] = bill_date
            consolidated_list.append(line_data)
            
        return consolidated_list
    
    def assess_line_eligibility(self, line_data: Dict[str, Any]) -> LineEligibility:
        """
        Assess eligibility for a single line based on the consolidated data
        """
        # Extract basic info
        line_number = line_data.get('line_identifier', 'Unknown')
        phone_number = line_number if line_number.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit() else None
        device_name = line_data.get('device_name')
        loan_payoff_amount = line_data.get('loan_payoff_amount')
        installment_info = line_data.get('installment_info')
        installment_current = line_data.get('installment_current')
        installment_total = line_data.get('installment_total')
        bill_date_str = line_data.get('bill_date')
        
        # Parse installment info if needed
        if installment_info and not installment_current:
            try:
                parts = installment_info.split(' of ')
                if len(parts) == 2:
                    installment_current = int(parts[0])
                    installment_total = int(parts[1])
            except (ValueError, IndexError):
                pass
        
        # Check bill recency
        is_recent_bill = False
        if bill_date_str:
            try:
                bill_date = datetime.strptime(bill_date_str, '%Y-%m-%d')
                days_diff = (self.current_date - bill_date).days
                is_recent_bill = days_diff <= self.bill_recency_days
            except ValueError:
                pass
        
        # Check loan maturity (4+ installments)
        is_mature_loan = installment_current is not None and installment_current >= 4
        
        # Check credit cap
        is_within_cap = loan_payoff_amount is not None and loan_payoff_amount > 0
        
        # Calculate eligible credit
        eligible_credit = 0.0
        if loan_payoff_amount and loan_payoff_amount > 0:
            eligible_credit = min(loan_payoff_amount, self.max_credit_per_line)
        
        # Determine qualification status
        if is_recent_bill and is_mature_loan and is_within_cap:
            qualification_status = "QUALIFIED"
        else:
            qualification_status = "NOT QUALIFIED"
            eligible_credit = 0.0
        
        return LineEligibility(
            line_number=line_number,
            phone_number=phone_number,
            device_name=device_name,
            loan_payoff_amount=loan_payoff_amount,
            installment_info=installment_info,
            installment_number=installment_current,
            total_installments=installment_total,
            bill_date=bill_date_str,
            is_recent_bill=is_recent_bill,
            is_mature_loan=is_mature_loan,
            is_within_cap=is_within_cap,
            eligible_credit=eligible_credit,
            qualification_status=qualification_status,
            details=line_data
        )
    
    def analyze_multi_page_bill(self, file_paths: List[str]) -> BillAnalysisResult:
        """
        Main method to analyze a complete multi-page bill
        """
        logger.info(f"Starting analysis of {len(file_paths)} pages...")
        
        all_page_data = []
        
        # Analyze each page
        for i, file_path in enumerate(file_paths, 1):
            try:
                page_data = self.analyze_single_page(file_path, i, len(file_paths))
                all_page_data.append(page_data)
            except Exception as e:
                logger.error(f"Error analyzing page {i}: {e}")
                all_page_data.append({
                    'page_number': i,
                    'bill_date': None,
                    'lines_found': [],
                    'page_summary': f'Error analyzing page {i}',
                    'error': str(e)
                })
        
        # Consolidate line data
        consolidated_lines = self.consolidate_line_data(all_page_data)
        logger.info(f"Consolidated {len(consolidated_lines)} unique lines")
        
        # Assess eligibility for each line
        line_eligibilities = []
        for line_data in consolidated_lines:
            eligibility = self.assess_line_eligibility(line_data)
            line_eligibilities.append(eligibility)
        
        # Calculate totals
        total_qualified_credit = sum(line.eligible_credit for line in line_eligibilities)
        qualified_lines = sum(1 for line in line_eligibilities if line.qualification_status == "QUALIFIED")
        
        # Determine overall status
        overall_status = "QUALIFIED" if qualified_lines > 0 else "NOT QUALIFIED"
        
        # Get bill date
        bill_date = None
        is_bill_recent = False
        for line in line_eligibilities:
            if line.bill_date:
                bill_date = line.bill_date
                is_bill_recent = line.is_recent_bill
                break
        
        # Generate analysis summary
        analysis_summary = self.generate_analysis_summary(
            line_eligibilities, total_qualified_credit, qualified_lines, len(consolidated_lines)
        )
        
        return BillAnalysisResult(
            total_qualified_credit=total_qualified_credit,
            total_lines_analyzed=len(consolidated_lines),
            qualified_lines=qualified_lines,
            bill_date=bill_date,
            is_bill_recent=is_bill_recent,
            line_eligibilities=line_eligibilities,
            overall_status=overall_status,
            analysis_summary=analysis_summary
        )
    
    def generate_analysis_summary(self, line_eligibilities: List[LineEligibility], 
                                total_credit: float, qualified_lines: int, total_lines: int) -> str:
        """
        Generate a comprehensive analysis summary
        """
        summary = []
        summary.append("=" * 60)
        summary.append("VERIZON SWITCH & SAVE PROMOTION - ELIGIBILITY ANALYSIS")
        summary.append("=" * 60)
        summary.append(f"Analysis Date: {self.current_date.strftime('%B %d, %Y')}")
        summary.append(f"Total Lines Analyzed: {total_lines}")
        summary.append(f"Qualified Lines: {qualified_lines}")
        summary.append(f"Total Qualified Credit: ${total_credit:.2f}")
        summary.append("")
        
        if qualified_lines > 0:
            summary.append("✅ CUSTOMER QUALIFIES FOR PROMOTION")
        else:
            summary.append("❌ CUSTOMER DOES NOT QUALIFY FOR PROMOTION")
        
        summary.append("")
        summary.append("LINE-BY-LINE BREAKDOWN:")
        summary.append("-" * 40)
        
        for i, line in enumerate(line_eligibilities, 1):
            summary.append(f"\nLine {i}: {line.line_number}")
            summary.append(f"  Device: {line.device_name or 'Unknown'}")
            summary.append(f"  Loan Payoff: ${line.loan_payoff_amount:.2f}" if line.loan_payoff_amount else "  Loan Payoff: Not found")
            summary.append(f"  Installment: {line.installment_info or 'Not found'}")
            summary.append(f"  Status: {line.qualification_status}")
            summary.append(f"  Eligible Credit: ${line.eligible_credit:.2f}")
            
            # Show failure reasons
            if line.qualification_status == "NOT QUALIFIED":
                reasons = []
                if not line.is_recent_bill:
                    reasons.append("Bill not recent (>30 days)")
                if not line.is_mature_loan:
                    reasons.append("Loan not mature (<4 installments)")
                if not line.is_within_cap:
                    reasons.append("No valid loan amount found")
                if reasons:
                    summary.append(f"  Failure Reasons: {', '.join(reasons)}")
        
        return "\n".join(summary)
    
    def print_detailed_report(self, result: BillAnalysisResult):
        """
        Print a detailed eligibility report
        """
        print(result.analysis_summary)
        
        # Additional technical details
        print("\n" + "=" * 60)
        print("TECHNICAL DETAILS")
        print("=" * 60)
        print(f"Bill Date: {result.bill_date or 'Not found'}")
        print(f"Bill Recency: {'✅ Recent' if result.is_bill_recent else '❌ Not recent'}")
        print(f"Max Credit per Line: ${self.max_credit_per_line:.2f}")
        print(f"Bill Recency Requirement: {self.bill_recency_days} days")

def main():
    """
    Main function to demonstrate the multi-page bill analyzer
    """
    # Initialize the analyzer
    llm = VegasChatLLM()
    analyzer = MultiPageBillAnalyzer(llm)
    
    # Example: Multiple pages of a bill
    bill_pages = [
        r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page1.png",
        r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page2.png",
        r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\page3.png",
        # Add more pages as needed
    ]
    
    # For single page testing, use:
    # bill_pages = [r"C:\Users\goginra\Desktop\Rajesh\Projects\ACSS\Bill Insights\7.png"]
    
    # Filter out non-existent files
    existing_pages = [page for page in bill_pages if os.path.exists(page)]
    
    if not existing_pages:
        print("Error: No valid bill pages found. Please update the file paths.")
        return
    
    print(f"Analyzing {len(existing_pages)} bill pages...")
    
    try:
        # Run the analysis
        result = analyzer.analyze_multi_page_bill(existing_pages)
        
        # Print the detailed report
        analyzer.print_detailed_report(result)
        
        # Optional: Save results to JSON
        import json
        result_dict = {
            'total_qualified_credit': result.total_qualified_credit,
            'total_lines_analyzed': result.total_lines_analyzed,
            'qualified_lines': result.qualified_lines,
            'overall_status': result.overall_status,
            'bill_date': result.bill_date,
            'is_bill_recent': result.is_bill_recent,
            'lines': [
                {
                    'line_number': line.line_number,
                    'device_name': line.device_name,
                    'loan_payoff_amount': line.loan_payoff_amount,
                    'installment_info': line.installment_info,
                    'qualification_status': line.qualification_status,
                    'eligible_credit': line.eligible_credit
                }
                for line in result.line_eligibilities
            ]
        }
        
        # Save to file
        with open('bill_analysis_result.json', 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        print(f"\nResults saved to 'bill_analysis_result.json'")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()