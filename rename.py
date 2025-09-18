import os
import re

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the "pictures" folder
img_folder = os.path.join(current_dir, "pictures")

# Function to rename files
def rename_files_in_folder(folder_path):
    try:
        # Iterate over all files in the folder
        for file_name in os.listdir(folder_path):
            # Check if the file is an image by its extension
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                # Extract the numeric part after "fn"
                match = re.search(r'(.*_fn)(\d+)(\..+)', file_name)
                if match:
                    prefix = match.group(1)  # Everything before the number
                    number = match.group(2)  # The numeric part
                    suffix = match.group(3)  # The file extension
                    
                    # Pad the number with leading zeros to make it 6 digits
                    padded_number = f"{int(number):06}"
                    
                    # Create the new filename
                    new_file_name = f"{prefix}{padded_number}{suffix}"
                    
                    # Full paths for renaming
                    old_path = os.path.join(folder_path, file_name)
                    new_path = os.path.join(folder_path, new_file_name)
                    
                    # Rename the file
                    os.rename(old_path, new_path)
                    print(f"Renamed: {file_name} -> {new_file_name}")
    except FileNotFoundError:
        print(f"The folder '{folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Rename files in the "pictures" folder
rename_files_in_folder(img_folder)
