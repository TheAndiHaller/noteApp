import express, { NextFunction, Request, Response } from "express";
import routes from "./routes/index";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use('/', routes);

// Error catching endware.
app.use((err: Error, req: Request, res: Response, next: NextFunction) => { // eslint-disable-line no-unused-vars
  console.error(err.stack); // Log the error (for debugging)
  res.status(500).json({ message: err.message }); // Send a JSON error response
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
