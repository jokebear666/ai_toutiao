import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import CalendarWidget from './Calendar';
import useBaseUrl from '@docusaurus/useBaseUrl';
import dashboardData from '../../data/dashboard.json';

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

const CodeIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16 18 22 12 16 6"></polyline>
        <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
);

interface PaperCardProps {
    title: string;
    link?: string;
    papers: Array<{
        id: number;
        title: string;
        date: string;
        author: string;
        tags: Array<{label: string, color: string}>;
        hasCode?: boolean;
        imgUrl?: string;
    }>;
}

const CategoryCard = ({ title, link, papers }: PaperCardProps) => (
    <Link to={link} className={styles.card} style={{textDecoration: 'none', color: 'inherit', cursor: link ? 'pointer' : 'default'}}>
        <div className={styles.cardTitle}>{title}</div>
        <div className={styles.paperPreviewList}>
            {papers.map((paper, i) => (
                <div key={i} className={styles.paperPreviewItem}>
                    <div className={styles.paperPreviewImg} style={{
                        backgroundImage: `url(${paper.imgUrl || useBaseUrl('/img/docusaurus-social-card.jpg')})`,
                        backgroundSize: 'cover'
                    }}></div>
                    
                    <div style={{fontSize:'0.8rem', color:'#111827', fontWeight:600, lineHeight:1.4, height:'2.8em', overflow:'hidden', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical'}}>
                        {paper.title}
                    </div>

                    <div style={{display:'flex', gap:4, flexWrap:'wrap'}}>
                        {paper.tags.map((tag, idx) => (
                            <span key={idx} style={{
                                fontSize:'0.65rem', 
                                padding:'2px 6px', 
                                borderRadius:4, 
                                background: tag.color, 
                                color:'#fff',
                                whiteSpace:'nowrap'
                            }}>
                                {tag.label}
                            </span>
                        ))}
                    </div>

                    <div className={styles.paperPreviewMeta} style={{marginTop:'auto'}}>
                        <span>{paper.date} · {paper.author}</span>
                        <div style={{display:'flex', gap:4}}>
                            {paper.hasCode && (
                                <span style={{display:'flex', alignItems:'center', gap:2, background:'#f3f4f6', padding:'2px 6px', borderRadius:4, fontSize:'0.65rem'}}>
                                    <CodeIcon /> CODE
                                </span>
                            )}
                            <span style={{display:'flex', alignItems:'center', gap:2, background:'#f3f4f6', padding:'2px 6px', borderRadius:4, fontSize:'0.65rem'}}>
                                <PdfIcon /> PDF
                            </span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    </Link>
);

export default function Dashboard() {
  const {siteConfig} = useDocusaurusContext();
  const hotAds = (siteConfig?.themeConfig as any)?.hotAds || [];
  
  // Use data from JSON file
  const mockPapers = dashboardData.ai || [];
  const cvPapers = dashboardData.cv || [];
  const mlPapers = dashboardData.ml || [];
  const otherPapers = dashboardData.other || [];

  return (
    <div className={styles.container}>
        {/* Left Column: Calendar & Ads */}
        <div className={styles.leftCol}>
            <CalendarWidget />
            
            {hotAds.map((ad: any, i: number) => (
                <a key={i} href={ad.href} target="_blank" rel="noopener noreferrer" className={styles.adCard} style={{display: 'block'}}>
                    <img src={useBaseUrl('/' + ad.img)} alt={ad.alt || `Ad ${i+1}`} className={styles.adImg} />
                </a>
            ))}
        </div>

        {/* Right Column: Main Content */}
        <div className={styles.mainCol}>
            <div className={styles.headerCard}>
                <h1 className={styles.headerTitle}>Today's Papers</h1>
                <button style={{background:'rgba(255,255,255,0.2)', border:'none', borderRadius:'50%', width:48, height:48, display:'flex', alignItems:'center', justifyContent:'center', color:'white', cursor:'pointer'}}>
                    <MoreIcon />
                </button>
            </div>

            <div className={styles.cardRow}>
                <CategoryCard title="Artificial Intelligence" papers={mockPapers} link="/arxiv-daily?category=csai" />
                <CategoryCard title="Computer Vision" papers={cvPapers} link="/arxiv-daily?category=cscv" />
            </div>

            <div className={styles.cardRow}>
                <CategoryCard title="Machine Learning" papers={mlPapers} link="/arxiv-daily?category=cslg" />
                <CategoryCard title="Other Fields" papers={otherPapers} link="/arxiv-daily?category=csoh" />
            </div>
        </div>
    </div>
  );
}
