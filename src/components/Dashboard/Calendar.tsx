import React, { useState } from 'react';
import styles from './styles.module.css';

export default function CalendarWidget() {
  const [currentMonth, setCurrentMonth] = useState(new Date(2026, 0, 1)); // Mock 2026 Jan
  const [selectedDate, setSelectedDate] = useState<number | null>(23); // Mock selection

  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();
  
  const days = [];
  for (let i = 0; i < firstDay; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  // Mock data availability: 23 (blue), 17 (dark)
  const availableDays = [2, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 19, 20, 21, 22, 23, 24];

  return (
    <div className={styles.calendarWidget}>
        <div className={styles.calendarHeader}>
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))}>‹</button>
            <span>{currentMonth.getFullYear()}年 {currentMonth.getMonth() + 1}月</span>
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))}>›</button>
        </div>
        <div className={styles.calendarGrid}>
            {['日','一','二','三','四','五','六'].map(d => (
                <div key={d} className={styles.calendarDayHeader}>{d}</div>
            ))}
            {days.map((d, i) => {
                if (!d) return <div key={i} className={styles.calendarDay}></div>;
                const hasData = availableDays.includes(d);
                const isSelected = selectedDate === d;
                
                // Hardcoded style for 17 to match screenshot (dark blue/black)
                const isDark = d === 17;

                return (
                    <div 
                        key={i} 
                        className={`${styles.calendarDay} ${hasData ? styles.hasData : ''}`}
                        style={{ 
                            backgroundColor: isSelected ? '#2563eb' : (isDark ? '#1f2937' : undefined), 
                            color: (isSelected || isDark) ? 'white' : undefined 
                        }}
                    >
                        {d}
                    </div>
                );
            })}
        </div>
        <button className={styles.calendarAllBtn}>显示全部 Paper</button>
    </div>
  );
}
