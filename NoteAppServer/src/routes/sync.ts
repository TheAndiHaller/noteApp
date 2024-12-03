import { Router, Request, Response, NextFunction } from "express";
import multer from "multer";

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
    if (file.mimetype === "text/plain" || file.mimetype === "text/markdown" || file.mimetype === 'text/csv') {
      cb(null, true);
    } else {
      cb(new Error("Invalid file type"));
    }
  }
});

// Upload a file
router.post('/upload', upload.single("file"), (req: Request, res: Response, next: NextFunction) => {
  console.log("File received");
  console.log(req.file)
  res.status(201).json({ message: "file uploaded successfully"});
});

// Download a file
router.get("/download", (req: Request, res: Response) => {
  console.log("Sending file");
  const file = `${dirname}test.txt`;
  res.download(file);
});


/*
// create a catch-all middleware that handles unhandled errors.
router.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if(err instanceof multer.MulterError) {
      console.log('Multer error occurred: ', err.stack);

      return res.status(400).json({ message: 'file upload error occurred'});
  }

  console.log('Unexpected error occurred: ', err.stack);

  return res.status(500).json({ error: true, message: 'Something went wrong'});

});
*/

export default router;