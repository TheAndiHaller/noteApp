import { Router, Request, Response, NextFunction } from "express";
import multer from "multer";
import fs from "node:fs";
import path from "path";

const dirname: string = "uploads/";
const router = Router();
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, dirname);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
    //cb(null, Date.now() + '-' + file.originalname);
  },
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10000000 }, // 10MB file size limit
  fileFilter: (req, file, cb) => {
    if (
      file.mimetype === "text/plain" ||
      file.mimetype === "text/markdown" ||
      file.mimetype === "text/csv"
    ) {
      cb(null, true);
    } else {
      cb(new Error("Invalid file type"));
    }
  },
});

// Type for metadata
type Metadata = {
  filename: string,
  crc32: string,
  mtime: number,
  state: string
};

function parseMetadata(data: any): Metadata {
  return {
    filename: String(data.filename), // Ensure it's a string
    crc32: String(data.crc32),       // Ensure it's a string
    mtime: Number(data.mtime),       // Convert to number
    state: String(data.state),       // Ensure it's a string
  };
}

// Upload a file
router.post("/upload", upload.single("file"), (req: Request, res: Response) => {
    console.log("File received");

    const clientMetadata: Metadata = parseMetadata(req.body);
    const serverMetadataPath = path.join("metadata/", "server_metadata.json");

    let serverMetadata: Metadata[] = [];

    try {
      const data = fs.readFileSync(serverMetadataPath, 'utf8');
      serverMetadata = JSON.parse(data);
      console.log("serverMetadata");
      console.log(serverMetadata);
    } catch (err) {
      console.error(err);
    }

    const index = serverMetadata.findIndex(
      (ser_itm) => clientMetadata.filename === ser_itm.filename
    );
    
    if (index !== -1) {
      serverMetadata[index] = parseMetadata(clientMetadata); // Update the existing item
      console.log("File exists, updating");
    } else {
      console.log("File does not exist, adding new entry");
      serverMetadata.push(clientMetadata); // Add the new item
    }
   
    console.log("serverMetadata:");
    console.log(serverMetadata);

    const content = JSON.stringify(serverMetadata);

    try {
      fs.writeFileSync(serverMetadataPath, content);
      // file written successfully
      console.log("file written successfully");
    } catch (err) {
      console.error(err);
    }

    res.status(201).json({ message: "file uploaded successfully" });
});

// Download a file
router.get("/download", (req: Request, res: Response) => {
  const fileName: string = req.query.file as string;

  if (!fileName) {
    res.status(400).send("File name is required");
  }

  const file = path.join(dirname, fileName); 
  console.log(`Serving file: ${file}`);

  res.download(file, (err) => {
    if (err) {
      console.error(`Error sending file: ${err}`);
      res.status(500).send("Failed to download the file");
    }
  });
});

// Download folder
router.get("/getfiles", (req: Request, res: Response) => {
  const files: string[] = fs.readdirSync(dirname);
  const filesJson = {"files": files};
  console.log(filesJson);

  res.status(200).json(filesJson);
});


router.post("/compare_metadata", async (req: Request, res: Response) => {
  console.log("Client Metadata: ");
  const clientMetadata: Metadata[] = req.body;
  console.log(clientMetadata);

  const serverMetadataPath = path.join("metadata/", "server_metadata.json");

  // Check if the server metadata file exists
  let serverMetadata: Metadata[] = [];

  try {
    const data = fs.readFileSync(serverMetadataPath, 'utf8');
    serverMetadata = JSON.parse(data);
    console.log("Server Metadata: ");
    console.log(serverMetadata);
  } catch (err) {
    console.error(err);
  }
  
  // Compare local and server metadata
  const toUpload: string[] = [];
  const toDownload: string[] = [];
  const unchanged: string[] = [];

  clientMetadata.map((cli_itm) => {
    console.log(cli_itm.filename);
    const ser_itm: Metadata | undefined = serverMetadata.find(itm => itm.filename === cli_itm.filename);
    console.log(ser_itm);
    if (!ser_itm) {
      console.log("Not on server, to uploads");
      toUpload.push(cli_itm.filename);
    } else if (cli_itm.crc32 !== ser_itm.crc32) {
      console.log("cli CRC: " + cli_itm.crc32 + " - ser CRC: " + ser_itm.crc32);
      console.log("cli mod: " + cli_itm.mtime + " - ser mod: " + ser_itm.mtime);
      if (cli_itm.mtime > ser_itm.mtime) {
        console.log("On server, different, uploading");
        toUpload.push(cli_itm.filename);
      } else {
        console.log("On server, different, downloading");
        toDownload.push(cli_itm.filename);
      }
    } else {
      console.log("File on server, unchanged");
      unchanged.push(cli_itm.filename);
    }
  });

  serverMetadata.map((ser_itm) => {
    console.log(ser_itm.filename);
    const cli_itm: Metadata | undefined = clientMetadata.find(itm => itm.filename === ser_itm.filename);
    console.log(cli_itm);
    if (!cli_itm) {
      toDownload.push(ser_itm.filename);
    } 
  });

  console.log(toUpload);
  console.log(toDownload);
  console.log(unchanged);

  res.status(200).json({toUpload, toDownload, unchanged});
});

export default router;
