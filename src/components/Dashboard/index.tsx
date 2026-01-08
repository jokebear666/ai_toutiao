import React from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';
import CalendarWidget from './Calendar';
import { DonutChart, TrendChart, ComparisonChart, COLORS } from './Charts';
import useBaseUrl from '@docusaurus/useBaseUrl';

// Icons
const MoreIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="1"></circle>
        <circle cx="12" cy="5" r="1"></circle>
        <circle cx="12" cy="19" r="1"></circle>
    </svg>
);

const CheckIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="none">
        <circle cx="12" cy="12" r="10" fill="#2563eb"></circle>
        <path d="M8 12l3 3 5-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);

export default function Dashboard() {
  const {siteConfig} = useDocusaurusContext();
  
  return (
    <div className={styles.container}>
        {/* Left: Calendar */}
        <div className={styles.calendarCol}>
            <CalendarWidget />
        </div>

        {/* Center: Dashboard */}
        <div className={styles.mainCol}>
            <div className={styles.headerCard}>
                <h1 className={styles.headerTitle}>Today's Dashboard</h1>
                <button style={{background:'rgba(255,255,255,0.2)', border:'none', borderRadius:'50%', width:40, height:40, display:'flex', alignItems:'center', justifyContent:'center', color:'white', cursor:'pointer'}}>
                    <MoreIcon />
                </button>
            </div>

            <div className={styles.cardRow}>
                {/* Today's Paper Count */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>
                        Today's Paper Count
                        <span style={{fontSize:'0.8rem', color:'#9ca3af', fontWeight:400}}>Goralue netwac-</span>
                    </div>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-end'}}>
                        <div>
                            <div className={styles.bigNumber}>152</div>
                            <div className={styles.growth}>↑ +15%</div>
                        </div>
                        {/* Decorative flowchart SVG */}
                        <svg width="120" height="80" viewBox="0 0 120 80">
                            <rect x="10" y="10" width="20" height="20" fill="#e5e7eb" rx="4"/>
                            <rect x="50" y="10" width="20" height="20" fill="#e5e7eb" rx="4"/>
                            <rect x="90" y="10" width="20" height="20" fill="#e5e7eb" rx="4"/>
                            <rect x="30" y="50" width="20" height="20" fill="#8b5cf6" rx="4" transform="rotate(45 40 60)"/>
                            <rect x="70" y="50" width="20" height="20" fill="#8b5cf6" rx="4" transform="rotate(45 80 60)"/>
                            <line x1="20" y1="30" x2="40" y2="50" stroke="#d1d5db" strokeWidth="2"/>
                            <line x1="60" y1="30" x2="40" y2="50" stroke="#d1d5db" strokeWidth="2"/>
                            <line x1="60" y1="30" x2="80" y2="50" stroke="#d1d5db" strokeWidth="2"/>
                            <line x1="100" y1="30" x2="80" y2="50" stroke="#d1d5db" strokeWidth="2"/>
                        </svg>
                    </div>
                </div>

                {/* Today's Paper Count by Category */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>
                        Today's Paper Count by 
                        <span style={{background:'#f3f4f6', padding:'2px 8px', borderRadius:'4px', fontSize:'0.8rem', color:'#666', fontWeight:400}}>神经系统概览</span>
                    </div>
                    <div style={{display:'flex', alignItems:'center'}}>
                        <div style={{flex:1, position:'relative'}}>
                            <DonutChart />
                            <div style={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%, -50%)', textAlign:'center', color:'#666', fontSize:'0.8rem'}}>
                                60<br/>Robotiss
                            </div>
                        </div>
                        <div style={{flex:1, fontSize:'0.75rem', display:'flex', flexDirection:'column', gap:'6px'}}>
                            {[
                                {label: 'AI/ML', color: COLORS[0]},
                                {label: 'Semppen', color: COLORS[1]},
                                {label: 'Robs (N.P)', color: COLORS[2]},
                                {label: 'Computer Vision', color: COLORS[3]},
                                {label: 'NLP', color: COLORS[4]},
                                {label: 'Theory', color: COLORS[5]},
                            ].map((item, i) => (
                                <div key={i} style={{display:'flex', alignItems:'center', gap:'8px'}}>
                                    <div style={{width:8, height:8, background: item.color, borderRadius:2}}></div>
                                    <span style={{color:'#6b7280'}}>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className={styles.cardRow}>
                {/* Paper Counts (Last 30 Days) */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>
                        Paper Counts (Last 30 Days)
                        <span style={{fontSize:'0.75rem', background:'#eff6ff', color:'#2563eb', padding:'2px 8px', borderRadius:'12px', fontWeight:400}}>Daily/ Cum (obsleen)</span>
                    </div>
                    <TrendChart />
                </div>

                {/* 热门领域趋势对比 */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>热门领域趋势对比 (CV vs NLP)</div>
                    <ComparisonChart />
                </div>
            </div>

            <div className={styles.cardRow}>
                {/* Trending Keywords */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>Trending Keywords Today</div>
                    <ul className={styles.keywordList}>
                        <li className={styles.keywordItem}>
                            <CheckIcon />
                            Large Language Models
                        </li>
                        <li className={styles.keywordItem}>
                            <CheckIcon />
                            Graph Neural (GNN)
                        </li>
                        <li className={styles.keywordItem}>
                            <CheckIcon />
                            Self-supervised Learning (SSL)
                        </li>
                    </ul>
                </div>

                {/* Recent Publications */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>Recent Publications (Highlights)</div>
                    <div className={styles.highlightList}>
                         {[1,2,3,4].map(i => (
                             <div key={i} className={styles.highlightItem}>
                                 <div className={styles.highlightImg}></div>
                                 <div style={{height:4, width:'80%', background:'#e5e7eb', margin:'0 auto 4px', borderRadius:2}}></div>
                                 <div style={{height:4, width:'60%', background:'#e5e7eb', margin:'0 auto', borderRadius:2}}></div>
                             </div>
                         ))}
                    </div>
                </div>
            </div>
        </div>

        {/* Right: Ads */}
        <div className={styles.adsCol}>
            <div className={styles.adCard}>
                <img src={useBaseUrl('/img/ads_1.png')} alt="Ad 1" className={styles.adImg} />
            </div>
            <div className={styles.adCard}>
                <img src={useBaseUrl('/img/ads_2.png')} alt="Ad 2" className={styles.adImg} />
            </div>
        </div>
    </div>
  );
}
