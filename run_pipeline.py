import os
import json
import requests

CSV_PATH = "test_dirty_data.csv"
OUTPUT_PATH = "clean_data.json"
# Your active n8n test webhook URL
WEBHOOK_URL = "https://khanaayaan422.app.n8n.cloud/webhook-test/data-input" 

def send_data_to_agent():
    if not os.path.exists(CSV_PATH):
        print(f" Error: Could not find {CSV_PATH} in the current directory.")
        return

    print(f" Reading local data from {CSV_PATH}...")
    with open(CSV_PATH, "r") as file:
        raw_csv_data = file.read()

    payload = {
        "body": {
            "data": raw_csv_data
        }
    }

    print(f" Sending dataset to n8n Cloud Agent...")
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 200:
            print("AI Agent successfully processed the data.")
            
            # Parse the agent response
            try:
                response_data = response.json()
                
                # If n8n nests the agent output inside an object, extract it
                if isinstance(response_data, list) and len(response_data) > 0:
                    agent_output = response_data[0].get("output", response_data[0])
                elif isinstance(response_data, dict):
                    agent_output = response_data.get("output", response_data)
                else:
                    agent_output = response_data

                # If the agent output is stringified JSON, clean and parse it
                if isinstance(agent_output, str):
                    # Strip out accidental markdown blocks if present
                    cleaned_str = agent_output.strip().replace("```json", "").replace("```", "")
                    save_content = json.loads(cleaned_str)
                else:
                    save_content = agent_output

                # Save to local file system
                with open(OUTPUT_PATH, "w") as out_file:
                    json.dump(save_content, out_file, indent=4)
                
                print(f" Success! Automated clean data saved locally to: {OUTPUT_PATH}")
                
            except json.JSONDecodeError:
                print(" Warning: Received response, but could not parse it as clean JSON.")
                print("Raw response text below:")
                print(response.text)
        else:
            print(f" Sent, but received status code {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f" Connection failed: {str(e)}")

if __name__ == "__main__":
    send_data_to_agent()