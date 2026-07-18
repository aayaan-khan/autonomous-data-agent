import os
import sys
import traceback
import pandas as pd

from LLM_client import ask_analyst


SYSTEM_PERSONA = """
You are an expert Senior Data Analyst.

Your task is to inspect raw dataset metadata,
identify anomalies,
and produce a professional data-cleaning plan.

Do NOT write Python code.

Return the answer in Markdown.
"""


def profile_and_plan(file_path: str):
    """
    Reads a CSV file,
    profiles the dataset,
    and asks Gemini for a cleaning strategy.
    """

    if not os.path.exists(file_path):
        print(f" File not found: {file_path}")
        return

    try:

        print(f" Reading dataset: {file_path}")

        df = pd.read_csv(file_path)

        total_rows = len(df)
        total_cols = len(df.columns)

        missing_values = df.isnull().sum().to_dict()

        # FIXED
        data_types = df.dtypes.astype(str).to_dict()

        sample_data = df.head(5).to_markdown(index=False)

        prompt = f"""
Analyze the following dataset metadata.

Dataset Information

File:
{file_path}

Rows:
{total_rows}

Columns:
{total_cols}

Column Types

{data_types}

Missing Values

{missing_values}

Sample Data

{sample_data}

Generate a professional report with:

# Dataset Health Report

# Data Quality Issues

# Cleaning Recommendations

# Cleaning Priority

# Final Summary

Do NOT generate code.
"""

        print("🤖 Asking Gemini...\n")

        analysis = ask_analyst(
            prompt=prompt,
            system_instruction=SYSTEM_PERSONA,
        )

        print("=" * 80)
        print(analysis)
        print("=" * 80)

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python src/data_cleaner.py <csv_file>")
    else:
        profile_and_plan(sys.argv[1])