import { Router, Request, Response } from "express";
import sync from "./sync";

const router = Router();

router.get("/", (req: Request, res: Response) => {
  res.send("Home");
});

router.use("/sync", sync);

export default router;
