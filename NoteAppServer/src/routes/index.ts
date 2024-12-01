import { Router, Request, Response } from "express";

const router = Router();

// Sample route
router.get("/", (req: Request, res: Response) => {
  res.send("Hello, World!");
});

router.get("/example", (req: Request, res: Response) => {
  res.send("This is an example route");
});

export default router;
