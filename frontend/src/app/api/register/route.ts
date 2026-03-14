import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Use service role key server-side — never exposed to the browser
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(req: NextRequest) {
  const { phoneNumber, language } = await req.json();

  // Normalise to match Meta's format: digits only, no +, spaces, or dashes
  const phone = phoneNumber.replace(/^\+/, '').replace(/[\s\-]/g, '');

  const { data, error } = await supabase
    .from('users')
    .insert([{ phone, language }]);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ message: 'User registered', data });
}
