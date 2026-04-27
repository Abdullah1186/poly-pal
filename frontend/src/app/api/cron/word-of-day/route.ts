
import { NextResponse } from 'next/server';

export async function GET() {
  // First request wakes Railway up — may timeout, that's fine
  try {
    await fetch(`${process.env.RAILWAY_BACKEND_URL}/cron/word-of-day`, {
      method: 'POST',
      headers: { 'x-cron-secret': process.env.CRON_SECRET! },
      signal: AbortSignal.timeout(10_000), // 10s wake-up attempt
    });
  } catch {
    // Likely just sleeping — wait and retry
    await new Promise(r => setTimeout(r, 15_000));
    const res = await fetch(`${process.env.RAILWAY_BACKEND_URL}/cron/word-of-day`, {
      method: 'POST',
      headers: { 'x-cron-secret': process.env.CRON_SECRET! },
      signal: AbortSignal.timeout(30_000),
    });
    if (!res.ok) return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
