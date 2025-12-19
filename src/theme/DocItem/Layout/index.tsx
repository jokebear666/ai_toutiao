import React, {useMemo, useState} from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import {useLocation} from '@docusaurus/router';
// removed intro-only leftbar logic

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props) {
  const {siteConfig} = useDocusaurusContext();
  const ads = (siteConfig?.themeConfig as any)?.hotAds || [];
  const hasAds = Array.isArray(ads) && ads.length > 0;
  const location = useLocation();
  const dailyBase = useBaseUrl('/daily/');
  const isDaily = location.pathname.startsWith(dailyBase);

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
    const start = new Date(
      `${startStr.slice(0, 4)}-${startStr.slice(4, 6)}-${startStr.slice(6, 8)}`,
    );
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

  const after = location.pathname.slice(dailyBase.length);
  const mPath = after.match(/^(\w+)(?:\/(\d{8}-\d{8}))?/);
  const catFromPath = mPath ? mPath[1] : '';
  const weekFromPath = mPath && mPath[2] ? mPath[2] : '';
  const hashDay = location.hash?.replace('#', '') || '';
  const initialDate = useMemo(() => {
    if (hashDay && /\d{4}-\d{2}-\d{2}/.test(hashDay)) {
      return new Date(hashDay);
    }
    if (weekFromPath) {
      const startStr = weekFromPath.slice(0, 8);
      return new Date(`${startStr.slice(0,4)}-${startStr.slice(4,6)}-${startStr.slice(6,8)}`);
    }
    return new Date();
  }, [hashDay, weekFromPath]);
  const [monthDate, setMonthDate] = useState(new Date(initialDate.getFullYear(), initialDate.getMonth(), 1));
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

  if (!isDaily && !hasAds) {
    return <Layout {...props} />;
  }

  return (
    <div className={isDaily ? 'content-with-ads daily-layout' : 'content-with-ads'}>
      <div className="content-main"><div className="content-inner">
        {isDaily && (
          <div className="daily-nav">
            {categories.map((c) => (
              <a key={c.key} className="daily-nav-item" href={useBaseUrl(`/daily/${normalize(c.key)}`)}>{c.label}</a>
            ))}
          </div>
        )}
        <div className={isDaily ? 'daily-grid' : ''}>
          <Layout {...props} />
        </div>
      </div></div>
      {isDaily ? (
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
                    const cat = catFromPath || '';
                    const href = cat ? `/daily/${cat}/${range}#${dayStr}` : `/daily/${range}#${dayStr}`;
                    const isToday = fmtDay(new Date()) === dayStr;
                    const active = hashDay === dayStr;
                    return (
                      <a key={dayStr} className={`calendar-cell calendar-day${isToday ? ' is-today' : ''}${active ? ' is-active' : ''}`} href={useBaseUrl(href)}>
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
      ) : hasAds ? (
        <aside className="content-right-ads">
          {ads.map((ad: any, idx: number) => (
            <a className="content-ad" key={idx} href={ad.href} target="_blank" rel="noopener noreferrer">
              <img src={/^https?:\/\//.test(ad.img) ? ad.img : useBaseUrl(ad.img?.startsWith('/') ? ad.img : '/' + ad.img)} alt={ad.alt || 'ad'} />
            </a>
          ))}
        </aside>
      ) : null}
    </div>
  );
}
