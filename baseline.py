import hashlib
import os
import json
import tkinter as  tk
from hasher import generate_hash
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet

#Encryption function blocks
#This block checks if secret key exists, if it does then it loads it, and if it doesn't then it creates one and saves it
def create_or_load_key():
    key_file = "secret.key"

    if not os.path.exists(key_file):
        key = Fernet.generate_key() #This will generate a random key
        with open(key_file, "wb") as f:
            f.write(key)
        print("New encryption key has been created: secret.key")
    else:
        with open(key_file, "rb") as f:
            key = f.read()
        print("Existing encryption key has been loaded.")

    return key

#This block converts the baseline dictionary into a JSON string that is encrypted and writes them to baseline.json
def save_encrypted_baseline(baseline: dict):
    key = create_or_load_key()
    fernet = Fernet(key)

    json_bytes = json.dumps(baseline, indent=4).encode("utf-8") #Turns the dictionary into a JSON string and encodes it into bytes

    encrypted = fernet.encrypt(json_bytes) #This encrypts those bytes

    with open("baseline.json", "wb") as f:
        f.write(encrypted)

    print("Baseline has been saved to baseline.json successfully")

#This block will read baseline.json and decrypt it using secret.key to recover the original dictionary
def load_decrypted_baseline() -> dict:
    key = create_or_load_key()
    fernet = Fernet(key)

    with open("baseline.json", "rb") as f:
        encrypted = f.read()

    json_bytes = fernet.decrypt(encrypted)
    baseline = json.loads(json_bytes.decode("utf-8"))

    print("Baseline has been loaded and decrypted successfully")
    return baseline

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
def create_baseline(target, existing_baseline=None):
    baseline = existing_baseline if existing_baseline else{} #If there is an existing baseline for a file or folder the user selected in a previous session, they can decide to continue with it

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

    save_encrypted_baseline(baseline)

    print(f"\nBaseline hash created successfully for: {target}")
    return baseline

#Only runs when I execute this script directly, it won't run when another script imports from this script
if __name__ == "__main__":
    target = select_target()

    if not target:
        print("No file or folder has been selected.")
    else:
        print(f"Selected file/folder: {target}")

        #This will load the existing baseline hash if the file exists in baseline.json
        existing_baseline = {}
        if os.path.exists("baseline.json"):
            existing_baseline = load_decrypted_baseline()

        #This will check if that file or folder has entries in the baseline.json
        target_already_exists = any(path.startswith(target) for path in existing_baseline.keys())

        if target_already_exists: #The selected file/folder has been monitored before
            user_choice = messagebox.askquestion(
                "Secure Baseline Found",
                "A baseline (secure reference used for integrity monitoring) already exists for this folder/file.\n\n"
                "Would you like to continue monitoring your folder/file using this existing baseline?\n\n"
                "Click 'Yes' to continue with the existing baseline.\n"
                "Click 'No' to create a new baseline."
            )
            if user_choice == "yes": #If a baseline exists
                baseline = existing_baseline
                messagebox.showinfo(
                    "Existing baseline (secure reference) loaded",
                    "Your existing secure reference has been loaded.\n"
                    "File monitoring will now begin."
                )
            else: #If a baseline doesn't exist, a new one will be created
                baseline = create_baseline(target, existing_baseline)
                messagebox.showinfo(
                    "Baseline Created",
                    f"A fresh security reference has been created successfully for: \n{target}"
                )
        else: #The selected file/folder has never been monitored before
            baseline = create_baseline(target, existing_baseline)
            messagebox.showinfo(
                "Baseline Created",
                f"A security reference has been created successfully for:\n{target}"
            )