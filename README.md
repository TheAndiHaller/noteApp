# NoteApp

## Brainstorming
Notes are simple .md .txt .cvs files that can be edited with any text editor.

1. Nodejs server / API to sync files across clients.
2. Database or file container? Google drive shared folder? to store the notes / files online.
3. Python scipt to sync the notes / files with the server. 
4. React-Native App to sync and edit the notes.
5. SQLite to store metadata (timestamps, path)


## Workflow:




# Roadmap
## Version 0.3.0
- Server
- [ ] Detect file changes
- [ ] Keep track of files / dates

- Client
- [ ] Detect file changes
- [ ] Keep track of files / dates
- [ ] Config file (server URL, folder path, user)
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
