#!/usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime  # Import datetime module

# Function to parse time difference string to milliseconds
def parse_time_diff(time_diff_str):
    # Regular expression pattern to match time difference formats
    time_pattern = re.compile(r'(\d+(\.\d+)?)([mµ]s|s)?')
    
    match = time_pattern.match(time_diff_str)
    if match:
        value = float(match.group(1))
        unit = match.group(3)
        if unit == 's':
            value *= 1000  # Convert seconds to milliseconds
        return value
    else:
        return None

def update_json_file(data):
    # GitHub repository information
    owner = "obi-wan-xenobi"
    repo = "Node-Ranking"
    branch = "main"
    filename = "nodes_data.json"
    
    # Personal Access Token (PAT)
    token = os.environ.get("GITHUB_PAT")  # Access the PAT stored as environment variable
    
    # GitHub API URL for updating file content
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    
    # Compose the request headers
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Fetch the current content of the JSON file
    response = requests.get(url, headers=headers)
    response_json = response.json()
    
    # Decode the content from base64
    current_content = json.loads(requests.utils.decode_base64(response_json["content"]))
    
    # Merge the new data with the existing content
    current_content.extend(data)
    
    # Add timestamp to the data
    timestamp = datetime.now().isoformat()
    current_content.append({"Last Updated": timestamp})  # Add timestamp field
    
    # Encode the updated content to JSON
    updated_content = json.dumps(current_content, indent=4)
    
    # Compose the request payload
    payload = {
        "message": "Update JSON file",
        "content": updated_content,
        "branch": branch,
        "sha": response_json["sha"]
    }
    
    # Make a PUT request to update the file
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("JSON file updated successfully.")
    else:
        print(f"Failed to update JSON file. Status code: {response.status_code}")

def main():
    # Send a GET request to the website
    url = "http://186.233.186.56:5002/nodes"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find the table containing the nodes information
        table = soup.find("table")
        
        # Initialize a list to store nodes data
        nodes_data = []
        
        # Iterate over each row in the table
        for row in table.find_all("tr")[1:]:
            # Extract data from each cell in the row
            cells = row.find_all("td")
            node_ip = cells[0].text
            block_id = int(cells[1].text)
            tx_hash = cells[2].text
            time_diff_str = cells[3].text
            time_diff = parse_time_diff(time_diff_str)
            if time_diff is not None:  # Check if time_diff is valid
                nodes_data.append({"Node IP": node_ip, "Block ID": block_id, "Time Diff": time_diff})
        
        # Sort the nodes based on their block ID and time differences
        sorted_nodes = sorted(nodes_data, key=lambda x: (-x["Block ID"], x["Time Diff"]))
        
        # Get the top 50 nodes with the highest block ID and lowest time differences
        top_50_nodes = sorted_nodes[:50]
        
        # Calculate the Xenobi ranking
        xenobi_ranking = None
        for i, node in enumerate(top_50_nodes, start=1):
            if node["Node IP"].startswith("74.50.77"):
                xenobi_ranking = i
                break
        
        # Add Xenobi ranking to the data
        if xenobi_ranking is not None:
            top_50_nodes.append({"Xenobi Ranking": xenobi_ranking})
        
        # Update the JSON file in the GitHub repository
        update_json_file(top_50_nodes)
    else:
        print("Failed to retrieve data from the website.")

if __name__ == "__main__":
    main()
