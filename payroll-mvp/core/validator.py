from typing import Dict, Any, List, Optional, Union
import json
from pathlib import Path


class PayrollValidator:
    """
    Validator class for payroll inputs.
    
    Validates employee location, salary components, and ensures
    all inputs conform to business and compliance rules.
    """
    
    def __init__(self, allowed_states: Optional[List[str]] = None):
        """
        Initialize validator with allowed states.
        
        Args:
            allowed_states: List of allowed state names (defaults to Maharashtra and Karnataka)
        """
        if allowed_states is None:
            self.allowed_states = ["maharashtra", "karnataka"]
        else:
            self.allowed_states = [state.lower() for state in allowed_states]
            
        # Load all state data for validation
        self.state_data = {}
        data_dir = Path(__file__).parent.parent / "data"
        
        for state in self.allowed_states:
            try:
                state_file = data_dir / f"{state}.json"
                with open(state_file, "r") as f:
                    self.state_data[state] = json.load(f)
            except FileNotFoundError:
                # Skip if state file not found
                pass
    
    def validate_location(self, location: str) -> str:
        """
        Validate if location is in allowed states.
        
        Args:
            location: State name for employee
            
        Returns:
            Normalized state name (lowercase)
            
        Raises:
            ValueError: If location is not in allowed states
        """
        location = location.lower()
        
        if location not in self.allowed_states:
            allowed_states_str = ", ".join(self.allowed_states)
            raise ValueError(
                f"Location '{location}' is not in allowed states. "
                f"Allowed states are: {allowed_states_str}"
            )
        
        return location
    
    def validate_salary(self, ctc: float, base_salary: float, 
                        benefits: Dict[str, float]) -> bool:
        """
        Validate salary components and their relationships.
        
        Args:
            ctc: Cost to Company (annual)
            base_salary: Monthly base salary
            benefits: Dictionary of additional benefits
            
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        # Check for negative values
        if ctc <= 0:
            raise ValueError("CTC must be positive")
        
        if base_salary <= 0:
            raise ValueError("Base salary must be positive")
        
        for benefit_name, benefit_value in benefits.items():
            if benefit_value < 0:
                raise ValueError(f"Benefit '{benefit_name}' cannot be negative")
        
        # Calculate monthly CTC
        monthly_ctc = ctc / 12
        
        # Calculate gross salary (base + benefits)
        total_benefits = sum(benefits.values())
        gross_salary = base_salary + total_benefits
        
        # Validate that gross doesn't exceed monthly CTC
        # Allow for small rounding differences (1 rupee)
        if gross_salary > monthly_ctc + 1:
            raise ValueError(
                f"Total monthly gross salary ({gross_salary}) exceeds monthly CTC ({monthly_ctc}). "
                f"Either increase CTC or decrease salary components."
            )
        
        return True
    
    def validate_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all employee data for payroll processing.
        
        Args:
            employee_data: Complete employee data dictionary
            
        Returns:
            Validated and normalized employee data
            
        Raises:
            ValueError: If any validation fails
        """
        # Extract required fields
        required_fields = ["ctc", "base_salary", "location"]
        for field in required_fields:
            if field not in employee_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Get values with defaults
        ctc = float(employee_data["ctc"])
        base_salary = float(employee_data["base_salary"])
        location = employee_data["location"]
        benefits = employee_data.get("benefits", {})
        
        # Validate each component
        normalized_location = self.validate_location(location)
        self.validate_salary(ctc, base_salary, benefits)
        
        # Return normalized data
        normalized_data = employee_data.copy()
        normalized_data["location"] = normalized_location
        
        return normalized_data