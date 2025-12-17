import React, {type ReactNode} from 'react';
import DocCategoryGeneratedIndexPage from '@theme-original/DocCategoryGeneratedIndexPage';
import type DocCategoryGeneratedIndexPageType from '@theme/DocCategoryGeneratedIndexPage';
import type {WrapperProps} from '@docusaurus/types';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';

type Props = WrapperProps<typeof DocCategoryGeneratedIndexPageType>;

export default function DocCategoryGeneratedIndexPageWrapper(props: Props): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const ads = (siteConfig?.themeConfig as any)?.hotAds || [];
  const hasAds = Array.isArray(ads) && ads.length > 0;
  if (!hasAds) {
    return <DocCategoryGeneratedIndexPage {...props} />;
  }
  return (
    <div className="content-with-ads">
      <div className="content-main"><div className="content-inner">
        <DocCategoryGeneratedIndexPage {...props} />
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
