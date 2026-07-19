import os
import requests

# 1. Path to your local dirty dataset
CSV_PATH = "test_dirty_data.csv"

# 2. YOUR N8N WEBHOOK URL
# Replace this with the live Webhook URL from your n8n canvas
WEBHOOK_URL = "https://khanaayaan422.app.n8n.cloud/webhook-test/data-input" 

def send_data_to_agent():
    if not os.path.exists(CSV_PATH):
        print(f" Error: Could not find {CSV_PATH} in the current directory.")
        return

    print(f" Reading local data from {CSV_PATH}...")
    with open(CSV_PATH, "r") as file:
        raw_csv_data = file.read()

    # Package the raw text content exactly how your AI Agent expects it
    payload = {
        "body": {
            "data": raw_csv_data
        }
    }

    print(f" Sending dataset to n8n Cloud Agent...")
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 200:
            print(" Success! The AI Agent has received the data and is processing it.")
            print("\n Agent Response Response:")
            print(response.text)
        else:
            print(f" Sent, but received status code {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f" Connection failed: {str(e)}")

if __name__ == "__main__":
    send_data_to_agent()