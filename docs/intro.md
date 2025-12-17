---
sidebar_position: 1
title: 首页
hide_title: true
hide_table_of_contents: true
---
import BrowserOnly from '@docusaurus/BrowserOnly';

<div className="hot-header-card">
  <div className="hot-header-left">
    <div className="hot-header-icon">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="8" y1="12" x2="16" y2="12"></line>
      </svg>
    </div>
    <div>
      <div className="hot-header-title">每日早晚报</div>
      <div className="hot-header-subtitle">聚合全网AI信息、热点、历史上的今天等。每日更新。</div>
    </div>
  </div>
  <button className="hot-view-button">查看往日</button>
</div>

<div className="hot-datebar">
  <div className="hot-date">
    <BrowserOnly>{() => {
      const d = new Date();
      const pad = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}年${pad(d.getMonth()+1)}月${pad(d.getDate())}日`;
    }}</BrowserOnly>
  </div>
  <div className="hot-date-actions">
    <div className="hot-icon">☁️</div>
    <div className="hot-icon">📤</div>
  </div>
  </div>

<div className="hot-lunar-box">
  <BrowserOnly>{() => {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const week = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'][d.getDay()];
    const lunarInfo = [0x04bd8,0x04ae0,0x0a570,0x054d5,0x0d260,0x0d950,0x16554,0x056a0,0x09ad0,0x055d2,0x04ae0,0x0a5b6,0x0a4d0,0x0d250,0x1d255,0x0b540,0x0d6a0,0x0ada2,0x095b0,0x14977,0x04970,0x0a4b0,0x0b4b5,0x06a50,0x06d40,0x1ab54,0x02b60,0x09570,0x052f2,0x04970,0x06566,0x0d4a0,0x0ea50,0x06e95,0x05ad0,0x02b60,0x186e3,0x092e0,0x1c8d7,0x0c950,0x0d4a0,0x1d8a6,0x0b550,0x056a0,0x1a5b4,0x025d0,0x092d0,0x0d2b2,0x0a950,0x0b557,0x06ca0,0x0b550,0x15355,0x04da0,0x0a5d0,0x14573,0x052d0,0x0a9a8,0x0e950,0x06aa0,0x0aea6,0x0ab50,0x04b60,0x0aae4,0x0a570,0x05260,0x0f263,0x0d950,0x05b57,0x056a0,0x096d0,0x04dd5,0x04ad0,0x0a4d0,0x0d4d4,0x0d250,0x0d558,0x0b540,0x0b5a0,0x195a6,0x095b0,0x049b0,0x0a974,0x0a4b0,0x0b27a,0x06a50,0x06d40,0x0af46,0x0ab60,0x09570,0x04af5,0x04970,0x064b0,0x074a3,0x0ea50,0x06b58,0x05ac0,0x0ab60,0x096d5,0x092e0,0x0c960,0x0d954,0x0d4a0,0x0da50,0x07552,0x056a0,0x0abb7,0x025d0,0x092d0,0x0cab5,0x0a950,0x0b4a0,0x0baa4,0x0ad50,0x055d9,0x04ba0,0x0a5b0,0x15176,0x052b0,0x0a930,0x07954,0x06aa0,0x0ad50,0x05b52,0x04b60,0x0a6e6,0x0a4e0,0x0d260,0x0ea65,0x0d530,0x05aa0,0x076a3,0x096d0,0x04bd7,0x04ad0,0x0a4d0,0x1d0b6,0x0d250,0x0d520,0x0dd45,0x0b5a0,0x056d0,0x055b2,0x049b0,0x0a577,0x0a4b0,0x0aa50,0x1b255,0x06d20,0x0ada0,0x14b63];
    const lYearDays = (y) => { let sum = 348; for (let i = 0x8000; i > 0x8; i >>= 1) sum += (lunarInfo[y-1900] & i) ? 1 : 0; return sum + leapDays(y); };
    const leapMonth = (y) => (lunarInfo[y-1900] & 0xf);
    const leapDays = (y) => leapMonth(y) ? ((lunarInfo[y-1900] & 0x10000) ? 30 : 29) : 0;
    const monthDays = (y,m) => ((lunarInfo[y-1900] & (0x10000 >> m)) ? 30 : 29);
    const offset = Math.floor((d.getTime() - new Date(1900,0,31).getTime())/86400000);
    let i=1900, temp=0; let off=offset;
    for (; i<2101 && off>0; i++) { temp = lYearDays(i); off -= temp; }
    if (off<0) { off += temp; i--; }
    const year = i;
    const leap = leapMonth(year);
    let isLeap = false; let month=1;
    for (; month<13 && off>0; month++) {
      temp = (leap>0 && month===leap+1 && !isLeap) ? leapDays(year) : monthDays(year, month);
      if (leap>0 && month===leap+1 && !isLeap) { isLeap = true; month--; }
      else if (isLeap && month===leap+1) { isLeap = false; }
      off -= temp;
    }
    if (off===0 && leap>0 && month===leap+1) { if (isLeap) { isLeap=false; } else { isLeap=true; month--; } }
    if (off<0) { off += temp; month--; }
    const day = off + 1;
    const toCNYear = (y) => String(y).split('').map(c=>({"0":"〇","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六","7":"七","8":"八","9":"九"}[c])).join('');
    const monthNames = ['一','二','三','四','五','六','七','八','九','十','十一','十二'];
    const dayToCN = (d) => d<=10?['初一','初二','初三','初四','初五','初六','初七','初八','初九','初十'][d-1]:d<20?('十'+['一','二','三','四','五','六','七','八','九'][d-10]):d===20?'二十':d<30?('廿'+['一','二','三','四','五','六','七','八','九'][d-20]):'三十';
    const lunarStr = `农历${toCNYear(year)}年 ${monthNames[month-1]}月${dayToCN(day)}`;
    return `今天是${d.getFullYear()}年${pad(d.getMonth()+1)}月${pad(d.getDate())}日 ${week}，${lunarStr}`;
  }}</BrowserOnly>
</div>

<h3>今日简报 · AI</h3>

<div className="hot-pills">
  <span className="pill pill-primary">早报</span>
  <span className="pill">晚报</span>
</div>

<ol className="hot-news-list">
  <li>澳大利亚邦迪海滩发生枪击事件：已造成至少12人死亡，警方称可能为恐袭。</li>
  <li>悉尼枪击事件现场视频曝光：居民描述听到数十声枪响，现场一片混乱。</li>
  <li>泽连斯基放弃加入北约：乌克兰总统表示和平计划必然包含妥协。</li>
  <li>美媒称美国头号敌人是自身债务：经济问题成为当前最大的隐忧。</li>
  <li>张本智和夺得WTT总决赛男单冠军：决赛以4比2获胜。</li>
  <li>王曼昱卫冕WTT总决赛女单冠军：表现优异。</li>
  <li>澳总理：枪击案是针对犹太人的恐袭：言论引发关注。</li>
  <li>83个国家拥抱AI教育计划：对教育公平与效率具有潜在影响。</li>
  <li>谷歌发布高能效AI芯片方案：强调能效与可扩展性。</li>
  <li>阿里云推出混合推理平台：面向企业级大模型应用落地。</li>
</ol>
