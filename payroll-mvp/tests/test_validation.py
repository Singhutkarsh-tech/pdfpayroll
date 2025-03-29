import sys
import os
import pytest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.validator import PayrollValidator


@pytest.fixture
def validator():
    """Fixture for PayrollValidator instance."""
    return PayrollValidator(["maharashtra", "karnataka"])


class TestLocationValidation:
    
    def test_valid_location(self, validator):
        """Test validation of valid locations."""
        # Test case-insensitive validation
        assert validator.validate_location("Maharashtra") == "maharashtra", \
            "Should accept Maharashtra and return lowercase"
        
        assert validator.validate_location("KARNATAKA") == "karnataka", \
            "Should accept KARNATAKA and return lowercase"
        
        assert validator.validate_location("karnataka") == "karnataka", \
            "Should accept already lowercase karnataka"
    
    def test_invalid_location(self, validator):
        """Test validation of invalid locations."""
        with pytest.raises(ValueError) as excinfo:
            validator.validate_location("Delhi")
        
        assert "not in allowed states" in str(excinfo.value), \
            "Should raise ValueError for invalid state"
        
        # Check if error message includes allowed states
        for state in ["maharashtra", "karnataka"]:
            assert state in str(excinfo.value).lower(), \
                f"Error message should mention {state} as an allowed state"


class TestSalaryValidation:
    
    def test_valid_salary(self, validator):
        """Test validation of valid salary components."""
        ctc = 300000  # Annual CTC
        base_salary = 15000  # Monthly base salary
        benefits = {"hra": 6000, "conveyance": 1000}
        
        # Monthly gross: 22,000
        # Monthly CTC: 25,000
        
        assert validator.validate_salary(ctc, base_salary, benefits) is True, \
            "Should accept valid salary components"
    
    def test_negative_values(self, validator):
        """Test validation with negative values."""
        with pytest.raises(ValueError) as excinfo:
            validator.validate_salary(-300000, 15000, {"hra": 6000})
        
        assert "CTC must be positive" in str(excinfo.value), \
            "Should reject negative CTC"
        
        with pytest.raises(ValueError) as excinfo:
            validator.validate_salary(300000, -15000, {"hra": 6000})
        
        assert "Base salary must be positive" in str(excinfo.value), \
            "Should reject negative base salary"
        
        with pytest.raises(ValueError) as excinfo:
            validator.validate_salary(300000, 15000, {"hra": -6000})
        
        assert "cannot be negative" in str(excinfo.value), \
            "Should reject negative benefits"
    
    def test_gross_exceeds_ctc(self, validator):
        """Test validation when gross salary exceeds CTC."""
        ctc = 300000  # Annual CTC: 25,000 monthly
        base_salary = 20000  # Monthly base salary
        benefits = {"hra": 8000, "conveyance": 2000}  # Total: 10,000
        
        # Monthly gross: 30,000
        # Monthly CTC: 25,000
        
        with pytest.raises(ValueError) as excinfo:
            validator.validate_salary(ctc, base_salary, benefits)
        
        assert "exceeds monthly CTC" in str(excinfo.value), \
            "Should reject when gross salary exceeds monthly CTC"


class TestEmployeeDataValidation:
    
    def test_missing_required_fields(self, validator):
        """Test validation of missing required fields."""
        # Missing CTC
        with pytest.raises(ValueError) as excinfo:
            validator.validate_employee_data({
                "base_salary": 15000,
                "location": "Maharashtra"
            })
        
        assert "Required field 'ctc' is missing" in str(excinfo.value), \
            "Should detect missing CTC field"
        
        # Missing base_salary
        with pytest.raises(ValueError) as excinfo:
            validator.validate_employee_data({
                "ctc": 300000,
                "location": "Maharashtra"
            })
        
        assert "Required field 'base_salary' is missing" in str(excinfo.value), \
            "Should detect missing base_salary field"
        
        # Missing location
        with pytest.raises(ValueError) as excinfo:
            validator.validate_employee_data({
                "ctc": 300000,
                "base_salary": 15000
            })
        
        assert "Required field 'location' is missing" in str(excinfo.value), \
            "Should detect missing location field"
    
    def test_complete_validation(self, validator):
        """Test complete employee data validation."""
        # Valid data
        employee_data = {
            "ctc": 300000,
            "base_salary": 15000,
            "location": "Maharashtra",
            "benefits": {"hra": 6000, "conveyance": 1000}
        }
        
        validated_data = validator.validate_employee_data(employee_data)
        
        assert validated_data["location"] == "maharashtra", \
            "Should normalize location to lowercase"
        
        # Invalid location
        employee_data["location"] = "Delhi"
        
        with pytest.raises(ValueError) as excinfo:
            validator.validate_employee_data(employee_data)
        
        assert "not in allowed states" in str(excinfo.value), \
            "Should reject invalid location"
        
        # Invalid salary components
        employee_data["location"] = "Maharashtra"
        employee_data["base_salary"] = 30000  # Too high for the CTC
        
        with pytest.raises(ValueError) as excinfo:
            validator.validate_employee_data(employee_data)
        
        assert "exceeds monthly CTC" in str(excinfo.value), \
            "Should reject when salary components are invalid"