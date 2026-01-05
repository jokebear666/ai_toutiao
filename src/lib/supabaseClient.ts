import { createClient } from '@supabase/supabase-js';
import siteConfig from '@generated/docusaurus.config';

// Access customFields from the generated config
const customFields = siteConfig.customFields || {};
const supabaseUrl = (customFields.supabaseUrl as string) || '';
const supabaseKey = (customFields.supabaseAnonKey as string) || '';

// Create a single instance of the client
export const supabase = (supabaseUrl && supabaseKey) 
  ? createClient(supabaseUrl, supabaseKey) 
  : null;

// Helper to check if Supabase is configured
export const isSupabaseConfigured = () => {
    return !!supabase;
};
