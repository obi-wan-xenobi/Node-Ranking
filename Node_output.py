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
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        print("Response JSON:", response_json)  # Debug statement

        try:
            # Decode the content from base64
            current_content = json.loads(base64.b64decode(response_json["content"]).decode("utf-8"))
            
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
        except KeyError:
            print("KeyError: 'content' not found in response JSON.")
    else:
        print(f"Failed to fetch JSON file. Status code: {response.status_code}")
