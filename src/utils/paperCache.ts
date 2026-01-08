export type PaperCacheItem = {
    data: any[];
    dates: any[];
    timestamp: number;
};

// Global cache object
export const globalPaperCache: Record<string, PaperCacheItem> = {};

// Cache TTL (5 minutes)
export const CACHE_TTL = 5 * 60 * 1000;

export const getCachedData = (slug: string) => {
    const item = globalPaperCache[slug];
    if (!item) return null;
    
    // Optional: Check TTL here if strict expiration is needed on read
    // if (Date.now() - item.timestamp > CACHE_TTL) return null;
    
    return item;
};

export const setCachedData = (slug: string, data: any[], dates: any[]) => {
    globalPaperCache[slug] = {
        data,
        dates,
        timestamp: Date.now()
    };
};
