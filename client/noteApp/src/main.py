import requests

print("Starting...")

server_url = "http://localhost:3000/sync/"
myfiles = {"file": open(r"test.txt" ,"r")}
#myfiles = {"file": open(r"notes.md" ,"r")}

# Upload file
def upload():
  res = requests.post(server_url + "upload", files=myfiles, timeout=2)
  print(res.text)

# Download file
def download():
  try:
    res = requests.get(server_url + "download")
    res.raise_for_status() 

    with open("test.txt", "w", encoding="utf-8") as file:
      print(res.text)
      file.write(res.text)
    print("File downloaded and saved successfully.")
  except requests.exceptions.RequestException as e:
    print(f"Failed to download the file: {e}")
  except Exception as e:
    print(f"An error occurred: {e}")

download()

print("Done")