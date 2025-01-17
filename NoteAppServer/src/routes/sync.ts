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
  limits: { fileSize: 1000000 }, // 1MB file size limit
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

// Upload a file
router.post("/upload", upload.single("file"), (req: Request, res: Response) => {
    console.log("File received");
    console.log(req.file);
    console.log(req.body);
    res.status(201).json({ message: "file uploaded successfully" });
  }
);

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
/*
{
  filename: 'hello.txt',
  inode: 39969446693098504,
  crc32: 388595853,
  size: 14,
  mtime: 1737052590.321867,
  ctime: 1737052580.8427987,
  state: 'active'
}
*/

type metadata = {
  filename: string,
  inode: number,
  crc32: number,
  size: number,
  mtime: number,
  ctime: number,
  state: string
};

router.post("/compare_metadata", async (req: Request, res: Response) => {
  const clientMetadata: metadata[] = req.body;
  console.log(clientMetadata);

  const serverMetadataPath = path.join("metadata/", "server_metadata.json");

  // Check if the server metadata file exists
  let serverMetadata: metadata[] = [];

  fs.readFile(serverMetadataPath, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
    } else {
      serverMetadata = JSON.parse(data);
      console.log(data);
    }
  });
  
  // Compare local and server metadata
  const toUpload: string[] = [];
  const toDownload: string[] = [];
  const unchanged: string[] = [];

  clientMetadata.map((cli_itm) => {
    console.log(cli_itm.filename);
    const ser_itm: metadata | undefined = serverMetadata.find(itm => itm.filename === cli_itm.filename);
    console.log(ser_itm);
    if (!ser_itm) {
      toUpload.push(cli_itm.filename);
    } else if (cli_itm.crc32 !== ser_itm.crc32) {
      if (cli_itm.mtime > ser_itm.crc32) {
        toUpload.push(cli_itm.filename);
      } else {
        toDownload.push(cli_itm.filename);
      }
    } else {
      unchanged.push(cli_itm.filename);
    }
  });

  serverMetadata.map((ser_itm) => {
    console.log(ser_itm.filename);
    const cli_itm: metadata | undefined = clientMetadata.find(itm => itm.filename === ser_itm.filename);
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

/*
// create a catch-all middleware that handles unhandled errors.
router.use((err: Error, req: Request, res: Response) => {
  if (err instanceof multer.MulterError) {
    console.log("Multer error occurred: ", err.stack);
    res.status(400).json({ message: "file upload error occurred" });
  }
  console.log("Unexpected error occurred: ", err.stack);
  res.status(500).json({ error: true, message: "Something went wrong" });
});
*/

export default router;
