import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';
import CalendarWidget from './Calendar';
import { DonutChart, ComparisonChart, COLORS } from './Charts';
import useBaseUrl from '@docusaurus/useBaseUrl';

// Icons
const MoreIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="1"></circle>
        <circle cx="12" cy="5" r="1"></circle>
        <circle cx="12" cy="19" r="1"></circle>
    </svg>
);

const PdfIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
    </svg>
);

export default function Dashboard() {
  const {siteConfig} = useDocusaurusContext();
  
  return (
    <div className={styles.container}>
        {/* Left Column: Calendar & Ads */}
        <div className={styles.leftCol}>
            <CalendarWidget />
            
            <div className={styles.adCard}>
                <img src={useBaseUrl('/img/ads_1.png')} alt="Ad 1" className={styles.adImg} />
            </div>
            <div className={styles.adCard}>
                <img src={useBaseUrl('/img/ads_2.png')} alt="Ad 2" className={styles.adImg} />
            </div>
        </div>

        {/* Right Column: Main Content */}
        <div className={styles.mainCol}>
            <div className={styles.headerCard}>
                <h1 className={styles.headerTitle}>Today's Dashboard</h1>
                <button style={{background:'rgba(255,255,255,0.2)', border:'none', borderRadius:'50%', width:48, height:48, display:'flex', alignItems:'center', justifyContent:'center', color:'white', cursor:'pointer'}}>
                    <MoreIcon />
                </button>
            </div>

            <div className={styles.cardRow}>
                {/* Today's Paper (3 Previews) */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>Today's Paper</div>
                    <div className={styles.paperPreviewList}>
                        {[1, 2, 3].map((i) => (
                            <div key={i} className={styles.paperPreviewItem}>
                                <div className={styles.paperPreviewImg} style={{
                                    backgroundImage: i === 1 ? `url(${useBaseUrl('/img/docusaurus-social-card.jpg')})` : undefined,
                                    backgroundSize: 'cover'
                                }}></div>
                                <div className={styles.paperPreviewMeta}>
                                    <span>2026-01-08</span>
                                    <span style={{display:'flex', alignItems:'center', gap:4}}>
                                        <PdfIcon /> PDF
                                    </span>
                                </div>
                                <div style={{fontSize:'0.75rem', color:'#111827', fontWeight:600, lineHeight:1.4}}>
                                    Mastering the Game of Go with Self-play...
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Today's Paper Count */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>
                        Today's Paper Count
                        <span style={{fontSize:'0.85rem', color:'#9ca3af', fontWeight:400}}>Goralue netwac-</span>
                    </div>
                    <div style={{flex:1, display:'flex', flexDirection:'column', justifyContent:'center'}}>
                        <div className={styles.bigNumber}>152</div>
                        <div className={styles.growth}>↑ +15%</div>
                    </div>
                    
                    {/* Decorative Node Graph (Bottom Right) */}
                    <div style={{position:'absolute', bottom:24, right:24}}>
                        <svg width="100" height="60" viewBox="0 0 100 60">
                             {/* Nodes */}
                            <circle cx="20" cy="20" r="8" fill="#e5e7eb" />
                            <circle cx="50" cy="40" r="8" fill="#e5e7eb" />
                            <circle cx="80" cy="20" r="8" fill="#e5e7eb" />
                            <circle cx="35" cy="50" r="8" fill="#8b5cf6" />
                            <circle cx="65" cy="50" r="8" fill="#8b5cf6" />
                            
                            {/* Lines */}
                            <line x1="20" y1="20" x2="50" y2="40" stroke="#d1d5db" strokeWidth="2" />
                            <line x1="80" y1="20" x2="50" y2="40" stroke="#d1d5db" strokeWidth="2" />
                            <line x1="35" y1="50" x2="50" y2="40" stroke="#d1d5db" strokeWidth="2" />
                            <line x1="65" y1="50" x2="50" y2="40" stroke="#d1d5db" strokeWidth="2" />
                        </svg>
                    </div>
                </div>
            </div>

            <div className={styles.cardRow}>
                {/* Donut Chart */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>
                        Today's Paper Count by 
                        <span style={{background:'#f3f4f6', padding:'4px 12px', borderRadius:'6px', fontSize:'0.85rem', color:'#4b5563', fontWeight:500}}>神经系统概览</span>
                    </div>
                    <div style={{display:'flex', alignItems:'center', height:'100%'}}>
                        <div style={{flex:1, position:'relative', height:200}}>
                            <DonutChart />
                            <div style={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%, -50%)', textAlign:'center', color:'#4b5563', fontSize:'0.9rem', fontWeight:600}}>
                                60<br/>
                                <span style={{fontSize:'0.75rem', fontWeight:400, color:'#9ca3af'}}>Robotiss</span>
                            </div>
                        </div>
                        <div style={{flex:1, paddingLeft:20}}>
                            <div style={{display:'flex', flexDirection:'column', gap:12}}>
                                {[
                                    {label: 'AI/ML', color: COLORS[0]},
                                    {label: 'Semppen', color: COLORS[1]},
                                    {label: 'Robs (N.P)', color: COLORS[2]},
                                    {label: 'Computer Vision', color: COLORS[3]},
                                    {label: 'NLP', color: COLORS[4]},
                                    {label: 'Theory', color: COLORS[5]},
                                ].map((item, i) => (
                                    <div key={i} style={{display:'flex', alignItems:'center', gap:'10px'}}>
                                        <div style={{width:10, height:10, background: item.color, borderRadius:2}}></div>
                                        <span style={{color:'#4b5563', fontSize:'0.85rem', fontWeight:500}}>{item.label}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bar Chart */}
                <div className={styles.card}>
                    <div className={styles.cardTitle}>热门领域趋势对比 (CV vs NLP)</div>
                    <div style={{flex:1, display:'flex', alignItems:'flex-end'}}>
                        <ComparisonChart />
                    </div>
                    {/* X-Axis labels are handled in the chart component, but we can add custom legend if needed */}
                </div>
            </div>
        </div>
    </div>
  );
}
