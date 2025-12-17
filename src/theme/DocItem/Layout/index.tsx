import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
// removed intro-only leftbar logic

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props) {
  const {siteConfig} = useDocusaurusContext();
  const ads = (siteConfig?.themeConfig as any)?.hotAds || [];
  const hasAds = Array.isArray(ads) && ads.length > 0;
  if (!hasAds) {
    return <Layout {...props} />;
  }
  return (
    <div className="content-with-ads">
      <div className="content-main"><div className="content-inner">
        <Layout {...props} />
      </div></div>
      <aside className="content-right-ads">
        {ads.map((ad: any, idx: number) => (
          <a className="content-ad" key={idx} href={ad.href} target="_blank" rel="noopener noreferrer">
            <img src={/^https?:\/\//.test(ad.img) ? ad.img : useBaseUrl(ad.img?.startsWith('/') ? ad.img : '/' + ad.img)} alt={ad.alt || 'ad'} />
          </a>
        ))}
      </aside>
    </div>
  );
}
