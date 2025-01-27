# built-in library's
import sys
import os
import zlib
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

#sys.path.append("libs")
import requests
# import watchdog # for monitoring changes in folder

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE_PATH = os.path.join(SCRIPT_DIR, 'local_metadata.json')
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, 'config.json')
VERSION = "V0.4.0"

class Config:
  def __init__(self):
    self.serverURL = "http://localhost:3000/sync/"
    self.folderPath = None
    # Load configuration file
    self.loadConfigFile() 

  def loadConfigFile(self):
    """Load configuration from the config file."""
    try:
      with open(CONFIG_FILE_PATH, 'r') as file:
        config = json.load(file)
        self.serverURL = config.get("serverURL", self.serverURL)
        folder_to_track = config.get("folderToTrack")
        if folder_to_track:
          self.folderPath = Path(folder_to_track)    
    except FileNotFoundError:
      print(f"Config file not found. A new one will be created at {CONFIG_FILE_PATH}.")
    except json.JSONDecodeError:
      print(f"Error decoding JSON in config file: {CONFIG_FILE_PATH}. Reinitializing defaults.")

  def saveConfig(self):
   """Save the current configuration to the config file."""
   config = {
       "serverURL": self.serverURL,
       "folderToTrack": str(self.folderPath) if self.folderPath else None
   }
   try:
       with open(CONFIG_FILE_PATH, 'w') as file:
           json.dump(config, file, indent=4)  # Use `indent=4` for readability.
   except Exception as e:
       print(f"Error saving config file: {e}")

  def setFolderPath(self, folderPath):
    """Set the folder path and save the configuration."""
    self.folderPath = Path(folderPath)
    self.saveConfig()

  def setServerURL(self, serverURL):
       """Set the server URL and save the configuration."""
       self.serverURL = serverURL
       self.saveConfig()

config = Config()


@dataclass
class Metadata:
  filename: str
  crc32: str
  mtime: float
  state: str = "active"

  # Just as an example
  def is_modified(self, new_crc32: str) -> bool:
    return self.crc32 != new_crc32

class MetadataFile:
  def __init__(self, path):
    self.path: str = path
    self.content = {"files": []}
    self.load()

  def load(self):
    """Load metadata file from file system"""
    try:
      with open(self.path, 'r') as file:
        self.content = json.load(file)
    except FileNotFoundError:
      print("Metadata file not found. Initializing a new one.")
      self.save()
    except json.JSONDecodeError:
      print("Error decoding metadata file. Resetting to default.")
      self.content = {"files": []}
      self.save()

  def save(self):
    """Save metadata file to file system"""
    try:
      with open(self.path, 'w') as file:
        json.dump(self.content, file, indent=4)
    except IOError as e:
      print("Error writing file")

  def getFileMetadata(self, filename):
    """Search for filename in metadata"""
    file_metadata = next((file for file in self.content["files"] if file["filename"] == filename), None)
    if file_metadata:
      return Metadata(**file_metadata)
    return None

  def updateFileMetadata(self, metadata: Metadata):
    """Find the file in metadata and update it, or add it if it doesn't exist"""
    file_found = next((file for file in self.content["files"] if file["filename"] == metadata.filename), None)
    if file_found:
      file_found.update(metadata.__dict__)
    else:
      self.content["files"].append(metadata.__dict__)
  
  def removeFileMetadata(self, filename):
    """Remove file metadata"""
    self.content["files"] = [file for file in self.content["files"] if file["filename"] != filename]

  def verifyMetadata(self, metadata: Metadata):
    """Find the file in metadata and update it if changed, or add it if it doesn't exist"""
    file_found = next((file for file in self.content["files"] if file["filename"] == metadata.filename), None)
    if file_found:
      if file_found["crc32"] != metadata.crc32:
        print("File found: Updating")
        file_found.update(metadata.__dict__)
      else:
        print("File found: Up to date")
    else:
      print("New file: Adding")
      self.content["files"].append(metadata.__dict__)
    self.save()

metadataFile = MetadataFile(METADATA_FILE_PATH)

