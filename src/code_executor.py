# src/code_executor.py
import sys
import os
import pandas as pd
from LLM_client import ask_analyst

EXECUTOR_PERSONA = """
You are an expert automated data cleaning engineer. Your only job is to write pure, 
executable Python code using pandas to clean a dataset based on a provided cleaning plan.

CRITICAL RULES:
1. Output ONLY executable Python code. 
2. Do NOT wrap the code in markdown blocks like ```python ... ```.
3. Assume the input dataset is loaded into a variable named 'df'.
4. Save the finalized, cleaned dataframe back to the variable 'df'.
5. Do not include comments, explanations, or prose. Just raw code.
"""

def execute_autonomous_cleaning(file_path: str, cleaning_plan: str):
    """Asks Gemini to write pandas code based on the plan, then runs it on the file."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    try:
        print(f"Loading target dataset for active cleaning: {file_path}")
        df = pd.read_csv(file_path)
        
        # Structure the prompt for code generation
        prompt = f"""
        Based on the following data cleaning plan, write the exact Python pandas code to clean the dataframe 'df'.
        
        --- DATA CLEANING PLAN ---
        {cleaning_plan}
        
        Write code that explicitly:
        - Replaces "invalid_str" in revenue and converts it to float.
        - Handles missing values in age and country.
        - Fixes or nullifies "missing_date" strings in signup_date.
        """
        
        print(" Agent is generating execution code...")
        generated_code = ask_analyst(prompt, system_instruction=EXECUTOR_PERSONA)
        
        # Clean up any accidental formatting strings the LLM might have returned
        clean_code = generated_code.replace("```python", "").replace("```", "").strip()
        
        print("\n--- GENERATED CODE TO EXECUTE ---")
        print(clean_code)
        print("---------------------------------\n")
        
        print(" Executing generated code in an isolated scope...")
        # Create a local environment context for the code execution
        local_vars = {'df': df, 'pd': pd}
        exec(clean_code, globals(), local_vars)
        
        # Extract the modified dataframe out of the execution context
        cleaned_df = local_vars['df']
        
        # Save the result to a new file
        output_path = file_path.replace(".csv", "_pristine.csv")
        cleaned_df.to_csv(output_path, index=False)
        print(f" Success! Autonomous clean complete. Saved to: {output_path}")
        
        print("\n Preview of Cleaned Dataset:")
        print(cleaned_df.to_string())
        
    except Exception as e:
        print(f" Execution failed: {str(e)}")

if __name__ == "__main__":
    # For testing purposes, let's pass a file path and a mini manual test plan
    if len(sys.argv) > 1:
        sample_plan = "Convert revenue to numeric, replace invalid rows with median, fill country with 'Unknown'"
        execute_autonomous_cleaning(sys.argv[1], sample_plan)
    else:
        print("Usage: python src/code_executor.py <path_to_csv_file>")