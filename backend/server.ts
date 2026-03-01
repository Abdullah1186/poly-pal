import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { handleWhatsAppMessage } from './whatsapp';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.post('/webhook', handleWhatsAppMessage);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));