import os #Lets you interact with the file system
import json #Lets you convert between JSON text and python dictionaries
import time #Used for pausing the program and getting the timestamp
from watchdog.observers import Observer #Observer watches the filesystem for events
from watchdog.events import FileSystemEventHandler #This imports a base class that helps define what to do when a file event happens
from hasher import generate_hash #Function from hasher.py
from baseline import load_decrypted_baseline #Function from baseline.py
from notifier import send_alert #Function from notifier.py

#Variables storing the filenames being used in the code 
baseline_file = "baseline.json"
alerts_file = "alerts.json"

#This function loads the folder path that was selected by the user and saved by baseline.py so the user doesn't have to select it again
def load_monitored_file_path():
    if not os.path.exists("config.json"): #Checks if config.json doesn't exist yet 
        print("No monitored file path found, please run baseline.py first")
        return None
    
    with open("config.json", "r") as f: #Opens config.json in read mode 
        config = json.load(f) #Parses config.json into a python dictionary called config

    return config.get("monitored_path") #Returns the value stored under "monitored_path"
    
#Saves the detected file change to alerts.json
def save_detection_alert(file_path, change_type, dest_path=None): #dest_path is optional because it depends if there's been a file that's been moved or renamed
    alerts = [] #Starts with an empty list that will hold all the file change alerts 

    #Loads existing  alerts that are in the alerts.json file if the file exists
    if os.path.exists(alerts_file):
        try: #Tries to load existing alerts into the list
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
        except (json.JSONDecodeError, OSError):
            alerts = [] #if the file is corrupted or undreadable, it resets it to empty instead of crashing
            
    #Adds a new alert to the alerts.json file
    alert = {
        "file": os.path.basename(file_path), #Extracts the file name only
        "path": file_path,
        "change_type": change_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S") #Format of the time
    }

    #This records the new path of the file if the file was renamed or moved
    if dest_path:
        alert["new_file"] = os.path.basename(dest_path)
        alert["new_path"] = dest_path

    alerts.append(alert) #Adds the new alert to the list of all alerts 

    #This will save the updated list of alerts back into alerts.json
    with open(alerts_file, 'w') as f:
        json.dump(alerts, f, indent=4) #The indent makes it human-readable

    print(f"Alert saved: {change_type} detected on the file {os.path.basename(file_path)}")

