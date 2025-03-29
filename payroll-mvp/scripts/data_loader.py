import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import Settings
from config.logger import logger


def load_state_data(state: str, data: dict) -> None:
    """
    Load or update state data file.
    
    Args:
        state: State name (case-insensitive)
        data: State data dictionary
    """
    state = state.lower()
    file_path = Settings.get_state_file_path(state)
    
    # Create data directory if it doesn't exist
    os.makedirs(Settings.DATA_DIR, exist_ok=True)
    
    # Write data to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Updated data file for {state}")


def load_default_states() -> None:
    """
    Load default data for supported states.
    """
    # Maharashtra data
    maharashtra_data = {
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
    
    # Karnataka data
    karnataka_data = {
        "state_name": "Karnataka",
        "professional_tax": {
            "monthly_slabs": [
                {"min": 0, "max": 15000, "tax": 0},
                {"min": 15001, "max": 25000, "tax": 200},
                {"min": 25001, "max": None, "tax": 300}
            ],
            "annual_ceiling": 2400
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
            "minimum_wage_threshold": 142
        },
        "labour_welfare_fund": {
            "employee_contribution": 20,
            "employer_contribution": 40,
            "payment_frequency": "annual"
        }
    }
    
    # Load data for states
    load_state_data("maharashtra", maharashtra_data)
    load_state_data("karnataka", karnataka_data)
    
    logger.info("Loaded default data for all supported states")


if __name__ == "__main__":
    # Create directories
    Settings.create_directories()
    
    # Load default state data
    load_default_states()