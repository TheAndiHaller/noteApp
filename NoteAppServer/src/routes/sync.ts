import { Router, Request, Response, NextFunction } from "express";
import multer from "multer";

const router = Router();
const uploader = multer({ dest: 'uploads/'});

// Upload a file
router.post('/upload', uploader.single('file'), (req: Request, res: Response, next: NextFunction) => {
  console.log("File received");
  console.log(req.file)
  res.status(201).json({ message: 'file uploaded successfully'});
})

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