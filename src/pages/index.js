import React from 'react';
import { Redirect } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function Home() {
  // const introUrl = useBaseUrl('/intro');
  // return <Redirect to={introUrl} />;
  const targetUrl = useBaseUrl('/arxiv-daily');
  return <Redirect to={targetUrl} />;
}
