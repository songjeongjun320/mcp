"""Calculate BMI tool module."""

from typing import Union, Dict, Any

def calculate_bmi(weight: str, height: str, unit_system: str = "metric") -> Dict[str, Any]:
    """
    Calculate BMI (Body Mass Index) based on height and weight

    Parameters
    ----------
        weight (str): Weight in kilograms (metric) or pounds (imperial)
        height (str): Height in meters (metric) or inches (imperial)
        unit_system (str): Unit system to use ('metric' or 'imperial')

    Returns
    -------
    Dict[str, Any]
        Result containing BMI value and classification.
    """
    try:
        # Convert string parameters to float
        weight_num = float(weight)
        height_num = float(height)
        
        # Convert imperial to metric if needed
        if unit_system.lower() == "imperial":
            weight_kg = weight_num * 0.453592  # pounds to kg
            height_m = height_num * 0.0254     # inches to meters
        else:
            weight_kg = weight_num
            height_m = height_num
        
        # Calculate BMI
        bmi = weight_kg / (height_m ** 2)
        
        # BMI classification
        if bmi < 18.5:
            classification = "Underweight"
        elif 18.5 <= bmi < 25:
            classification = "Normal weight"
        elif 25 <= bmi < 30:
            classification = "Overweight"
        else:
            classification = "Obese"
        
        return {
            "success": True,
            "bmi": round(bmi, 2),
            "classification": classification,
            "unit_system": unit_system,
            "inputs": {
                "weight": weight,
                "height": height,
                "weight_kg": round(weight_kg, 2),
                "height_m": round(height_m, 2)
            }
        }
    except (ValueError, TypeError) as e:
        return {
            "success": False,
            "error": f"Invalid input: {str(e)}. Please provide valid numbers.",
            "operation": "calculate_bmi",
            "inputs": {
                "weight": weight,
                "height": height,
                "unit_system": unit_system
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "operation": "calculate_bmi",
            "inputs": {
                "weight": weight,
                "height": height,
                "unit_system": unit_system
            }
        }
