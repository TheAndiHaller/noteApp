# built-in library's
import sys
import os
import zlib
import json
from pathlib import Path
from datetime import datetime

#sys.path.append("libs")
import requests
# import watchdog # for monitoring changes in folder

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE_PATH = os.path.join(SCRIPT_DIR, 'local_metadata.json')
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, 'config.json')

server_url = "http://localhost:3000/sync/"

# Upload file
def upload(file, metadata):
  res = requests.post(server_url + "upload", files=file, data=metadata, timeout=2)
  print(res.text)

# Download file
def download(fileName):
  try:
    res = requests.get(server_url + "download", params={"file" : fileName})
    res.raise_for_status() 

    with open(fileName, "w", encoding="utf-8") as file:
      print(res.text)
      file.write(res.text)
    print("File downloaded and saved successfully.")
  except requests.exceptions.RequestException as e:
    print(f"Failed to download the file: {e}")
  except Exception as e:
    print(f"An error occurred: {e}")

# Upload all files in folder
def uploadFolder(folder_path):
  for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    #file_path = filename
    if os.path.isfile(file_path):
      if file_path.endswith(".txt") or file_path.endswith(".md") or file_path.endswith('.csv'):
        with open(file_path, 'r') as file:
          print(f"Sending {filename}...")
          upload({"file" : file})
          print('-' * 40)

# Download all files from folder
def downloadFiles(fileList):
  for fileName in fileList:
    download(fileName)

# get list of files
def getFileList():
  res = requests.get(server_url + "getfiles")
  data = res.json()
  fileList = data["files"]
  print(fileList)
  downloadFiles(fileList)

# Calculate the CRC32 to detect changes in files
def calculate_crc32(data: bytes) -> int:
    return zlib.crc32(data)

# Send metadata to server for comparation
def sendMetadata(metadata):
  try:
    res = requests.post(
        url = server_url + "compare_metadata",
        json=metadata,
        timeout=10
      )
    res.raise_for_status()
    print(res.json())
    return res.json()
  except requests.exceptions.RequestException as e:
     print(f"Error sending metadata to server: {e}")
     return {"error": str(e)}
   
# Upload list of files
#def uploadFileList(files):
   


# Synchronises the local folder with the server
def syncFolder(folder_path):
  print("syncing...")
  # get local metadata file
  metadata = getLocalMetadataFile()
  # Iterate through all files in the folder
  for filename in os.listdir(folder_path):
    # Build the full file path
    file_path = os.path.join(folder_path, filename)
    # Check if it's a file (not a folder)
    if os.path.isfile(file_path):
      if file_path.endswith(".txt") or file_path.endswith(".md") or file_path.endswith('.csv'):
        with open(file_path, 'rb') as file:
          file_data = file.read()
          checksum = calculate_crc32(file_data)
          print(f"File {filename} Checksum: {checksum}")
          stat = os.stat(file_path)

          file_found = next((file for file in metadata['files'] if file['filename'] == filename), None)
          if file_found:
              # Check if the file has been modified
              if file_found['crc32'] != checksum:
                  print(f"{filename} has been modified.")
                  file_found['crc32'] = checksum
              else:
                  print(f"{filename} is up-to-date.")
          else:
              # Add the new name to the array
              data = {
                "filename": filename, 
                "inode": stat.st_ino,
                "crc32": checksum, 
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "ctime": stat.st_birthtime,
                "state": "active"
                }
              metadata['files'].append(data)
              print(f"Added {filename} with  {data}")
  
  saveLocalMetadataFile(metadata)
  server_data = sendMetadata(metadata['files'])
  toUpload = server_data['toUpload']
  toDownload = server_data['toDownload']
  unchanged = server_data['unchanged']
  print(toUpload)
  for filename in toUpload:
    file_path = os.path.join(folder_path, filename)
    file_metadata = next((file for file in metadata['files'] if file['filename'] == filename))
    with open(file_path, 'r') as file:
       upload({"file" : file}, file_metadata)


def loadConfig():
  try:
        # Try to open the file in read mode and load its contents
    with open(CONFIG_FILE_PATH, 'r') as file:
      return json.load(file)
  except FileNotFoundError:
        # If the file does not exist, create it and initialize with default content
    print("No config file, creating.")  # for now, just create the hardcoded file, later promt user
    default_content = {"folderToTrack": "C:/Users/andi_/OneDrive/Documentos/noteApp"}
    with open(CONFIG_FILE_PATH, 'w') as file:
      json.dump(default_content, file)  # Write the default content as JSON
      return default_content  # Return the default content

# Get the folder to track
def get_folder_to_track():
    config = loadConfig()
    return Path(config.get("folderToTrack", "."))  # Default to current directory

# Load metadata file
def getLocalMetadataFile():
    try:
        # Try to open the file in read mode and load its contents
        with open(METADATA_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, create it and initialize with default content
        print("No metadata file, creating.")
        default_content = {"files": []}
        with open(METADATA_FILE_PATH, 'w') as file:
            json.dump(default_content, file)  # Write the default content as JSON
        return default_content  # Return the default content

# Save metadata file
def saveLocalMetadataFile(metadata):
  with open(METADATA_FILE_PATH, 'w') as file:
    json.dump(metadata, file)


if __name__ == "__main__":
  folder_path = get_folder_to_track()
  print(f"Tracking folder: {folder_path}")
  
  if len(sys.argv) != 2:
      print("Error: you must provide an argument. --help")
      sys.exit(1)
  
  elif sys.argv[1] == "--help":
    print("NoteApp 0.2.0. To sync folder --sync")
    sys.exit(1)
  
  elif sys.argv[1] == "--sync":
    syncFolder(folder_path)
    sys.exit(1)
  
  elif sys.argv[1] == "--folder":
    uploadFolder(folder_path)
    sys.exit(1)

  else:
    print("Command: " + sys.argv[1] + " not recognized. --help")  
    sys.exit(1)