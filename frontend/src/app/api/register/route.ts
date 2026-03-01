import { NextRequest, NextResponse } from 'next/server';
import supabase from '@/lib/db';

export async function POST(req: NextRequest) {
  const { phoneNumber, language } = await req.json();

  const { data, error } = await supabase
    .from('users')
    .insert([{ phone: phoneNumber, language }]);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ message: 'User registered', data });
}