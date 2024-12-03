import requests

print("Starting...")

server_url = "http://localhost:3000/sync/"
myfiles = {'file': open('test.txt' ,'rb')}

res = requests.post(server_url + "upload", files=myfiles, timeout=2)

print(res.text)

print("Done")