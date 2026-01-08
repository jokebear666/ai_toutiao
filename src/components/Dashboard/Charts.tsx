import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';

export const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6366f1'];

// Donut Chart
const pieData = [
  { name: 'Robotiss', value: 60 },
  { name: 'Currn', value: 206 },
  { name: 'Carm', value: 30 },
  { name: 'Csurm', value: 20 },
];

export const DonutChart = () => (
  <ResponsiveContainer width="100%" height={180}>
    <PieChart>
      <Pie
        data={pieData}
        cx="50%"
        cy="50%"
        innerRadius={50}
        outerRadius={70}
        fill="#8884d8"
        paddingAngle={2}
        dataKey="value"
      >
        {pieData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  </ResponsiveContainer>
);

// Line Chart
const lineData = [
  { day: '0', count: 10 },
  { day: '5', count: 32 },
  { day: '10', count: 45 },
  { day: '15', count: 50 },
  { day: '20', count: 60 },
  { day: '25', count: 75 },
  { day: '30', count: 80 },
];

export const TrendChart = () => (
  <ResponsiveContainer width="100%" height={180}>
    <LineChart data={lineData} margin={{top: 20, right: 10, left: 0, bottom: 0}}>
      <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#9ca3af'}} />
      <YAxis hide />
      <Tooltip />
      <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={3} dot={{r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff'}} />
    </LineChart>
  </ResponsiveContainer>
);

// Bar Chart
const barData = [
  { name: '0', cv: 20 },
  { name: '1', cv: 28 },
  { name: '5', cv: 18 },
  { name: '10', cv: 25 },
  { name: '15', cv: 22 },
  { name: '20', cv: 38 },
  { name: '25', cv: 28 },
  { name: '30', cv: 20 },
  { name: '35', cv: 28 },
  { name: '40', cv: 32 },
  { name: '45', cv: 26 },
];

export const ComparisonChart = () => (
  <ResponsiveContainer width="100%" height={180}>
    <BarChart data={barData} barGap={4} margin={{top: 20, right: 0, left: 0, bottom: 0}}>
      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#9ca3af'}} />
      <YAxis hide />
      <Tooltip />
      <Bar dataKey="cv" fill="#93c5fd" radius={[4, 4, 0, 0]} barSize={12} />
    </BarChart>
  </ResponsiveContainer>
);
