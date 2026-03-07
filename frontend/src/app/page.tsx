'use client';

import { useState } from 'react';

const LANGUAGES = [
  'Spanish', 'French', 'German', 'Italian', 'Portuguese',
  'Japanese', 'Mandarin', 'Korean', 'Arabic', 'Hindi',
];

export default function Home() {
  const [phone, setPhone] = useState('');
  const [language, setLanguage] = useState(LANGUAGES[0]);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg('');

    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phoneNumber: phone, language }),
    });

    if (res.ok) {
      setStatus('success');
    } else {
      const data = await res.json();
      setErrorMsg(data.error ?? 'Something went wrong.');
      setStatus('error');
    }
  }

  if (status === 'success') {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black px-6">
        <div className="max-w-sm w-full text-center space-y-4">
          <div className="text-4xl">🎉</div>
          <h1 className="text-2xl font-semibold text-black dark:text-white">You're in!</h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            WhatsApp <span className="font-medium text-black dark:text-white">{process.env.NEXT_PUBLIC_WHATSAPP_NUMBER}</span> to start learning {language}.
          </p>
          <p className="text-sm text-zinc-400">We'll also send you a word of the day to keep you sharp.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black px-6">
      <div className="max-w-sm w-full space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-black dark:text-white">
            Poly Pal
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400">
            Learn a language over WhatsApp. Enter your number and we'll message you.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label htmlFor="phone" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              WhatsApp number
            </label>
            <input
              id="phone"
              type="tel"
              required
              placeholder="+1 555 000 0000"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              className="w-full rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 py-2.5 text-black dark:text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white"
            />
            <p className="text-xs text-zinc-400">Include country code, e.g. +44 7700 900000</p>
          </div>

          <div className="space-y-1">
            <label htmlFor="language" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Language to learn
            </label>
            <select
              id="language"
              value={language}
              onChange={e => setLanguage(e.target.value)}
              className="w-full rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 py-2.5 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white"
            >
              {LANGUAGES.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>

          {status === 'error' && (
            <p className="text-sm text-red-500">{errorMsg}</p>
          )}

          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full rounded-lg bg-black dark:bg-white text-white dark:text-black font-medium py-2.5 hover:bg-zinc-800 dark:hover:bg-zinc-100 disabled:opacity-50 transition-colors"
          >
            {status === 'loading' ? 'Signing up…' : 'Start learning'}
          </button>
        </form>
      </div>
    </main>
  );
}
