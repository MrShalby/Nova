import re
import math  # Importing math module for square root calculation

def extract_calculation(query):
    """Extracts the calculation expression from the query."""
    # Assuming the query is in the format "calculate <expression>"
    expression = query.replace("calculate", "").strip()
    # Replace "into" with "*"
    expression = expression.replace("into", "*")
    return expression
def calculate(expression):
    """Evaluates the mathematical expression and returns the result."""
    # Remove any non-mathematical characters (except for numbers, operators, and parentheses)
    expression = re.sub(r'[^0-9+\-*x/(). sqrt]', '', expression)
    
    # Replace "sqrt" with "math.sqrt" to use the math module's square root function
    expression = expression.replace("sqrt", "math.sqrt")
    
    # Replace "x" with "*" for multiplication
    expression = expression.replace("x", "*")
    
    try:
        # Using eval to calculate the result of the expression
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        return "There was an error calculating the result."
    
    try:
        # Using eval to calculate the result of the expression
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        return "There was an error calculating the result."