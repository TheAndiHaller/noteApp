# NoteApp
## Brainstorming
Notes are simple .md .txt .cvs files that can be edited with any text editor.

1. Nodejs server / API to sync files across clients.
2. Database or file container? Google drive shared folder? to store the notes / files online.
3. Python scipt to sync the notes / files with the server. 
4. React-Native App to sync and edit the notes.
5. SQLite to store metadata (timestamps, path)


File metadata
{
  "filename": "example.txt",
  "inode": "8718371873812718"
  "crc32": "0x12345678",
  "size": 1024,
  "mtime": "2025-01-16T12:00:00",
  "ctime": "2025-01-16T12:00:00",
  "state": "active | deleted | conflict"  
}


## Workflow:
1. Set folder to sync and user. Save to config file. 
2. --sync checks for files, if new, adds to the local file list with calculated CRC32, and timestamp
   If not new (already on list), check if CRC32 is same, if so, do nothing, else update CRC32 and timestamp
3. Send data to server, check for files on server.


## Install
### Windows
Create "noteapp.bat" file in "C:\Windows\System32" and add:

@echo off
python C:\path\to\main.py %*

Now, you can run:
noteapp --sync

## To install all the necesary libraries directly
pip install --target ./libs -r requirements.txt


# Roadmap
## Version 0.4.0
- Server
- [ ] Trash bin for deleted files.

- Client
- [ ] Recursive check for files in subfolders
- [ ] Implement file deletrion (Change status to deleted)


## Version 0.3.0
- Server
- [x] Route metadata_compare to check client metadata against server
- [x] Route to recive file + new metadata
- [x] Update server metadata file with new file data
- [x] Route to send files to client + metadata

- Client
- [x] Create and load config file 
- [x] Create metadata json for tracked files
- [x] Send local metadata to compare to server
- [x] Get instructions to upload or download files or leave them unchanged
- [x] Upload new or modified files
- [x] Download missing files or files that are newer on the server
- [x] Implement --setFolder to save current path as folder to sync
- [x] Add CLI commands with argparse or sys.argv
- [x] Integrate script to path


## Version 0.2.0
- Server
- [x] POST handle multiple files 
- [x] GET handle multiple files
- [x] Download al files from the folder

- Client
- [x] POST multiple files
- [x] GET multiple files
- [x] Send all files in folder
- [x] Test watchdog Module (for auto sync)
- [x] Implement CRC32 to verify if a file changed (for manual sync)

## Version 0.1.0
### ToDo:
- Server
- [x] Create repo
- [x] Create node server
- [x] Install dependencies (Ts, express, nodemon, dotenv, multer, sqlite3, zod)
- [x] API endpoint to receive file
- [x] Save file to filesystem
- [x] Endpoint to download files to client
  
- Client
- [x] Python CLI tool to send file to server
- [x] Function request GET to download files from server