#This is the event handler that actually defines what happens when watchdog detects a file event
class MyFIMEventHandler(FileSystemEventHandler): #A custom class that inherits from FileSystemEventHandler
    def __init__(self, baseline, monitored_path): #This is the constructor that takes the baseline dictionary and path being monitored
        #The values are stored on self so other methods in the class can access them
        self.baseline = baseline
        self.monitored_path = monitored_path

        #This is an empty dictionary that tracks the last known hash per file to prevent duplicate alerts 
        self.last_known_hash = {}

        #This will handle a single file selection
        self.target_file = os.path.normpath(monitored_path) if os.path.isfile(monitored_path) else None
    
    def should_ignore(self, file_path):
        #This ignores  the tool's own files to prevent false file change alerts
        ignored = ["baseline.json", "alerts.json", "secret.key", "config.json"]
        return any(ignored_file in file_path for ignored_file in ignored)
    
    #This function will return True when the file event detected is for a different file that wasn't selected for monitoring, meaning it will be skipped
    def is_target_file(self, file_path):
        if self.target_file:
            return os.path.normpath(file_path) != os.path.normpath(self.target_file)
        return False #returned if a folder is being monitored, meaning nothing will be skipped

    def on_modified(self, event):
        #This will fire an alert when an existing file gets modified
        if event.is_directory: #Ignores if a directory is being modified, it's only interested in files
            return
        
        #These will skip internal files and files that are outside the target, meaning files that weren't selected
        if self.should_ignore(event.src_path):
            return
        if self.is_target_file(event.src_path):
            return

        file_path = event.src_path #Stores the path of the modified file into a variable called file_path

        try: 
            #Once watchdog has been fired, SHA-256 hasher will rehash the file
            new_hash = generate_hash(file_path)

            #If the hash matches the last hash, it skips it
            if self.last_known_hash.get(file_path) == new_hash:
                return
            
            #This will update the record of that file's last known hash
            self.last_known_hash[file_path] = new_hash

            #This will look up what the file's hash was in the trsuted baseline
            baseline_hash = self.baseline.get(os.path.normpath(file_path))

            #This will compare the new hash against the trusted baseline hash
            if new_hash != baseline_hash:
                #If the current hash doesn't match the baseline, that means file has been changed
                print(f"Modification has been detected: {file_path}")
                
                try:
                    save_detection_alert(file_path, "Modified")
                except OSError as e:
                    print(f"Could not save the alert for {file_path}: {e}")

                try:    
                    send_alert(os.path.basename(file_path), "Modified")
                except Exception as e: #This broader except Exception is there because failure could be because of anything since it's calling a third-party library, winotify
                    print(f"Could not send the notification for {file_path}: {e}")
            else:
                #If the hashes match, that means the file did not get changed
                print(f"No file change detected: {file_path}")

        except(FileNotFoundError, PermissionError) as e: #Handles errors where the file isn't the there or can't be read
            print(f"Could not hash the file: {file_path} - {e}")

    def on_created(self, event):
        file_path = event.src_path #Stores the path of the created file into a variable called file_path

        #This will fire an alert when a new file has been added
        if event.is_directory:
            return
        if self.should_ignore(event.src_path):
            return
        if self.is_target_file(event.src_path):
            return
        
        print(f"A new file has been detected: {event.src_path}")
        #save_detection_alert may only fail because of file I/O issues so maybe the disk is full, the file is locked, etc  
        try:
            save_detection_alert(event.src_path, "Created")
        except OSError as e:
            print(f"Could not save the alert for {file_path}: {e}")

        try:
            send_alert(os.path.basename(file_path), "Created")
        except Exception as e: #This broader except Exception is there because failure could be because of anything since it's calling a third-party library, winotify
            print(f"Could not send the notification for {file_path}: {e}")
        #Any new file will be suspicious because its not even in the baseline

    def on_deleted(self, event):
        file_path = event.src_path #Stores the path of the deleted file into a variable called file_path

        #This will fire an alert when a file has been deleted
        if event.is_directory:
            return
        if self.should_ignore(event.src_path):
            return
        if self.is_target_file(event.src_path):
            return
        
        if os.path.normpath(event.src_path) in self.baseline:
            print(f"File has been deleted: {event.src_path}") #Only prints the message is the file deleted was actually in the baseline
        try:
            save_detection_alert(event.src_path, "Deleted")
        except OSError as e:
            print(f"Could not save the alert for {file_path}: {e}")

        try:
            send_alert(os.path.basename(file_path), "Deleted")
        except Exception as e: #This broader except Exception is there because failure could be because of anuthing since it's calling a third-party library, winotify
            print(f"Could not send the notification for {file_path}: {e}")
        
        self.last_known_hash.pop(event.src_path, None) #Removes the file from the hash tracker since it no longer exists

    def on_moved(self, event):
        #This will fire an alert when a file has been renamed or moved to a different location
        if event.is_directory:
            return
        if self.should_ignore(event.src_path):
            return
        if self.is_target_file(event.src_path):
            return
        
        #These capture both the original and new location of the file 
        old_path = event.src_path
        new_path = event.dest_path

        try:
            new_hash = generate_hash(new_path) #Hashes the file at its new location
            baseline_hash = self.baseline.get(os.path.normpath(old_path)) #Fetches the original baseline hash of that file using its old file path

            #Here alerts are saved either way but the difference is between whether the file was just moved or if its content was also changed
            if new_hash != baseline_hash:
                print(f"File was moved and content was changed: {old_path} -> {new_path}")
                
                try:
                    save_detection_alert(old_path, "Renamed/Moved & Content Changed", dest_path=new_path)
                except OSError as e:
                    print(f"Could not save the alert for {old_path}: {e}")

                try:
                    send_alert(os.path.basename(new_path), "Renamed/Moved & Content Changed")
                except Exception as e:
                    print(f"Could not send the notification for {new_path}: {e}")
            else:
                print(f"File was moved but content is unchanged: {old_path} → {new_path}")
                
                try:
                    save_detection_alert(old_path, "Renamed/Moved & Content Unchanged", dest_path=new_path)
                except OSError as e:
                    print(f"Could not save the alert for {old_path}: {e}")

                try:    
                    send_alert(os.path.basename(new_path), "Renamed/Moved & Content Unchanged")
                except Exception as e:
                    print(f"Could not send the notification for {new_path}: {e}")

            #Updates the hash tracker and removes the old path entry by replacing it with the new one
            self.last_known_hash.pop(old_path, None)
            self.last_known_hash[new_path] = new_hash
        
        except (FileNotFoundError, PermissionError) as e:
            print(f"Could not hash moved file: {new_path} - {e}")
    

if __name__ == "__main__":

    #This will load the monitored file path that was saved by baseline.py
    monitored_file_path = load_monitored_file_path()

    
    if not monitored_file_path:
        print("Please run baseline.py first to set up file monitoring")
    else:
        print(f"Monitoring: {monitored_file_path}")

        #This will load and decrypt the baseline hash from baseline.json
        baseline = load_decrypted_baseline()

        #This will set up the watchdog event handler and observer
        event_handler = MyFIMEventHandler(baseline, monitored_file_path)
        observer = Observer()

        #If a user selects a single file, watch its parent folder instead
        if os.path.isfile(monitored_file_path):
            watch_path = os.path.dirname(monitored_file_path)
        else:
            watch_path = monitored_file_path
        observer.schedule(event_handler, watch_path, recursive=True) #This tells the observer to watch watch_path, use event_handler for file events and check subfolders too

        #This will start the observer, tha background watching thread
        observer.start()
        print("Watchdog is now active and running. Monitoring for changes...")
        print("Press Ctrl+C to stop monitoring\n")

        #This will keep running watchdog until the user stops it with Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nFile Monitoring has been stopped")

        observer.join() #Waits for the observer thread to fully finish before the program exits 