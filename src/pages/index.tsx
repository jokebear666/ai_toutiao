import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Dashboard from '../components/Dashboard';
import { globalPaperCache, CACHE_TTL, setCachedData } from '../utils/paperCache';
import { supabase } from '../lib/supabaseClient';

// Prefetch logic
const prefetchDailyPapers = async () => {
    // Check if we already have valid cache for default category (e.g., 'cs.AI' or 'cs.CV')
    // Here we just pick a few popular categories to prefetch
    const categoriesToPrefetch = ['cs.AI', 'cs.CV', 'cs.LG'];
    
    for (const slug of categoriesToPrefetch) {
        if (globalPaperCache[slug] && (Date.now() - globalPaperCache[slug].timestamp < CACHE_TTL)) {
            continue;
        }

        if (!supabase) return;

        try {
            // Fetch first page only
            const { data: papers, error } = await supabase
                .from('papers')
                .select('*')
                .contains('categories', [slug])
                .order('published_date', { ascending: false })
                .range(0, 19);

            if (error) throw error;

            if (papers && papers.length > 0) {
                 // Also get unique dates for the filter bar
                 // Ideally this should be a separate efficient query, but for now we extract from fetched papers
                 // or we can just fetch dates. 
                 // To keep it simple and consistent with arxiv-daily.tsx logic:
                 const dates = Array.from(new Set(papers.map(p => p.published_date).filter(Boolean)));
                 
                 // We need to format dates as objects expected by the cache structure if needed
                 // But arxiv-daily.tsx expects: dates: uniqueDates (string[])
                 // Wait, let's check arxiv-daily.tsx cache usage.
                 // It says: uniqueDates = Array.from(new Set(cached.dates.map((d: any) => d.published_date)...
                 // So cached.dates should be an array of objects with published_date property?
                 // Let's check how I implemented setCachedData in arxiv-daily.tsx or how it's used.
                 
                 // Actually in arxiv-daily.tsx:
                 // const mappedItems = cached.data.map(...)
                 // if (cached.dates) uniqueDates = ...
                 
                 // Let's look at how arxiv-daily.tsx FETCHES data normally.
                 // const { data: dateData } = await supabase.from('papers').select('published_date')...
                 
                 // So if we want to prefetch properly, we should probably fetch dates too.
                 // But for a simple speedup, just caching the papers list (first page) is the biggest win.
                 // We can pass empty dates or minimal dates.
                 
                 setCachedData(slug, papers, papers.map(p => ({ published_date: p.published_date })));
            }
        } catch (err) {
            console.error(`Prefetch failed for ${slug}:`, err);
        }
    }
};

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  
  useEffect(() => {
      // Trigger prefetch on mount
      prefetchDailyPapers();
  }, []);

  return (
    <Layout
      title={`${siteConfig.title} Dashboard`}
      description="AI Paper Daily Dashboard">
      <Dashboard />
    </Layout>
  );
}
