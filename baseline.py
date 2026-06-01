import hashlib
import os
import json
import tkinter as  tk
from hasher import generate_hash
from tkinter import filedialog, messagebox

#This block asks the user whether they want to monitor a folder or a file
def select_target():
    root = tk.Tk()
    root.withdraw()

    user_choice = messagebox.askquestion(
        "Select File/Folder",
        "Do you want to monitor a folder or a file? \n\n Click 'Yes' for a folder, 'No' for a single file "
    )

    if user_choice == 'yes':
        path = filedialog.askdirectory(title="Select folder to monitor")
    else:
        path = filedialog.askopenfilename(title="Select file to monitor")

    return path 

#This function handles the user's choice, generates the hash and saves it to baseline.json
def create_baseline(target):
    baseline = {}

    if os.path.isfile(target):
        try:
            baseline[target] = generate_hash(target)
            print(f"Hashed file: {target}")
        except (PermissionError, FileNotFoundError) as e:
            print(f"Skipped: {target} - {e}")
    else:
        for root, dirs, files in os.walk(target):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    baseline[file_path] = generate_hash(file_path)
                    print(f"Hashed: {file_path}")
                except (PermissionError, FileNotFoundError) as e:
                    print(f"Skipped: {file_path} - {e}")

    with open('baseline.json', 'w') as f:
        json.dump(baseline, f, indent=4)

    print(f"\nBaseline hash created successfully for: {target}")
    return baseline

#Only runs when I execute this script directly, it won't run when another script imports from this script
if __name__ == "__main__":
    target = select_target()

    if not target:
        print("No file or folder has been selected.")
    else:
        print(f"Selected file/folder: {target}")
        create_baseline(target)
        messagebox.showinfo(
            "Success",
            f"Baseline has been created successfully for: \n {target}"
        )