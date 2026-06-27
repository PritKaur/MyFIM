import hashlib
import os #Lets you interact with the file system
import json #Lets you convert between JSON text and python dictionaries
import tkinter as  tk #Python's GUI library used for the pop-up windows 
from hasher import generate_hash #Function from hasher.py
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet #The encryption tool from the cryptography library
import sys

#Encryption function blocks
#This block checks if secret key exists, if it does then it loads it, and if it doesn't then it creates one and saves it
def create_or_load_key():
    key_file = "secret.key"

    if not os.path.exists(key_file): #Checks whether secret.key is already there
        key = Fernet.generate_key() #This will generate a random key if there's no existing secret.key
        with open(key_file, "wb") as f:
            f.write(key)
        print("New encryption key has been created: secret.key")
    else:
        with open(key_file, "rb") as f: #If a key exists, it's just read
            key = f.read()
        print("Existing encryption key has been loaded.")

    return key #The key is returned so that it can be used to encrypt and/or decrypt

#This block converts the baseline dictionary into a JSON string that is encrypted and writes them to baseline.json
def save_encrypted_baseline(baseline: dict):
    key = create_or_load_key()
    fernet = Fernet(key)

    json_bytes = json.dumps(baseline, indent=4).encode("utf-8") #Turns the dictionary into a JSON string and encodes it into bytes

    encrypted = fernet.encrypt(json_bytes) #This encrypts those bytes

    with open("baseline.json", "wb") as f: #The encrypted bytes are then written to baseline.json
        f.write(encrypted)

    print("Baseline has been saved to baseline.json successfully")

#This block will read baseline.json and decrypt it using secret.key to recover the original dictionary
def load_decrypted_baseline() -> dict: #This function does the exact reverse of saving the baseline hash
    key = create_or_load_key()
    fernet = Fernet(key)

    with open("baseline.json", "rb") as f: #This reads the raw encrypted bytes from baseline.json
        encrypted = f.read()

    json_bytes = fernet.decrypt(encrypted) #Converts the encrypted bytes back to the original form
    baseline = json.loads(json_bytes.decode("utf-8")) #The decode here converts the bytes back into a string and the json.loads converts the JSON string back into a python dictionary

    print("Baseline has been loaded and decrypted successfully")
    baseline = {os.path.normpath(k): v for k, v in baseline.items()} #What os.path.normpath does is that it cleans up a file path string without touching the actual filesystem, so it cleans up a meessy file path into a standard form, on windows it makes slashes \ and / consistent 
    return baseline

#This block asks the user whether they want to monitor a folder or a file
def select_target():
    root = tk.Tk() #This creates the main window that is hidden and needed by the tkinter before tkinter can show any pop-up
    root.withdraw() #This immediately hides it so that only the dialog box is seen, and not an empty window

    user_choice = messagebox.askquestion( #This will now show the Yes/No pop-up
        "Select File/Folder",
        "Do you want to monitor a folder or a file? \n\n Click 'Yes' for a folder, 'No' for a single file "
    )

    if user_choice == 'yes':
        path = filedialog.askdirectory(title="Select folder to monitor")
    else:
        path = filedialog.askopenfilename(title="Select file to monitor")

    return path #The chosen file path will be returned as a string

#This function will save the monitored path to config.json so that monitor.py can read it automatically instead of asking the user to select the file/folder for monitoring again
def save_monitored_file_path(target):
    with open("config.json", "w") as f: #Opens config.json in write mode
        json.dump({"monitored_path": target}, f) #Writes the path into config.json
    print(f"Monitored file path has been saved to config.json: {target}")

#This function handles the user's choice, generates the hash and saves it to baseline.json
def create_baseline(target, existing_baseline=None): #Takes the target file path and an existing baseline dictionary if it's there
    baseline = existing_baseline if existing_baseline else{} #If there is an existing baseline for a file or folder the user selected in a previous session, they can decide to continue with it

    if os.path.isfile(target): #This will check if the target is a single file or a whole folder
        try:
            baseline[target] = generate_hash(target) #Hashes and stores result in dictionary
            print(f"Hashed file: {target}")
        except (PermissionError, FileNotFoundError) as e: #Catches the errors no read permission or file doesn't exist
            print(f"Skipped: {target} - {e}")
    else: #Code executed if the target is a folder
        for root, dirs, files in os.walk(target): #root is the current directory path, dirs is list of subdirectories and files is list of files in the folder
            for file in files: #Loops through every file in the directory
                file_path = os.path.join(root, file) #builds the file path
                try:
                    baseline[file_path] = generate_hash(file_path) #Hashes and stores result in dictionary under its full path
                    print(f"Hashed: {file_path}")
                except (PermissionError, FileNotFoundError) as e:
                    print(f"Skipped: {file_path} - {e}")

    save_encrypted_baseline(baseline) #Saves the completed baseline dictionary to storage
    save_monitored_file_path(target) #Saves the monitored file path in config.json for future use

    print(f"\nBaseline hash created successfully for: {target}")
    return baseline #returns the baseline dictionary so it can be used immediately without having to be reloaded from the disk

#Only runs when I execute this script directly, it won't run when another script imports from this script
if __name__ == "__main__":
    raw_target = select_target()

    #Checks if raw_target is "falsy" meaning empty
    if not raw_target: #Triggered if the user closes the file picker dialog without picking anything
        print("No file or folder has been selected.")
        sys.exit(1) #So baseline.py can exit with a non-zero code (a unix/windows convention meaning "program failed") when the user doesn't select anything
    else: #Triggered if a target was selected by the user
        target = os.path.normpath(raw_target) #Cleans up the path string
        print(f"Selected file/folder: {target}")

        #This will load the existing baseline hash if the file exists in baseline.json
        existing_baseline = {}
        if os.path.exists("baseline.json"):
            existing_baseline = load_decrypted_baseline()

        #This will check if that file or folder has entries in the baseline.json
        target_already_exists = any(os.path.normpath(path).startswith(target) for path in existing_baseline.keys())

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
                save_monitored_file_path(target)
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