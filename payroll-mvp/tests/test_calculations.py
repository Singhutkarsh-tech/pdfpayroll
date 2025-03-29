import sys
import os
import json
import pytest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.calculator import PayrollCalculator


# Fixtures for test data
@pytest.fixture
def maharashtra_data():
    """Fixture for Maharashtra data."""
    data_file = Path(__file__).parent.parent / "data" / "maharashtra.json"
    
    # If data file doesn't exist, load default data
    if not data_file.exists():
        # Create minimal test data
        data = {
            "state_name": "Maharashtra",
            "professional_tax": {
                "monthly_slabs": [
                    {"min": 0, "max": 10000, "tax": 0},
                    {"min": 10001, "max": 15000, "tax": 175},
                    {"min": 15001, "max": 20000, "tax": 200},
                    {"min": 20001, "max": None, "tax": 300}
                ],
                "annual_ceiling": 2500
            },
            "provident_fund": {
                "employee_contribution_rate": 12.0,
                "employer_contribution_rate": 12.0,
                "employer_pension_rate": 8.33,
                "employer_epf_rate": 3.67,
                "salary_ceiling": 15000,
                "admin_charges_rate": 0.5,
                "edli_rate": 0.5
            },
            "esi": {
                "employee_contribution_rate": 0.75,
                "employer_contribution_rate": 3.25,
                "income_threshold": 21000,
                "minimum_wage_threshold": 137
            },
            "labour_welfare_fund": {
                "employee_contribution": 6,
                "employer_contribution": 12,
                "payment_frequency": "semi-annual"
            }
        }
        return data
    
    # Load data from file
    with open(data_file, "r") as f:
        return json.load(f)


@pytest.fixture
def calculator(maharashtra_data):
    """Fixture for PayrollCalculator instance."""
    return PayrollCalculator(maharashtra_data)


# Test professional tax calculation
class TestProfessionalTax:
    
    def test_zero_slab(self, calculator):
        """Test tax calculation for zero tax slab."""
        tax = calculator.calculate_professional_tax(9000)
        assert tax == 0, "Tax should be 0 for salary below 10000"
    
    def test_first_slab_boundary(self, calculator):
        """Test tax calculation at first slab boundary."""
        tax = calculator.calculate_professional_tax(10000)
        assert tax == 0, "Tax should be 0 for salary at 10000"
        
        tax = calculator.calculate_professional_tax(10001)
        assert tax == 175, "Tax should be 175 for salary at 10001"
    
    def test_second_slab_boundary(self, calculator):
        """Test tax calculation at second slab boundary."""
        tax = calculator.calculate_professional_tax(15000)
        assert tax == 175, "Tax should be 175 for salary at 15000"
        
        tax = calculator.calculate_professional_tax(15001)
        assert tax == 200, "Tax should be 200 for salary at 15001"
    
    def test_third_slab_boundary(self, calculator):
        """Test tax calculation at third slab boundary."""
        tax = calculator.calculate_professional_tax(20000)
        assert tax == 200, "Tax should be 200 for salary at 20000"
        
        tax = calculator.calculate_professional_tax(20001)
        assert tax == 300, "Tax should be 300 for salary at 20001"
    
    def test_open_ended_slab(self, calculator):
        """Test tax calculation for open-ended slab."""
        tax = calculator.calculate_professional_tax(50000)
        assert tax == 300, "Tax should be 300 for salary at 50000 (open-ended slab)"
    
    def test_annual_ceiling(self, calculator, maharashtra_data):
        """Test annual ceiling for professional tax."""
        monthly_tax = calculator.calculate_professional_tax(25000)
        annual_tax = monthly_tax * 12
        
        assert monthly_tax == 300, "Monthly tax should be 300 for salary at 25000"
        assert annual_tax > maharashtra_data["professional_tax"]["annual_ceiling"], "Annual tax exceeds ceiling"
        
        # In actual calculations, this would be capped at annual ceiling
        assert annual_tax == 3600, "Annual uncapped tax should be 3600"
        assert maharashtra_data["professional_tax"]["annual_ceiling"] == 2500, "Annual ceiling should be 2500"


