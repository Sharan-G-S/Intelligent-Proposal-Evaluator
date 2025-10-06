import pandas as pd
import json
import os

# Define the file paths based on our project structure
excel_file_path = 'data/raw/mock_project_database.xlsx'
content_folder_path = 'data/raw/proposals/content/'
output_json_path = 'data/processed/knowledge_base.json'

def create_knowledge_base():
    """
    Reads the Excel file and the individual text files, then combines them
    into a single structured JSON file.
    """
    print("Starting the knowledge base creation process...")

    # Read the metadata from the Excel file
    try:
        # --- THIS IS THE CORRECTED LINE ---
        df = pd.read_excel(excel_file_path, engine='openpyxl')
        print(f"Successfully loaded {len(df)} records from {excel_file_path}")
    except FileNotFoundError:
        print(f"Error: The file {excel_file_path} was not found.")
        return

    knowledge_base = []
    
    # Loop through each row in the Excel data
    for index, row in df.iterrows():
        project_id = row['Project_ID']
        text_file_name = f"{project_id}.txt"
        text_file_path = os.path.join(content_folder_path, text_file_name)

        full_text = ""
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except FileNotFoundError:
            print(f"Warning: Text file not found for {project_id} at {text_file_path}. Skipping content.")
        
        # Create a dictionary for the current project
        project_data = {
            "project_id": project_id,
            "project_title": row['Project_Title'],
            "implementing_agency": row['Implementing_Agency'],
            "year": int(row['Year']),
            "status": row['Status'],
            "full_text": full_text
        }
        
        knowledge_base.append(project_data)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    # Write the combined data to the output JSON file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=4)
        
    print(f"\nSuccessfully created the knowledge base with {len(knowledge_base)} entries.")
    print(f"Master JSON file saved to: {output_json_path}")


if __name__ == "__main__":
    create_knowledge_base()