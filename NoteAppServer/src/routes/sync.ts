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
