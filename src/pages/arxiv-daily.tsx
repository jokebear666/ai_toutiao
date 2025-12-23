import React, {useEffect, useMemo, useState} from 'react';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

type PaperItem = { title: string; authors?: string; link?: string; day?: string; thumbnail?: string };
type CategoryData = { label: string; slug: string; week?: string; items: PaperItem[] };

export default function ArxivDailyPage() {
  const {siteConfig} = useDocusaurusContext();
  const [data, setData] = useState<CategoryData[]>([]);
  const [active, setActive] = useState<string>('csai');
  const dataUrl = useBaseUrl('/data/arxiv_daily.json');
  const hotAds = (siteConfig?.themeConfig as any)?.hotAds || [];

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(dataUrl);
        if (!res.ok) return;
        const json = await res.json();
        const cats: CategoryData[] = json.categories || [];
        if (!cancelled) {
          setData(cats);
          if (cats.length && !cats.find(c => c.slug === active)) {
            setActive(cats[0].slug);
          }
        }
      } catch {}
    })();
    return () => { cancelled = true; };
  }, [dataUrl]);

  const zhMap = useMemo(() => ({
    ai: '人工智能', ce: '计算工程', cl: '计算语言学', cv: '计算机视觉', lg: '机器学习', dc: '分布式计算',
    mm: '多媒体', ne: '神经与进化计算', ro: '机器人学', se: '软件工程', ni: '网络与互联网架构', cy: '计算与社会',
    db: '数据库', ds: '数据结构与算法', gr: '图形学', gt: '博弈论', hc: '人机交互', ir: '信息检索', it: '信息论',
    ma: '多智能体系统', os: '操作系统', pl: '编程语言', sc: '符号计算', sd: '声音', si: '社会与信息网络', cr: '密码与安全'
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

  return (
    <Layout title="Arxiv每日论文">
      <div className="arxiv-page">
        <aside className="arxiv-leftbar">
          <div className="arxiv-left-logo">每日论文速递</div>
          <nav className="arxiv-left-menu">
            <a className="arxiv-left-item" href="#">发现</a>
            <a className="arxiv-left-item" href="#">发布</a>
            <a className="arxiv-left-item" href="#">通知</a>
          </nav>
          <a className="arxiv-login-btn" href="#">登录</a>
          <div className="arxiv-left-tips">
            <div>马 上 登 录 即 可</div>
            <ul>
              <li>周围同好优质内容</li>
              <li>和创作者互动交流</li>
              <li>与其他用户交流、交流</li>
            </ul>
          </div>
          <div className="arxiv-left-more">更多</div>
        </aside>
        <main className="arxiv-main">
          <div className="arxiv-top">
            <div className="arxiv-search">
              <input placeholder="登录探索更多内容" />
            </div>
            <div className="arxiv-top-links">
              <a href="#">创作中心</a>
              <a href="#">业务合作</a>
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
            {activeItems.map((it, idx) => {
              const h = 200 + ((idx % 3) * 40);
              const firstAuthor = ((it.authors || '').split(',')[0] || '').trim();
              return (
                <div key={idx} className="arxiv-card">
                  <div className="arxiv-card-image" style={{height: h}}>
                    {it.thumbnail ? (
                      <img src={it.thumbnail} loading="lazy" alt="" />
                    ) : null}
                  </div>
                  <div className="arxiv-card-footer">
                    <div className="arxiv-footer-title">{it.title}</div>
                    <div className="arxiv-footer-line">
                      <span className="arxiv-author">{firstAuthor}</span>
                      {it.link ? (
                        <a className="arxiv-like" href={it.link} target="_blank" rel="noopener noreferrer">PDF</a>
                      ) : (
                        <span className="arxiv-like">{it.day || ''}</span>
                      )}
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
              <img src={useBaseUrl('/' + a.img)} alt={a.alt || ''} />
            </a>
          ))}
        </aside>
      </div>
    </Layout>
  );
}