# Test PF calculation
class TestProvidentFund:
    
    def test_pf_below_ceiling(self, calculator):
        """Test PF calculation below salary ceiling."""
        base_salary = 12000
        pf = calculator.calculate_provident_fund(base_salary)
        
        expected_employee_contribution = base_salary * 0.12
        
        assert pf["employee_contribution"] == expected_employee_contribution, \
            f"Employee PF contribution should be {expected_employee_contribution}"
    
    def test_pf_above_ceiling(self, calculator, maharashtra_data):
        """Test PF calculation above salary ceiling."""
        base_salary = 20000
        ceiling = maharashtra_data["provident_fund"]["salary_ceiling"]
        pf = calculator.calculate_provident_fund(base_salary)
        
        expected_employee_contribution = ceiling * 0.12
        
        assert pf["employee_contribution"] == expected_employee_contribution, \
            f"Employee PF contribution should be capped at {expected_employee_contribution}"
    
    def test_employer_contributions(self, calculator):
        """Test employer PF contribution breakdown."""
        base_salary = 12000
        pf = calculator.calculate_provident_fund(base_salary)
        
        expected_epf = base_salary * 0.0367
        expected_pension = base_salary * 0.0833
        
        assert round(pf["employer_epf_contribution"], 2) == round(expected_epf, 2), \
            f"Employer EPF contribution should be {expected_epf}"
        
        assert round(pf["employer_pension_contribution"], 2) == round(expected_pension, 2), \
            f"Employer pension contribution should be {expected_pension}"


# Test ESI calculation
class TestESI:
    
    def test_esi_below_threshold(self, calculator):
        """Test ESI calculation below income threshold."""
        gross_salary = 15000
        esi = calculator.calculate_esi(gross_salary)
        
        expected_employee_contribution = gross_salary * 0.0075
        expected_employer_contribution = gross_salary * 0.0325
        
        assert esi["applicable"] is True, "ESI should be applicable"
        assert esi["employee_contribution"] == expected_employee_contribution, \
            f"Employee ESI contribution should be {expected_employee_contribution}"
        assert esi["employer_contribution"] == expected_employer_contribution, \
            f"Employer ESI contribution should be {expected_employer_contribution}"
    
    def test_esi_above_threshold(self, calculator, maharashtra_data):
        """Test ESI calculation above income threshold."""
        threshold = maharashtra_data["esi"]["income_threshold"]
        gross_salary = threshold + 1000
        esi = calculator.calculate_esi(gross_salary)
        
        assert esi["applicable"] is False, "ESI should not be applicable"
        assert esi["employee_contribution"] == 0, "Employee ESI contribution should be 0"
        assert esi["employer_contribution"] == 0, "Employer ESI contribution should be 0"


# Test net salary calculation
class TestNetSalary:
    
    def test_net_salary_calculation(self, calculator):
        """Test complete net salary calculation."""
        ctc = 300000  # Annual CTC
        base_salary = 15000  # Monthly base salary
        benefits = {"hra": 6000, "conveyance": 1000}
        
        result = calculator.calculate_net_salary(ctc, base_salary, benefits)
        
        # Basic validation of result structure
        assert "employee_details" in result, "Result should contain employee_details"
        assert "employer_contributions" in result, "Result should contain employer_contributions"
        assert "ctc" in result, "Result should contain ctc"
        assert "compliance" in result, "Result should contain compliance"
        
        # Validate monthly calculation
        monthly = result["employee_details"]["monthly"]
        assert monthly["base_salary"] == base_salary, "Base salary should match input"
        assert monthly["gross_salary"] == base_salary + sum(benefits.values()), "Gross salary calculation error"
        
        # Validate deductions
        deductions = monthly["deductions"]
        assert "professional_tax" in deductions, "Professional tax should be calculated"
        assert "pf_contribution" in deductions, "PF contribution should be calculated"
        assert "esi_contribution" in deductions, "ESI contribution should be calculated"
        
        # Validate net salary
        assert monthly["net_salary"] == monthly["gross_salary"] - deductions["total_deductions"], \
            "Net salary calculation error"