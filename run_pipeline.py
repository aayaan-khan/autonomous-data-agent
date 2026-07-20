import os
import json
import pandas as pd
import requests

CSV_PATH = "test_dirty_data.csv"
OUTPUT_JSON = "clean_data.json"
OUTPUT_CSV = "clean_data.csv"
WEBHOOK_URL = "https://khanaayaan422.app.n8n.cloud/webhook-test/data-input" 

# Adjust batch size depending on dataset density
BATCH_SIZE = 50  

def process_batch(batch_csv_str):
    """Sends a single chunk of CSV data to the n8n agent."""
    payload = {"body": {"data": batch_csv_str}}
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            # Extract content from response wrapper
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get("output", data[0])
            elif isinstance(data, dict):
                content = data.get("output", data)
            else:
                content = data

            if isinstance(content, str):
                cleaned = content.strip().replace("```json", "").replace("```", "")
                return json.loads(cleaned)
            return content
        else:
            print(f"⚠️ Batch failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error processing batch: {str(e)}")
        return None

def run_pipeline():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found!")
        return

    print(f"📖 Loading dataset from {CSV_PATH}...")
    
    # Read CSV using pandas for easy chunking
    df = pd.read_csv(CSV_PATH)
    total_rows = len(df)
    print(f"📊 Total records detected: {total_rows}")

    all_cleaned_records = []

    # Process in batches
    for start_idx in range(0, total_rows, BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, total_rows)
        chunk = df.iloc[start_idx:end_idx]
        
        chunk_csv_str = chunk.to_csv(index=False)
        print(f"🚀 Processing rows {start_idx + 1} to {end_idx}...")

        cleaned_batch = process_batch(chunk_csv_str)
        if cleaned_batch:
            if isinstance(cleaned_batch, list):
                all_cleaned_records.extend(cleaned_batch)
            else:
                all_cleaned_records.append(cleaned_batch)

    if not all_cleaned_records:
        print("❌ No data was successfully cleaned.")
        return

    # 1. Save complete JSON output
    with open(OUTPUT_JSON, "w") as f:
        json.dump(all_cleaned_records, f, indent=4)
    print(f"✨ Saved aggregated JSON to: {OUTPUT_JSON}")

    # 2. Export to clean CSV format
    try:
        clean_df = pd.DataFrame(all_cleaned_records)
        clean_df.to_csv(OUTPUT_CSV, index=False)
        print(f"✨ Saved clean dataset CSV to: {OUTPUT_CSV}")
    except Exception as e:
        print(f"⚠️ Could not convert to CSV: {str(e)}")

if __name__ == "__main__":
    run_pipeline()