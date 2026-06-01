import hashlib

#This function generates the hash for 1 file, reads that file in chunks and returns the hash as a hex string
def generate_hash(file_path):
    sha256 = hashlib.sha256()  #This is the hash calculator

    #This block is saying: open file, feed into calculator in small chunks and return fingerprint    
    with open(file_path,  'rb') as f: 
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()

#TEST BLOCK - This will only run when I run this file directly, not when it's later imported by another script
if __name__ == "__main__":
    import os

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