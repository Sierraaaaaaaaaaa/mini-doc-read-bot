import time
from openai import OpenAI

# Initialize the OpenAI client (it automatically picks up the OPENAI_API_KEY environment variable)
client = OpenAI()

def delete_all_files():
    print("Fetching files from OpenAI storage...")
    # List all files currently in your storage
    files = client.files.list()
    
    file_list = list(files.data)
    total_files = len(file_list)
    
    if total_files == 0:
        print("No files found in storage.")
        return

    # Danger zone confirmation
    confirm = input(f"Are you sure you want to permanently delete ALL {total_files} files? (Type 'YES' to confirm): ")
    if confirm != "YES":
        print("Operation cancelled.")
        return

    # Loop through and delete each file
    for index, file in enumerate(file_list, start=1):
        try:
            print(f"[{index}/{total_files}] Deleting file: {file.id} ({file.filename})...")
            client.files.delete(file.id)
            # Brief pause to respect API rate limits safely
            time.sleep(0.1) 
        except Exception as e:
            print(f"Failed to delete {file.id}: {e}")

    print("\nBulk deletion completed successfully.")

if __name__ == "__main__":
    delete_all_files()
