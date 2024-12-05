import requests
import os
import json

print("Starting...")

server_url = "http://localhost:3000/sync/"

# Upload file
def upload(file):
  res = requests.post(server_url + "upload", files=file, timeout=2)
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
def uploadFolder():
  folder_path = 'path/to/your/folder'

  # Iterate through all files in the folder
  for filename in os.listdir():
    # Build the full file path
    # file_path = os.path.join(folder_path, filename)
    file_path =  filename
  
    # Check if it's a file (not a folder)
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

getFileList()
#uploadFolder()

print("Done")

