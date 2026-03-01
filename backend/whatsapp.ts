import { Request, Response } from 'express';
import { Twilio } from 'twilio';
import { ChatOpenAI } from '@langchain/openai';
import { supabase } from './db';



const twilioClient = new Twilio(process.env.TWILIO_SID!, process.env.TWILIO_AUTH_TOKEN!);

export async function handleWhatsAppMessage(req: Request, res: Response) {
  try {
    const { From, Body } = req.body;

    // Load user memory
    const { data: user } = await supabase
      .from('users')
      .select('*')
      .eq('phone', From)
      .single();

    const chat = new ChatOpenAI({ model: 'gpt-4.1-mini' });

    const response = await chat.invoke([
      { role: 'system', content: `You are a friendly language tutor speaking in ${user.language}` },
      { role: 'user', content: Body }
    ]);

    // Save conversation summary
    await supabase
      .from('memory')
      .upsert({ phone: From, summary: response.content });

    // Reply to user via Twilio
    const messageBody = typeof response.content === 'string' 
      ? response.content 
      : response.content.map(block => 'text' in block ? block.text : '').join('');
    
    await twilioClient.messages.create({
      from: `whatsapp:${process.env.TWILIO_WHATSAPP_NUMBER}`,
      to: From,
      body: messageBody
    });

    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.sendStatus(500);
  }
}