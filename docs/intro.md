---
sidebar_position: 1
title: 首页
hide_title: true
hide_table_of_contents: true
---

{/* 顶部深色卡片区域 */}
<div style={{
  backgroundImage: 'linear-gradient(135deg, #3a3d42 0%, #2b2d30 100%)',
  color: '#fff',
  borderRadius: '8px',
  padding: '24px',
  marginBottom: '20px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between'
}}>
  <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
    {/* 红色图标 */}
    <div style={{
      backgroundColor: '#f13b3b',
      width: '56px',
      height: '56px',
      borderRadius: '12px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="8" y1="12" x2="16" y2="12"></line>
      </svg>
    </div>
    {/* 标题文字 */}
    <div>
      <h2 style={{margin: 0, fontSize: '20px', color: 'white', fontWeight: 'bold'}}>AI头条</h2>
      <p style={{margin: '4px 0 0 0', fontSize: '13px', color: '#aab0b8', lineHeight: '1.4'}}>
        聚合全网AI信息, AI工具, 热门Paper, AI产品发布, 热门代码库等。
      </p>
    </div>
  </div>
  {/* 查看往日按钮 */}
  <button style={{
    background: 'transparent',
    border: '1px solid #6b7280',
    color: '#fff',
    padding: '6px 16px',
    borderRadius: '4px',
    fontSize: '13px',
    cursor: 'pointer',
    flexShrink: 0
  }}>
    查看往日
  </button>
</div>

{/* 日期选择栏 */}
<div style={{
  display: 'flex', 
  justifyContent: 'space-between', 
  alignItems: 'center', 
  marginBottom: '10px',
  borderBottom: '1px solid #eee',
  paddingBottom: '10px'
}}>
  <div style={{fontWeight: '500', fontSize: '16px'}}>
    2025年12月15日
    <div style={{height: '3px', width: '100%', backgroundColor: '#f44336', marginTop: '8px'}}></div>
  </div>
  <div style={{display: 'flex', gap: '8px'}}>
    {/* 下载/分享图标占位 */}
    <div style={{padding: '6px', border: '1px solid #eee', borderRadius: '6px', cursor: 'pointer', color: '#666'}}>☁️</div>
    <div style={{padding: '6px', border: '1px solid #eee', borderRadius: '6px', cursor: 'pointer', color: '#666'}}>📤</div>
  </div>
</div>

{/* 农历信息框 */}
<div style={{
  backgroundColor: '#f5f7fa',
  padding: '20px',
  borderRadius: '8px',
  marginBottom: '30px',
  color: '#333',
  fontSize: '15px'
}}>
  今天是2025年12月15日 星期一， 农历二〇二五年十月廿六。
</div>

{/* 内容主体 */}

### 今日简报 · AI

<div style={{display: 'flex', gap: '8px', marginBottom: '20px'}}>
  <span style={{background: '#000', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '12px'}}>早报</span>
  <span style={{background: '#eee', color: '#666', padding: '2px 8px', borderRadius: '4px', fontSize: '12px'}}>晚报</span>
</div>

{/* 使用标准 Markdown 列表，配合 CSS 样式调整 */}
<div className="news-list" style={{lineHeight: '2'}}>

<!-- 1. **澳大利亚邦迪海滩发生枪击事件**：该事件已造成至少12人死亡，警方称此事件可能为恐怖袭击。

2. **悉尼枪击事件现场视频曝光**：居民描述听到数十声枪响，现场一片混乱。

3. **泽连斯基放弃加入北约**：乌克兰总统在讲话中表示，和平计划必然包含一些妥协。

4. **美媒称美国头号敌人是自身债务**：经济问题成为美国当前最大的隐忧。

5. **张本智和夺得WTT总决赛男单冠军**：在决赛中以4比2战胜对手，表现出色。

6. **王曼昱卫冕WTT总决赛女单冠军**：她在总决赛中取得佳绩，荣获奖金56万。

7. **澳总理：枪击案是针对犹太人的恐袭**：此言论引发社会广泛关注。 -->

</div>