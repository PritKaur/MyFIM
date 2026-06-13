import hashlib #Python's built-in hashing library

#This function generates the hash for 1 file, reads that file in chunks and returns the hash as a hex string
def generate_hash(file_path): #The file path is for the file you want to hash and monitor
    sha256 = hashlib.sha256()  #This is the hash calculator

    #This block is saying: open file, feed into calculator in small chunks and return fingerprint    
    with open(file_path,  'rb') as f: #Read-binary mode allows the monitoring of any file type, image, pdf, etc because python reads raw bytes
        while chunk := f.read(8192): #Chunks prevent the tool from crashing when monitoring huge files 
            sha256.update(chunk)

    return sha256.hexdigest() #the hash is returned as a readable 64-character hexadecimal string

#TEST BLOCK - This will only run when I run this file directly, not when it's later imported by another script
if __name__ == "__main__":
    import os #OS is only imported here because it's only needed for this testing part

    test_file = "test.txt"

    #Creating the test file
    with open(test_file, 'w') as f:
        f.write("Hello, this is my test file")

    #Hashing the test file
    hash1 = generate_hash(test_file)
    print(f"Original hash: {hash1}")

    #Modifying the file
    with open(test_file, 'a') as f:
        f.write("A small change")

    #Hashing the file again
    hash2 = generate_hash(test_file)
    print(f"New hash: {hash2}")

    if hash1 ==  hash2:
        print("Hashes are the same, file was not changed")
    else:
        print("Hashes are different, file was changed")

    #Clean up the test file
    os.remove(test_file)