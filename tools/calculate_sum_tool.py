"""Calculate sum tool module."""

from typing import Union, Dict, Any

def calculate_sum(number_a: str, number_b: str) -> Dict[str, Any]:
    """
    Calculate the sum of two numbers for testing purposes

    Parameters
    ----------
        number_a (str): First number to add
        number_b (str): Second number to add

    Returns
    -------
    Dict[str, Any]
        Result containing the sum and operation details.
    """
    try:
        # Convert string parameters to float
        num_a = float(number_a)
        num_b = float(number_b)
        
        result = num_a + num_b
        
        return {
            "success": True,
            "result": result,
            "operation": f"{num_a} + {num_b} = {result}",
            "inputs": {
                "number_a": number_a,
                "number_b": number_b
            }
        }
    except (ValueError, TypeError) as e:
        return {
            "success": False,
            "error": f"Invalid input: {str(e)}. Please provide valid numbers.",
            "operation": "calculate_sum",
            "inputs": {
                "number_a": number_a,
                "number_b": number_b
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "operation": "calculate_sum",
            "inputs": {
                "number_a": number_a,
                "number_b": number_b
            }
        }
