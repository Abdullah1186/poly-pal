import { NextResponse } from 'next/server';

// Called by Vercel Cron — proxies to the Railway agent backend
export async function GET() {
  const res = await fetch(`${process.env.RAILWAY_BACKEND_URL}/cron/word-of-day`, {
    method: 'POST',
    headers: { 'x-cron-secret': process.env.CRON_SECRET! },
  });

  if (!res.ok) {
    return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
