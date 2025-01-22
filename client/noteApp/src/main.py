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
def download(fileName, folder_path):
  try:
    res = requests.get(server_url + "download", params={"file" : fileName}, timeout=10)
    res.raise_for_status() 

    # ToDo: except if no metadata 
    file_metadata = res.headers.get("X-File-Metadata")
    file_metadata_json = json.loads(file_metadata)
    if file_metadata_json:
      print("File Metadata:", file_metadata_json)
      # get local metadata file
      metadata = getLocalMetadataFile()
      filename = file_metadata_json["filename"] 
      file_found = next((file for file in metadata['files'] if file['filename'] == filename), None)
      if file_found:
        print(f"{filename} has been modified.")
        file_found["crc32"] = file_metadata_json["crc32"] 
        file_found["mtime"] = file_metadata_json["mtime"]
        file_found["state"] = file_metadata_json["state"]
      else:
        # Add the new name to the array
        data = {
          "filename": filename, 
          "crc32": file_metadata_json["crc32"], 
          "mtime": file_metadata_json["mtime"],
          "state": file_metadata_json["state"]
          }
        metadata['files'].append(data)
        print(f"Added {filename} with  {data}")
      saveLocalMetadataFile(metadata)

    file_path = os.path.join(folder_path, fileName)
    with open(file_path, "w", encoding="utf-8") as file:
      print(res.text)
      file.write(res.text)
    print("File downloaded and saved successfully.")
  except requests.exceptions.RequestException as e:
    print(f"Failed to download the file: {e}")
  except Exception as e:
    print(f"An error occurred: {e}")

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
    return str(zlib.crc32(data))

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
          stat = os.stat(file_path)
          print(f"File {filename} Modi: {stat.st_mtime}")

          file_found = next((file for file in metadata['files'] if file['filename'] == filename), None)
          if file_found:
            # Check if the file has been modified
            if file_found['crc32'] != checksum:
                print(f"{filename} has been modified.")
                file_found["crc32"] =  checksum
                file_found["mtime"] =  stat.st_mtime
                file_found["state"] =  "active"
            else:
                print(f"{filename} is up-to-date.")
          else:
            # Add the new name to the array
            data = {
              "filename": filename, 
              "crc32": checksum, 
              "mtime": stat.st_mtime,
              "state": "active"
              }
            metadata['files'].append(data)
            print(f"Added {filename} with  {data}")
  
  saveLocalMetadataFile(metadata)
  server_data = sendMetadata(metadata['files'])
  toUpload = server_data['toUpload']
  toDownload = server_data['toDownload']
  unchanged = server_data['unchanged']
  print("Files to upload: ")
  print(toUpload)
  for filename in toUpload:
    file_path = os.path.join(folder_path, filename)
    file_metadata = next((file for file in metadata['files'] if file['filename'] == filename))
    with open(file_path, 'r') as file:
       upload({"file" : file}, file_metadata)

  print("Files to download: ")
  print(toDownload)
  for filename in toDownload:
    download(filename, folder_path)

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

  else:
    print("Command: " + sys.argv[1] + " not recognized. --help")  
    sys.exit(1)