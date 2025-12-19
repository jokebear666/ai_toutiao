import React from 'react';
import Layout from '@theme-original/Layout';
import {useLocation} from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function LayoutWrapper(props: any) {
  const location = useLocation();
  const introPath = useBaseUrl('/intro');
  const isIntro = location.pathname === introPath;
  const wrapperClass = isIntro ? 'layout-wrapper show-doc-sidebar' : 'layout-wrapper hide-doc-sidebar';
  return <div className={wrapperClass}><Layout {...props} /></div>;
}
