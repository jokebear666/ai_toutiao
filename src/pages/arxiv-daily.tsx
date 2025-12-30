import React, {useEffect, useMemo, useState} from 'react';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Mermaid from '@theme/Mermaid';

type PaperItem = {
  title: string;
  authors?: string;
  institution?: string;
  link?: string;
  code?: string;
  tags?: string[];
  day?: string;
  thumbnail?: string;
  contributions?: string;
  summary?: string;
  mindmap?: string;
  slug?: string;
};
type CategoryData = { label: string; slug: string; week?: string; items?: PaperItem[] };

const CodeIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6"></polyline>
    <polyline points="8 6 2 12 8 18"></polyline>
  </svg>
);

const PdfIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);

const DetailModal = ({ paper, onClose }: { paper: PaperItem; onClose: () => void }) => {
  const [slide, setSlide] = useState(0); // 0: Image, 1: Mindmap

  // Prevent background scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  return (
    <div className="paper-modal-overlay" onClick={onClose}>
      <div className="paper-modal-content" onClick={e => e.stopPropagation()}>
        <button className="paper-modal-close" onClick={onClose}>×</button>
        
        <div className="paper-modal-slider">
             <div className="paper-modal-slide" style={{ transform: `translateX(-${slide * 100}%)` }}>
                {/* Slide 0: Image */}
                <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', flexShrink: 0 }}>
                    {paper.thumbnail ? (
                        <img src={paper.thumbnail} alt={paper.title} />
                    ) : (
                        <div style={{color: '#999'}}>No Image Available</div>
                    )}
                </div>
                {/* Slide 1: Mindmap */}
                <div style={{ width: '100%', height: '100%', left: '100%', position: 'absolute', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'auto', padding: '20px' }}>
                     {paper.mindmap ? (
                        <div style={{ minWidth: '100%', minHeight: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                            <Mermaid value={(() => {
                              const text = paper.mindmap.replace(/"/g, '”');
                              // If mindmap already uses [] syntax, skip ()->[] conversion
                              // Check for any [ to be robust (including Chinese node IDs)
                              if (text.includes('[')) {
                                return text.replace(/\(/g, '（').replace(/\)/g, '）');
                              }
                              return text
                                .replace(/(\w+)\(([^)]*)\)/g, '$1[$2]') // Convert ID(...) to ID[...] (non-greedy)
                                .replace(/\(/g, '（') // Escape remaining parens
                                .replace(/\)/g, '）');
                            })()} />
                        </div>
                     ) : (
                        <div style={{color: '#999'}}>No Mindmap Available</div>
                     )}
                </div>
             </div>
             
             <button className="paper-modal-nav prev" onClick={() => setSlide(0)}>‹</button>
             <button className="paper-modal-nav next" onClick={() => setSlide(1)}>›</button>
             
             <div className="paper-modal-tabs">
                <div className={`paper-modal-tab ${slide === 0 ? 'active' : ''}`} onClick={() => setSlide(0)} />
                <div className={`paper-modal-tab ${slide === 1 ? 'active' : ''}`} onClick={() => setSlide(1)} />
             </div>
        </div>

        <div className="paper-modal-details">
            <div className="paper-modal-title">{paper.title}</div>
            <div className="paper-modal-meta">
                {paper.authors && <div><strong>Authors:</strong> {paper.authors}</div>}
                {paper.institution && <div><strong>Institution:</strong> {paper.institution}</div>}
                {paper.link && <div><strong>Link:</strong> <a href={paper.link} target="_blank" rel="noopener noreferrer">{paper.link}</a></div>}
                {paper.code && paper.code !== 'None' && <div><strong>Code:</strong> <a href={paper.code} target="_blank" rel="noopener noreferrer">{paper.code}</a></div>}
                {paper.day && <div><strong>Date:</strong> {paper.day}</div>}
                {paper.tags && Array.isArray(paper.tags) && paper.tags.length > 0 && (
                    <div>
                        <strong>Tags:</strong>
                        <div className="tag-container">
                            {paper.tags.map((tag, idx) => (
                                <span key={idx} className="tag-badge">{tag}</span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {paper.summary && (
                <div className="paper-modal-section">
                    <h3>Summary</h3>
                    <div className="paper-modal-summary">
                        {paper.summary}
                    </div>
                </div>
            )}

            {paper.contributions && (
                <div className="paper-modal-section">
                    <h3>Contributions</h3>
                    <div className="paper-modal-contributions">
                        <ul>
                            {paper.contributions.split(/(?=\d+\.)/).filter(i => i.trim().length > 0).map((item, i) => {
                                const cleanItem = item.replace(/^\d+\.\s*/, '').trim();
                                if (!cleanItem) return null;
                                return <li key={i}>{cleanItem}</li>;
                            })}
                        </ul>
                    </div>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

const CalendarWidget = ({ availableDates, selectedDate, onSelectDate }: { availableDates: string[], selectedDate: string | null, onSelectDate: (d: string | null) => void }) => {
    const [currentMonth, setCurrentMonth] = useState(() => {
        if (availableDates.length > 0) {
            const d = new Date(availableDates[0]);
            return new Date(d.getFullYear(), d.getMonth(), 1);
        }
        return new Date();
    });

    useEffect(() => {
        if (availableDates.length > 0) {
            const d = new Date(availableDates[0]);
            setCurrentMonth(new Date(d.getFullYear(), d.getMonth(), 1));
        }
    }, [availableDates]);

    const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
    const firstDayOfWeek = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay(); // 0 is Sunday

    const days = [];
    for (let i = 0; i < firstDayOfWeek; i++) {
        days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
        days.push(new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i));
    }

    const formatDate = (d: Date) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    };

    const prevMonth = () => {
        setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
    };

    const nextMonth = () => {
        setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
    };

    const monthNames = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];

    return (
        <div className="calendar-widget">
            <div className="calendar-header">
                <button onClick={prevMonth}>‹</button>
                <span>{currentMonth.getFullYear()}年 {monthNames[currentMonth.getMonth()]}</span>
                <button onClick={nextMonth}>›</button>
            </div>
            <div className="calendar-grid">
                <div className="calendar-day-header">日</div>
                <div className="calendar-day-header">一</div>
                <div className="calendar-day-header">二</div>
                <div className="calendar-day-header">三</div>
                <div className="calendar-day-header">四</div>
                <div className="calendar-day-header">五</div>
                <div className="calendar-day-header">六</div>
                {days.map((d, i) => {
                    if (!d) return <div key={i} className="calendar-day empty"></div>;
                    const dateStr = formatDate(d);
                    const hasData = availableDates.includes(dateStr);
                    const isSelected = selectedDate === dateStr;
                    return (
                        <div 
                            key={i} 
                            className={`calendar-day ${hasData ? 'has-data' : ''} ${isSelected ? 'selected' : ''}`}
                            onClick={() => hasData && onSelectDate(dateStr)}
                        >
                            {d.getDate()}
                        </div>
                    );
                })}
            </div>
            <button 
                className={`calendar-all-btn ${selectedDate === null ? 'active' : ''}`} 
                onClick={() => onSelectDate(null)}
            >
                显示全部 Paper
            </button>
        </div>
    );
};

export default function ArxivDailyPage() {
  const {siteConfig} = useDocusaurusContext();
  const [data, setData] = useState<CategoryData[]>([]);
  const [loadedCats, setLoadedCats] = useState<Set<string>>(new Set());
  const [searchIndex, setSearchIndex] = useState<PaperItem[]>([]);
  const [active, setActive] = useState<string>('csai');
  const [selectedPaper, setSelectedPaper] = useState<PaperItem | null>(null);
  const dataUrl = useBaseUrl('/data/arxiv_daily.json');
  const baseUrl = siteConfig.baseUrl || '/';
  const hotAds = (siteConfig?.themeConfig as any)?.hotAds || [];

  // 1. Load Metadata (Categories list)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(dataUrl);
        if (!res.ok) return;
        const json = await res.json();
        const cats: CategoryData[] = json.categories || [];
        if (!cancelled) {
          // Initialize items as empty array to avoid undefined errors
          const safeCats = cats.map(c => ({...c, items: c.items || []}));
          setData(safeCats);
          if (safeCats.length && !safeCats.find(c => c.slug === active)) {
            setActive(safeCats[0].slug);
          }
        }
      } catch {}
    })();
    return () => { cancelled = true; };
  }, [dataUrl]);

  // 2. Load Active Category Data
  useEffect(() => {
    if (!active || loadedCats.has(active)) return;
    
    (async () => {
        try {
            const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/';
            const url = `${cleanBase}data/arxiv_daily_${active}.json`;
            const res = await fetch(url);
            if (!res.ok) return;
            const catData = await res.json();
            
            setData(prev => prev.map(c => c.slug === active ? { ...c, items: catData.items || [] } : c));
            setLoadedCats(prev => new Set(prev).add(active));
        } catch (e) { console.error("Failed to load category", active, e); }
    })();
  }, [active, loadedCats, baseUrl]);

  // 3. Load Search Index
  useEffect(() => {
      (async () => {
          try {
             const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/';
             const url = `${cleanBase}data/arxiv_daily_search.json`;
             const res = await fetch(url);
             if (res.ok) {
                 const idx = await res.json();
                 setSearchIndex(idx);
             }
          } catch {}
      })();
  }, [baseUrl]);

  const zhMap = useMemo(() => ({
    ai: '人工智能', ce: '计算工程', cl: '计算语言学', cv: '计算机视觉', lg: '机器学习', dc: '分布式计算',
    mm: '多媒体', ne: '神经与进化计算', ro: '机器人学', se: '软件工程', ni: '网络与互联网架构', cy: '计算与社会',
    db: '数据库', ds: '数据结构与算法', gr: '图形学', gt: '博弈论', hc: '人机交互', ir: '信息检索', it: '信息论',
    ma: '多智能体系统', os: '操作系统', pl: '编程语言', sc: '符号计算', sd: '声音', si: '社会与信息网络', cr: '密码与安全',
    ar: '硬件架构', cc: '计算复杂性', cg: '计算几何', dl: '数字图书馆', dm: '离散数学', et: '新兴技术',
    fl: '形式语言与自动机', lo: '计算机逻辑', ms: '数学软件', oh: '其他', pf: '性能',
    na: '数值分析', sy: '系统与控制'
  }), []);
  const priorityMap = useMemo(() => ({
    ai: 1, ce: 2, cl: 3, cv: 4, lg: 5, dc: 6, mm: 7, ne: 8,
    ro: 9, se: 10, ni: 11, cy: 12,
    db: 13, ir: 14, os: 15, pl: 16, cr: 17,
    it: 18, ds: 19, ma: 20, sc: 21, sd: 22, si: 23, gr: 24, gt: 25, hc: 26
  }), []);
  const displayCats = useMemo(() => {
    const cats = data.map(c => {
      const short = (c.label || '').replace('cs.', '').toLowerCase();
      const cn = (zhMap as any)[short] || short.toUpperCase();
      const pri = (priorityMap as any)[short] ?? 999;
      return {label: cn, slug: c.slug, pri};
    });
    cats.sort((a, b) => (a.pri - b.pri) || a.label.localeCompare(b.label));
    return cats.map(({label, slug}) => ({label, slug}));
  }, [data, zhMap, priorityMap]);
  const visibleCats = useMemo(() => displayCats.slice(0, 8), [displayCats]);
  const overflowCats = useMemo(() => displayCats.slice(8), [displayCats]);
  const [moreOpen, setMoreOpen] = useState(false);
  const activeItems = useMemo(() => (data.find(c => c.slug === active)?.items || []), [data, active]);
  const allItems = useMemo(() => data.flatMap(c => c.items || []), [data]);

  const availableDates = useMemo(() => {
    const dates = new Set(activeItems.map(it => it.day).filter(Boolean) as string[]);
    return Array.from(dates).sort().reverse();
  }, [activeItems]);

  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  
  useEffect(() => {
    if (availableDates.length > 0) {
      setSelectedDate(availableDates[0]);
    } else {
      setSelectedDate(null);
    }
  }, [active, availableDates]);

  const [googleTranslateInit, setGoogleTranslateInit] = useState(false);
  
  // ... (google translate useEffect) ...

  const [searchQuery, setSearchQuery] = useState('');
  const [translatedQuery, setTranslatedQuery] = useState('');

  // Auto-translate Chinese query to English for better search results
  useEffect(() => {
    const query = searchQuery.trim();
    if (!query) {
      setTranslatedQuery('');
      return;
    }

    // Check if query contains Chinese characters
    const hasChinese = /[\u4e00-\u9fa5]/.test(query);
    if (!hasChinese) {
      setTranslatedQuery(query);
      return;
    }

    // Debounce translation to avoid too many requests
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=en&dt=t&q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data && data[0] && data[0][0] && data[0][0][0]) {
            setTranslatedQuery(data[0][0][0]);
        }
      } catch (e) {
        // Fallback to original query on error
        setTranslatedQuery(query);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const displayItems = useMemo(() => {
    // Use translatedQuery for filtering if available, otherwise searchQuery
    const effectiveQuery = translatedQuery || searchQuery;
    
    if (effectiveQuery.trim()) {
      const lowerQuery = effectiveQuery.toLowerCase();
      // Use searchIndex for search
      return searchIndex.filter(it => {
        const titleMatch = (it.title || '').toLowerCase().includes(lowerQuery);
        const tagsMatch = (it.tags || []).some(tag => tag.toLowerCase().includes(lowerQuery));
        return titleMatch || tagsMatch;
      });
    }
    if (!selectedDate) return activeItems;
    return activeItems.filter(it => it.day === selectedDate);
  }, [activeItems, searchIndex, selectedDate, searchQuery, translatedQuery]);

  const handleCardClick = async (it: PaperItem) => {
      // If search mode and item has slug (from search index), we might need to load full data
      if (searchQuery.trim() && it.slug) {
          const targetSlug = it.slug;
          if (targetSlug !== active) {
              setActive(targetSlug);
          }

          let fullItem = it;
          // Check if we need to fetch full data
          if (!loadedCats.has(targetSlug)) {
             try {
                 const cleanBase = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/';
                 const url = `${cleanBase}data/arxiv_daily_${targetSlug}.json`;
                 const res = await fetch(url);
                 const catData = await res.json();
                 
                 // Update state
                 setData(prev => prev.map(c => c.slug === targetSlug ? { ...c, items: catData.items || [] } : c));
                 setLoadedCats(prev => new Set(prev).add(targetSlug));
                 
                 // Find full item
                 const found = catData.items?.find((i: PaperItem) => i.title === it.title);
                 if (found) fullItem = found;
             } catch (e) { console.error("Error loading details", e); }
          } else {
             // Already loaded, find it in data
             const cat = data.find(c => c.slug === targetSlug);
             const found = cat?.items?.find(i => i.title === it.title);
             if (found) fullItem = found;
          }
          setSelectedPaper(fullItem);
      } else {
          // Normal mode or item without slug (shouldn't happen in search index)
          setSelectedPaper(it);
      }
  };

  return (
    <Layout title="Arxiv每日论文">
      <div className="arxiv-page">
        <aside className="arxiv-leftbar">
          <div className="arxiv-left-logo">每日论文速递</div>
          <CalendarWidget 
              availableDates={availableDates} 
              selectedDate={selectedDate} 
              onSelectDate={(date) => {
                setSelectedDate(date);
                setSearchQuery(''); // Clear search when date is selected
              }} 
          />
        </aside>
        <main className="arxiv-main">
          <div className="arxiv-top">
            <div className="arxiv-search">
              <input 
                placeholder="搜索标题或标签..." 
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  if (e.target.value.trim()) {
                    setSelectedDate(null); // Clear date selection when searching
                  }
                }}
              />
              {searchQuery && (
                  <button 
                    className="arxiv-search-clear"
                    onClick={() => {
                        setSearchQuery('');
                        if (availableDates.length > 0) {
                            setSelectedDate(availableDates[0]);
                        }
                    }}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
              )}
            </div>
          </div>
          <div className="arxiv-pills">
            {displayCats.length ? (
              <div className="arxiv-pills-row">
                {visibleCats.map((c) => (
                  <button key={c.slug} className={"arxiv-pill" + (c.slug === active ? ' is-active' : '')} onClick={() => { setActive(c.slug); setMoreOpen(false); }}>
                    {c.label}
                  </button>
                ))}
                {overflowCats.length > 0 && (
                  <div className={"arxiv-more" + (moreOpen ? ' is-open' : '')}>
                    <button className="arxiv-pill" onClick={() => setMoreOpen(!moreOpen)}>更多类型</button>
                    <div className="arxiv-more-menu">
                      {overflowCats.map((c) => (
                        <button key={c.slug} className={"arxiv-more-item" + (c.slug === active ? ' is-active' : '')} onClick={() => { setActive(c.slug); setMoreOpen(false); }}>
                          {c.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="arxiv-pills-row">
                {['人工智能','计算工程','计算语言学','计算机视觉','机器学习','分布式计算','多媒体','神经与进化计算'].map((c) => (
                  <button key={c} className="arxiv-pill" disabled>{c}</button>
                ))}
                <div className="arxiv-more">
                  <button className="arxiv-pill" disabled>更多类型</button>
                </div>
              </div>
            )}
          </div>
          <div className="arxiv-grid">
            {displayItems.map((it, idx) => {
              const firstAuthor = ((it.authors || '').split(',')[0] || '').trim();
              return (
                <div key={idx} className="arxiv-card" onClick={() => handleCardClick(it)}>
                  <div className="arxiv-card-image">
                    {it.thumbnail ? (
                      <img src={it.thumbnail} loading="lazy" alt="" />
                    ) : null}
                  </div>
                  <div className="arxiv-card-footer">
                    <div className="arxiv-footer-title">{it.title}</div>
                    {it.tags && Array.isArray(it.tags) && it.tags.length > 0 && (
                      <div className="arxiv-card-tag-row">
                        <span className="arxiv-card-tag">{it.tags[0]}</span>
                      </div>
                    )}
                    <div className="arxiv-footer-line">
                      <span className="arxiv-author">{firstAuthor}</span>
                      <div className="arxiv-actions">
                        {it.code && it.code !== 'None' && (
                          <a className="arxiv-btn arxiv-btn-code" href={it.code} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                            <CodeIcon />
                            CODE
                          </a>
                        )}
                        {it.link ? (
                          <a className="arxiv-btn arxiv-btn-pdf" href={it.link} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                            <PdfIcon />
                            PDF
                          </a>
                        ) : (
                          <span className="arxiv-like">{it.day || ''}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </main>
        <aside className="arxiv-right-ads">
          {hotAds && Array.isArray(hotAds) && hotAds.map((a: any, idx: number) => (
            <a key={idx} className="arxiv-ad" href={a.href} target="_blank" rel="noopener noreferrer">
              <img src={useBaseUrl('/' + a.img)} alt={a.alt || ''} loading="lazy" decoding="async" />
            </a>
          ))}
        </aside>
      </div>
      {selectedPaper && <DetailModal paper={selectedPaper} onClose={() => setSelectedPaper(null)} />}
    </Layout>
  );
}