# Upload file
def upload(file, metadata):
  res = requests.post(config.serverURL + "upload", files=file, data=metadata, timeout=2)
  print(res.text)

# Download file
def download(fileName, folder_path):
  try:
    res = requests.get(config.serverURL + "download", params={"file" : fileName}, timeout=10)
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
  res = requests.get(config.serverURL + "getfiles")
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
        url = config.serverURL + "compare_metadata",
        json=metadata,
        timeout=10
      )
    res.raise_for_status()
    print(res.json())
    return res.json()
  except requests.exceptions.RequestException as e:
     print(f"Error sending metadata to server: {e}")
     return {"error": str(e)}
   
# Helper: Check if a file is valid for synchronization
def isValidFile(file_path):
  valid_extensions = [".txt", ".md", ".csv"]
  return os.path.isfile(file_path) and any(file_path.endswith(ext) for ext in valid_extensions)

# Helper: Calculate CRC32 and get modification time
def getFileInfo(file_path):
  with open(file_path, 'rb') as file:
    file_data = file.read()
    checksum = calculate_crc32(file_data)
  mtime = os.stat(file_path).st_mtime
  return checksum, mtime

# Send metadata to server for comparation
def sendMetadata2(metadata):
  try:
    res = requests.post(
        url = config.serverURL + "compare_metadata",
        json=metadata,
        timeout=10
      )
    res.raise_for_status()
    data = res.json()
    print(data)
    return data["toUpload"], data["toDownload"]
  except requests.exceptions.RequestException as e:
     print(f"Error sending metadata to server: {e}")
     return None

# Upload files with metadata to server
def uploadFiles(files):
  print("Uploading files:")
  for filename in files:
    print(f"{filename} ...")
    file_path = os.path.join(folder_path, filename)
    file_metadata = next((file for file in metadataFile.content['files'] if file['filename'] == filename))
    with open(file_path, 'r') as file:
       uploadSingleFile({"file" : file}, file_metadata)

# Upload file
def uploadSingleFile(file, metadata):
  res = requests.post(config.serverURL + "upload", files=file, data=metadata, timeout=2)
  print(res.text)

# Download files with metadata from Server
def downloadFiles2(files):
  print("Downloading files:")

# Synchronises the local folder with the server
def syncFolderNew():
  # Check folder for files:
  for filename in os.listdir(config.folderPath):
    # when we find a file, we buid the path and verify if it is a valid file
    file_path = os.path.join(config.folderPath, filename)
    if isValidFile(file_path):
      # if valid, we get metadata
      checksum, mtime = getFileInfo(file_path)
      # with that we need to check if already tracking, if so, check if uptodate, if not tracked, add
      metadata = Metadata(filename, checksum, mtime)
      metadataFile.verifyMetadata(metadata)

  toUplaod, toDownload = sendMetadata2(metadataFile.content["files"])

  if toUplaod:
    uploadFiles(toUplaod)
  if toDownload:
    downloadFiles2(toDownload)

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
  folder_path = config.folderPath
  if folder_path is None:
    print("Error: No Tracking folder set!")
    print("Use command setFolder inside the desired folder.")
    sys.exit(1)
  
  print(f"Tracking folder: {folder_path}")
  
  if len(sys.argv) != 2:
      print("Error: you must provide an argument. help for more info")
      sys.exit(1)
  
  elif sys.argv[1] == "help":
    print(f"NoteApp {VERSION}. ")
    print(f"To set current folder use: setFolder")
    print(f"To sync folder use: sync")
    sys.exit(1)
  
  elif sys.argv[1] == "sync":
    syncFolder(folder_path)
    sys.exit(1)

  elif sys.argv[1] == "setFolder":
    cwd = os.getcwd()
    while True:
      user_input = input(f"Setting: {cwd} to sync. y/n ")
      if user_input == "y":
        config.setFolderPath(cwd)
        sys.exit(1)
      else:
        print("No changes made.")
        sys.exit(1)

  else:
    print("Command: " + sys.argv[1] + " not recognized. help")  
    sys.exit(1)