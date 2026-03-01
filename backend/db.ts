import { createClient, SupabaseClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

// Make sure these environment variables exist in your backend deployment
const SUPABASE_URL = process.env.SUPABASE_URL!;
const SUPABASE_KEY = process.env.SUPABASE_KEY!;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  throw new Error('Supabase URL or Key is missing. Check your .env file!');
}

// Export a reusable Supabase client
export const supabase: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);