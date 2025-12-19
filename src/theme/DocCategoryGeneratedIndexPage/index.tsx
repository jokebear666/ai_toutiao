import React, {type ReactNode, useMemo, useState} from 'react';
import DocCategoryGeneratedIndexPage from '@theme-original/DocCategoryGeneratedIndexPage';
import type DocCategoryGeneratedIndexPageType from '@theme/DocCategoryGeneratedIndexPage';
import type {WrapperProps} from '@docusaurus/types';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import {useLocation} from '@docusaurus/router';

type Props = WrapperProps<typeof DocCategoryGeneratedIndexPageType>;

export default function DocCategoryGeneratedIndexPageWrapper(props: Props): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const ads = (siteConfig?.themeConfig as any)?.hotAds || [];
  const hasAds = Array.isArray(ads) && ads.length > 0;
  const location = useLocation();
  const dailyBase = useBaseUrl('/daily/');
  const isDailyCategory = location.pathname.startsWith(dailyBase);
  const catSlug = isDailyCategory ? location.pathname.slice(dailyBase.length).replace(/^\//, '') : '';
  const categories = [
    {key: 'cs_AI', label: 'AI'},
    {key: 'cs_CE', label: 'CE'},
    {key: 'cs_CL', label: 'CL'},
    {key: 'cs_CV', label: 'CV'},
    {key: 'cs_LG', label: 'LG'},
    {key: 'cs_DC', label: 'DC'},
    {key: 'cs_MM', label: 'MM'},
    {key: 'cs_NE', label: 'NE'},
    {key: 'cs_RO', label: 'RO'},
    {key: 'cs_SE', label: 'SE'},
    {key: 'cs_NI', label: 'NI'},
    {key: 'cs_CY', label: 'CY'},
  ];
  const normalize = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
  const lastWeeks = (n: number) => {
    const res: string[] = [];
    const now = new Date();
    const tmp = new Date(now);
    const day = tmp.getDay();
    const diffToMonday = day === 0 ? 6 : day - 1;
    tmp.setDate(tmp.getDate() - diffToMonday);
    const fmt = (d: Date) => `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
    for (let i = 0; i < n; i++) {
      const monday = new Date(tmp);
      monday.setDate(monday.getDate() - i * 7);
      const sunday = new Date(monday);
      sunday.setDate(sunday.getDate() + 6);
      res.push(`${fmt(monday)}-${fmt(sunday)}`);
    }
    return res;
  };
  const weeks = lastWeeks(16);
  const fmtDay = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const daysOfWeek = (range: string) => {
    const [startStr] = range.split('-');
    const start = new Date(`${startStr.slice(0,4)}-${startStr.slice(4,6)}-${startStr.slice(6,8)}`);
    const res: string[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(d.getDate() + i);
      res.push(fmtDay(d));
    }
    return res;
  };
  const toCompact = (d: Date) => `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  const weekRangeOfDate = (d: Date) => {
    const tmp = new Date(d);
    const jsDay = tmp.getDay();
    const diffToMonday = jsDay === 0 ? 6 : jsDay - 1;
    const monday = new Date(tmp);
    monday.setDate(monday.getDate() - diffToMonday);
    const sunday = new Date(monday);
    sunday.setDate(sunday.getDate() + 6);
    return `${toCompact(monday)}-${toCompact(sunday)}`;
  };
  const initialMonth = new Date();
  const [monthDate, setMonthDate] = useState(new Date(initialMonth.getFullYear(), initialMonth.getMonth(), 1));
  const monthLabel = `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}`;
  const prevMonth = () => setMonthDate(new Date(monthDate.getFullYear(), monthDate.getMonth() - 1, 1));
  const nextMonth = () => setMonthDate(new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 1));
  const monthCells = useMemo(() => {
    const first = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
    const daysInMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0).getDate();
    const jsDay = first.getDay();
    const lead = jsDay === 0 ? 6 : jsDay - 1;
    const cells: (Date | null)[] = [];
    for (let i = 0; i < lead; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(new Date(monthDate.getFullYear(), monthDate.getMonth(), d));
    return cells;
  }, [monthDate]);
  if (!hasAds && !isDailyCategory) {
    return <DocCategoryGeneratedIndexPage {...props} />;
  }
  return (
    <div className={isDailyCategory ? 'content-with-ads daily-layout' : 'content-with-ads'}>
      <div className="content-main"><div className="content-inner">
        {isDailyCategory && (
          <div className="daily-nav">
            {categories.map((c) => (
              <a key={c.key} className="daily-nav-item" href={useBaseUrl(`/daily/${normalize(c.key)}`)}>{c.label}</a>
            ))}
          </div>
        )}
        <div className={isDailyCategory ? 'daily-grid' : ''}>
          <DocCategoryGeneratedIndexPage {...props} />
        </div>
      </div></div>
      {isDailyCategory ? (
        <>
          <aside className="content-right-sidebar">
            <div className="daily-time-sidebar">
              <div className="daily-time-title">选择时间</div>
              <div className="daily-calendar">
                <div className="calendar-header">
                  <button className="calendar-nav-btn" onClick={prevMonth}>‹</button>
                  <div className="calendar-title">{monthLabel}</div>
                  <button className="calendar-nav-btn" onClick={nextMonth}>›</button>
                </div>
                <div className="calendar-weekdays">
                  <div>一</div><div>二</div><div>三</div><div>四</div><div>五</div><div>六</div><div>日</div>
                </div>
                <div className="calendar-grid">
                  {monthCells.map((d, idx) => {
                    if (!d) return <div key={idx} className="calendar-cell calendar-empty" />;
                    const dayStr = fmtDay(d);
                    const range = weekRangeOfDate(d);
                    const href = catSlug ? `/daily/${normalize(catSlug)}/${range}#${dayStr}` : `/daily/${range}#${dayStr}`;
                    const isToday = fmtDay(new Date()) === dayStr;
                    return (
                      <a key={dayStr} className={`calendar-cell calendar-day${isToday ? ' is-today' : ''}`} href={useBaseUrl(href)}>
                        {String(d.getDate())}
                      </a>
                    );
                  })}
                </div>
              </div>
            </div>
          </aside>
          {hasAds && (
            <aside className="content-right-ads">
              {ads.map((ad: any, idx: number) => (
                <a className="content-ad" key={idx} href={ad.href} target="_blank" rel="noopener noreferrer">
                  <img src={/^https?:\/\//.test(ad.img) ? ad.img : useBaseUrl(ad.img?.startsWith('/') ? ad.img : '/' + ad.img)} alt={ad.alt || 'ad'} />
                </a>
              ))}
            </aside>
          )}
        </>
      ) : (
        hasAds ? (
          <aside className="content-right-ads">
            {ads.map((ad: any, idx: number) => (
              <a className="content-ad" key={idx} href={ad.href} target="_blank" rel="noopener noreferrer">
                <img src={/^https?:\/\//.test(ad.img) ? ad.img : useBaseUrl(ad.img?.startsWith('/') ? ad.img : '/' + ad.img)} alt={ad.alt || 'ad'} />
              </a>
            ))}
          </aside>
        ) : null
      )}
    </div>
  );
}
