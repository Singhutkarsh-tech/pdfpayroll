from typing import Dict, Any, Optional
import json
from datetime import datetime
import os
from pathlib import Path


class ReportGenerator:
    """
    Generates payroll reports in various formats.
    
    Creates detailed payroll reports for employees including
    all salary components, deductions, and compliance details.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize report generator with output directory.
        
        Args:
            output_dir: Directory for report output (defaults to reports directory)
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent / "reports"
        else:
            self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_json_report(self, employee_id: str, salary_details: Dict[str, Any]) -> str:
        """
        Generate JSON report for employee salary details.
        
        Args:
            employee_id: Unique identifier for employee
            salary_details: Complete salary breakdown
            
        Returns:
            Path to the generated JSON report
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{employee_id}_{timestamp}_payroll.json"
        file_path = self.output_dir / filename
        
        # Add report metadata
        report_data = {
            "report_id": f"PR_{employee_id}_{timestamp}",
            "generated_at": datetime.now().isoformat(),
            "employee_id": employee_id,
            "salary_details": salary_details
        }
        
        # Write report to file
        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        return str(file_path)
    
    def generate_summary_report(self, employee_id: str, salary_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a simplified summary report for quick reference.
        
        Args:
            employee_id: Unique identifier for employee
            salary_details: Complete salary breakdown
            
        Returns:
            Dictionary with summarized payroll information
        """
        monthly = salary_details["employee_details"]["monthly"]
        annual = salary_details["employee_details"]["annual"]
        employer = salary_details["employer_contributions"]["monthly"]
        
        return {
            "employee_id": employee_id,
            "state": salary_details["compliance"]["state"],
            "monthly_summary": {
                "gross_salary": monthly["gross_salary"],
                "total_deductions": monthly["deductions"]["total_deductions"],
                "net_salary": monthly["net_salary"]
            },
            "annual_summary": {
                "ctc": salary_details["ctc"]["provided"],
                "gross_salary": annual["gross_salary"],
                "total_deductions": annual["deductions"]["total_deductions"],
                "net_salary": annual["net_salary"]
            },
            "key_deductions": {
                "pf": monthly["deductions"]["pf_contribution"],
                "professional_tax": monthly["deductions"]["professional_tax"],
                "esi": monthly["deductions"]["esi_contribution"]
            },
            "employer_contributions": employer["total_contributions"],
            "generated_at": datetime.now().isoformat()
        }