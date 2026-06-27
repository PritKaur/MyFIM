# MyFIM: File Integrity Monitoring Tool

This tool is designed to be simple, free, and lightweight for small businesses with limited budgets and/or a lack of dedicated IT staff. The tool monitors files or folders that are selected by the user of the tool. It creates an initial hash of the selected file or folder and compares current file hashes against it to see if the file has changed in any way and informs the user of any changes to files that have been detected through Windows desktop notifications and also provides a web-based dashboard for the user to view more details about the file change alert. 

The tool uses several tools and technologies, including Python and Windows OS, because it's required for the desktop notifications part of the tool. The requirements.txt file includes some of the Python libraries and packages that would need to be present for the tool to function properly. 

The launcher of the tool is the start_fim.bat file, which is there to allow users of the tool to start the tool by simply double-clicking on the file instead of manually running the different Python scripts that make up the tool in different terminals. The .bat file runs the scripts in a certain order and will open the baseline tool first to select files or folders to monitor, start the dashboard, and the main file monitoring engine. 

In terms of security, access to the dashboard requires the user to enter valid login credentials which for the purpose of the demonstration of this semester project are currently hardcoded in the script. Secret.key is also an encryption key being used to encrypt the baseline storage and it must be deleted alone without deleting baseline.json too because they work together. If one is deleted and the other is not, then decryption will bring errors. 
