# NoteApp

## Brainstorming
Notes are simple .md .txt .cvs files that can be edited with any text editor.

1. Nodejs server / API to sync files across clients.
2. Database or file container? Google drive shared folder? to store the notes / files online.
3. Python scipt to sync the notes / files with the server. 
4. React-Native App to sync and edit the notes.
5. SQLite to store metadata (timestamps, path)


# Roadmap

## Version 0.5
### ToDo:
- Server
- [x] Create repo
- [x] Create node server
- [ ] Install dependencies (Ts, express, nodemon, dotenv, multer, sqlite3, zod)
- [ ] API endpoint to recive file
- [ ] Save file to filesystem
- [ ] Endpoint to ask to send files to client
  
- Client
- [ ] Python CLI tool to send file to server
- [ ] Command to ask to download files from server
