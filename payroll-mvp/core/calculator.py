from typing import Dict, Any, Optional, Union, List
from decimal import Decimal
import json
import os
from pathlib import Path


class PayrollCalculator:
    """
    Core calculator class for payroll processing.
    
    Handles various payroll calculations including professional tax,
    provident fund, ESI, and net salary calculations based on state-specific rules.
    """
    
    def __init__(self, state_data: Dict[str, Any]):
        """
        Initialize calculator with state-specific data.
        
        Args:
            state_data: Dictionary containing state-specific payroll rules
        """
        self.state_data = state_data
        self.state_name = state_data["state_name"]
    
    @staticmethod
    def load_state_data(state: str) -> Dict[str, Any]:
        """
        Load state data from JSON file.
        
        Args:
            state: State name (case-insensitive)
            
        Returns:
            Dictionary with state-specific payroll data
            
        Raises:
            FileNotFoundError: If state data file doesn't exist
        """
        state = state.lower()
        data_dir = Path(__file__).parent.parent / "data"
        state_file = data_dir / f"{state}.json"
        
        if not state_file.exists():
            raise FileNotFoundError(f"State data for {state} not found")
        
        with open(state_file, "r") as f:
            return json.load(f)
    
    def calculate_professional_tax(self, monthly_salary: Union[float, Decimal]) -> float:
        """
        Calculate professional tax based on monthly salary and state rules.
        
        Args:
            monthly_salary: Employee's monthly salary
            
        Returns:
            Professional tax amount for the month
            
        Examples:
            >>> calculator = PayrollCalculator(load_state_data("maharashtra"))
            >>> calculator.calculate_professional_tax(12000)
            175.0
        """
        # Convert to float for consistent comparison
        monthly_salary = float(monthly_salary)
        
        slabs = self.state_data["professional_tax"]["monthly_slabs"]
        annual_ceiling = self.state_data["professional_tax"]["annual_ceiling"]
        
        # Find the appropriate slab
        tax_amount = 0
        for slab in slabs:
            min_val = slab["min"]
            max_val = slab["max"]
            
            # Handle open-ended slab (null max value)
            if max_val is None and monthly_salary >= min_val:
                tax_amount = slab["tax"]
                break
            elif min_val <= monthly_salary <= max_val:
                tax_amount = slab["tax"]
                break
        
        return tax_amount
    
    def calculate_provident_fund(self, base_salary: Union[float, Decimal]) -> Dict[str, float]:
        """
        Calculate PF contributions based on base salary and state rules.
        
        Args:
            base_salary: Employee's monthly base salary
            
        Returns:
            Dictionary with employee and employer PF contribution details
        """
        base_salary = float(base_salary)
        pf_data = self.state_data["provident_fund"]
        
        # Calculate PF on the capped amount
        pf_applicable_salary = min(base_salary, pf_data["salary_ceiling"])
        
        employee_contribution = pf_applicable_salary * (pf_data["employee_contribution_rate"] / 100)
        
        # Employer contribution is split between EPF and Pension Fund
        employer_epf = pf_applicable_salary * (pf_data["employer_epf_rate"] / 100)
        employer_pension = pf_applicable_salary * (pf_data["employer_pension_rate"] / 100)
        
        # Admin charges
        admin_charges = pf_applicable_salary * (pf_data["admin_charges_rate"] / 100)
        edli_charges = pf_applicable_salary * (pf_data["edli_rate"] / 100)
        
        return {
            "employee_contribution": round(employee_contribution, 2),
            "employer_epf_contribution": round(employer_epf, 2),
            "employer_pension_contribution": round(employer_pension, 2),
            "admin_charges": round(admin_charges, 2),
            "edli_charges": round(edli_charges, 2),
            "total_employer_contribution": round(employer_epf + employer_pension + admin_charges + edli_charges, 2),
            "total_pf_contribution": round(employee_contribution + employer_epf + employer_pension + admin_charges + edli_charges, 2)
        }
    
    def calculate_esi(self, gross_salary: Union[float, Decimal]) -> Dict[str, float]:
        """
        Calculate ESI contributions based on gross salary and state rules.
        
        Args:
            gross_salary: Employee's monthly gross salary
            
        Returns:
            Dictionary with employee and employer ESI contribution details,
            or empty values if ESI is not applicable
        """
        gross_salary = float(gross_salary)
        esi_data = self.state_data["esi"]
        
        # ESI is applicable only if salary is below threshold
        if gross_salary <= esi_data["income_threshold"]:
            employee_contribution = gross_salary * (esi_data["employee_contribution_rate"] / 100)
            employer_contribution = gross_salary * (esi_data["employer_contribution_rate"] / 100)
            
            return {
                "applicable": True,
                "employee_contribution": round(employee_contribution, 2),
                "employer_contribution": round(employer_contribution, 2),
                "total_contribution": round(employee_contribution + employer_contribution, 2)
            }
        else:
            return {
                "applicable": False,
                "employee_contribution": 0,
                "employer_contribution": 0,
                "total_contribution": 0
            }
    
    def calculate_labour_welfare_fund(self) -> Dict[str, float]:
        """
        Calculate Labour Welfare Fund contributions based on state rules.
        
        Returns:
            Dictionary with employee and employer LWF contribution details
        """
        lwf_data = self.state_data["labour_welfare_fund"]
        
        # LWF is typically a fixed amount
        employee_contribution = lwf_data["employee_contribution"]
        employer_contribution = lwf_data["employer_contribution"]
        
        if lwf_data["payment_frequency"] == "semi-annual":
            # Convert to monthly equivalent
            employee_contribution /= 6
            employer_contribution /= 6
        elif lwf_data["payment_frequency"] == "annual":
            # Convert to monthly equivalent
            employee_contribution /= 12
            employer_contribution /= 12
        
        return {
            "employee_contribution": round(employee_contribution, 2),
            "employer_contribution": round(employer_contribution, 2),
            "total_contribution": round(employee_contribution + employer_contribution, 2),
            "payment_frequency": lwf_data["payment_frequency"]
        }
    
    def calculate_net_salary(self, ctc: float, base_salary: float, 
                          benefits: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate complete salary breakdown including all deductions.
        
        Args:
            ctc: Cost to Company (annual)
            base_salary: Monthly base salary
            benefits: Dictionary of additional benefits
            
        Returns:
            Complete salary breakdown with all components
        """
        # Calculate monthly CTC
        monthly_ctc = ctc / 12
        
        # Calculate gross salary (base + benefits)
        total_benefits = sum(benefits.values())
        gross_salary = base_salary + total_benefits
        
        # Calculate various deductions
        professional_tax = self.calculate_professional_tax(gross_salary)
        pf_details = self.calculate_provident_fund(base_salary)
        esi_details = self.calculate_esi(gross_salary)
        lwf_details = self.calculate_labour_welfare_fund()
        
        # Total employee deductions
        total_deductions = (
            professional_tax + 
            pf_details["employee_contribution"] + 
            esi_details["employee_contribution"] + 
            lwf_details["employee_contribution"]
        )
        
        # Calculate net salary
        net_salary = gross_salary - total_deductions
        
        # Calculate employer contributions
        employer_contributions = (
            pf_details["total_employer_contribution"] +
            esi_details["employer_contribution"] +
            lwf_details["employer_contribution"]
        )
        
        # Verify CTC calculation
        calculated_ctc = (gross_salary + employer_contributions) * 12
        ctc_difference = abs(calculated_ctc - ctc)
        
        return {
            "employee_details": {
                "monthly": {
                    "base_salary": base_salary,
                    "benefits": benefits,
                    "gross_salary": gross_salary,
                    "deductions": {
                        "professional_tax": professional_tax,
                        "pf_contribution": pf_details["employee_contribution"],
                        "esi_contribution": esi_details["employee_contribution"],
                        "labour_welfare_fund": lwf_details["employee_contribution"],
                        "total_deductions": total_deductions
                    },
                    "net_salary": net_salary
                },
                "annual": {
                    "base_salary": base_salary * 12,
                    "benefits": {k: v * 12 for k, v in benefits.items()},
                    "gross_salary": gross_salary * 12,
                    "deductions": {
                        "professional_tax": min(professional_tax * 12, self.state_data["professional_tax"]["annual_ceiling"]),
                        "pf_contribution": pf_details["employee_contribution"] * 12,
                        "esi_contribution": esi_details["employee_contribution"] * 12,
                        "labour_welfare_fund": lwf_details["employee_contribution"] * 12,
                        "total_deductions": (
                            min(professional_tax * 12, self.state_data["professional_tax"]["annual_ceiling"]) +
                            pf_details["employee_contribution"] * 12 +
                            esi_details["employee_contribution"] * 12 +
                            lwf_details["employee_contribution"] * 12
                        )
                    },
                    "net_salary": (
                        gross_salary * 12 - 
                        min(professional_tax * 12, self.state_data["professional_tax"]["annual_ceiling"]) -
                        pf_details["employee_contribution"] * 12 -
                        esi_details["employee_contribution"] * 12 -
                        lwf_details["employee_contribution"] * 12
                    )
                }
            },
            "employer_contributions": {
                "monthly": {
                    "pf_details": {
                        "epf_contribution": pf_details["employer_epf_contribution"],
                        "pension_contribution": pf_details["employer_pension_contribution"],
                        "admin_charges": pf_details["admin_charges"],
                        "edli_charges": pf_details["edli_charges"]
                    },
                    "esi_contribution": esi_details["employer_contribution"],
                    "labour_welfare_fund": lwf_details["employer_contribution"],
                    "total_contributions": employer_contributions
                },
                "annual": {
                    "pf_details": {
                        "epf_contribution": pf_details["employer_epf_contribution"] * 12,
                        "pension_contribution": pf_details["employer_pension_contribution"] * 12,
                        "admin_charges": pf_details["admin_charges"] * 12,
                        "edli_charges": pf_details["edli_charges"] * 12
                    },
                    "esi_contribution": esi_details["employer_contribution"] * 12,
                    "labour_welfare_fund": lwf_details["employer_contribution"] * 12,
                    "total_contributions": employer_contributions * 12
                }
            },
            "ctc": {
                "provided": ctc,
                "calculated": calculated_ctc,
                "difference": ctc_difference
            },
            "compliance": {
                "state": self.state_name,
                "esi_applicable": esi_details["applicable"],
                "professional_tax_applicable": professional_tax > 0
            }
        }