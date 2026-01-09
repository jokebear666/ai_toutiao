// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';
import 'dotenv/config';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

console.log("Supabase Config Loaded:", {
  url: process.env.SUPABASE_URL,
  hasKey: !!process.env.SUPABASE_ANON_KEY
});

const isDev = process.env.NODE_ENV === 'development';
const isVercel = !!process.env.VERCEL;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI头条',
  tagline: 'AI头条',
  favicon: 'img/favicon_b.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://jokebear666.github.io',
 // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  customFields: {
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseAnonKey: process.env.SUPABASE_ANON_KEY,
  },

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'jokebear666', // Usually your GitHub org/user name.
  projectName: 'ai_toutiao', // Usually your repo name.
  trailingSlash: true,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
  
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: 'docs',
          showLastUpdateTime: true,
          remarkPlugins: [require('remark-math')],
          rehypePlugins: [require('rehype-katex')],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      docs: {
        sidebar: {
          hideable: true,
        },
      },
      navbar: {
        title: 'AI头条',
        logo: {
          alt: 'AI头条',
          src: 'img/favicon_b.ico',
        },
        hideOnScroll: false,
        items: [
          {
            to: '/arxiv-daily',
            label: 'Arxiv每日论文',
            position: 'left',
            activeBaseRegex: '^/arxiv-daily'
          },
          // {
          //   to: '/category/daily',
          //   label: 'Daily',
          //   position: 'left',
          //   activeBaseRegex: '^/category/daily'
          // },
          // {
          //   to: '/category/paper',
          //   label: 'Paper',
          //   position: 'left',
          //   activeBaseRegex: '^/category/paper'
          // },
          {
            to: '/docs/sponsor/advertise',
            label: '赞助商',
            position: 'right',
            activeBaseRegex: '^/docs/sponsor/'
          },
          // {
          //   href: 'https://github.com/jokebear666',
          //   label: 'GitHub',
          //   position: 'right',
          // },
        ],
      },
      hotAds: [
        { img: 'img/ads_1.png', href: 'https://xhslink.com/m/2lTbaZQ1RbP', alt: 'AI头条' },
        { img: 'img/ads_2.png', href: 'https://xhslink.com/m/2lTbaZQ1RbP', alt: '草莓师姐' }
      ],
      // footer: {
      //   style: 'dark',
      //   copyright: `Copyright © ${new Date().getFullYear()} jokebear666, Inc. Built with Docusaurus.`,
      // },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
