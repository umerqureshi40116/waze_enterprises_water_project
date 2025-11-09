import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { formatCurrency } from '../utils/currency';
import { Link, useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  AlertCircle,
  CheckCircle,
  Wallet
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [monthlyStats, setMonthlyStats] = useState([]);
  const [extraExpenditures, setExtraExpenditures] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoDownloadEnabled, setAutoDownloadEnabled] = useState(() => {
    return localStorage.getItem('autoDownloadReport') === 'true';
  });



  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Auto-download daily report if enabled
  useEffect(() => {
    if (autoDownloadEnabled && summary) {
      const lastDownloadDate = localStorage.getItem('lastReportDownloadDate');
      const today = new Date().toISOString().split('T')[0];
      
      if (lastDownloadDate !== today) {
        downloadDailyReport();
        localStorage.setItem('lastReportDownloadDate', today);
      }
    }
  }, [summary, autoDownloadEnabled]);

  const fetchDashboardData = async () => {
  try {
    const [summaryRes, statsRes, expendituresRes] = await Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/stats/monthly'),
      api.get('/extra-expenditures/total').catch(() => null)
    ]);
    
    setSummary(summaryRes.data);
    setMonthlyStats(Array.isArray(statsRes.data) ? statsRes.data : statsRes.data?.data || []);
    setExtraExpenditures(expendituresRes?.data || { total_amount: 0, count: 0 });
  } catch (error) {
    console.error('Dashboard fetch error:', error);
    toast.error('Failed to fetch dashboard data');
    setMonthlyStats([]);
  } finally {
    setLoading(false);
  }
  };

  const downloadDailyReport = async () => {
    try {
      const response = await api.get('/reports/export-excel', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date().toISOString().split('T')[0];
      link.setAttribute('download', `daily-report-${today}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      if (!autoDownloadEnabled) {
        toast.success('Daily report downloaded!');
      }
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download daily report');
    }
  };

  const toggleAutoDownload = () => {
    const newValue = !autoDownloadEnabled;
    setAutoDownloadEnabled(newValue);
    localStorage.setItem('autoDownloadReport', newValue);
    toast.success(newValue ? 'Auto-download enabled!' : 'Auto-download disabled');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Sales',
      value: formatCurrency(summary?.monthly_sales),
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      show: true,
      route: '/sales'
    },
    {
      name: 'Cost of Units Sold',
      value: formatCurrency(summary?.monthly_purchases),
      icon: TrendingDown,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      show: true,
      route: '/purchases'
    },
    {
      name: 'Total Monthly Purchase Revenue',
      value: formatCurrency(summary?.total_monthly_purchase_revenue),
      icon: DollarSign,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      show: true,
      route: '/purchases'
    },
    {
      name: 'Profit of Units Sold',
      value: summary?.monthly_profit !== null ? formatCurrency(summary?.monthly_profit) : 'N/A',
      icon: DollarSign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      show: user?.role === 'admin',
      route: '/reports'
    },
    {
      name: 'Total Stock Items',
      value: summary?.total_stock_items || 0,
      icon: Package,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      show: true,
      route: '/stock'
    },
    {
      name: 'Receivables',
      value: formatCurrency(summary?.pending_purchase_payments),
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      show: true,
      route: '/purchases'
    },
    {
      name: 'Payables',
      value: formatCurrency(summary?.pending_sale_payments),
      icon: CheckCircle,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100',
      show: true,
      route: '/sales'
    },
    {
      name: 'Operating Expenses',
      value: formatCurrency(extraExpenditures?.total_amount || 0),
      icon: Wallet,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100',
      show: true,
      route: '/extra-expenditures'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back, {user?.username}!</p>
      </div>

      {/* Report Download Section */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">📊 Daily Report</h3>
            <p className="text-sm text-gray-600 mt-1">
              {autoDownloadEnabled 
                ? '✅ Auto-download enabled - Report downloads daily at page load' 
                : 'Download your daily business report as Excel file'}
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={downloadDailyReport}
              className="btn btn-primary flex items-center gap-2"
              title="Download today's report"
            >
              📥 Download Now
            </button>
            <button
              onClick={toggleAutoDownload}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                autoDownloadEnabled
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-gray-300 hover:bg-gray-400 text-gray-900'
              }`}
              title={autoDownloadEnabled ? 'Disable auto-download' : 'Enable auto-download'}
            >
              {autoDownloadEnabled ? '✓ Auto' : '○ Auto'}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.filter(stat => stat.show).map((stat) => {
          const Icon = stat.icon;
          return (
            <button
              key={stat.name}
              onClick={() => navigate(stat.route)}
              className="card hover:shadow-lg transition-all hover:scale-105 cursor-pointer text-left bg-white border-0"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.bgColor} p-3 rounded-full`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Chart */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Sales vs Purchases (Last 6 Months)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis type="number" domain={[25000, 300000]} tickCount={8} tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`} />
            <Tooltip 
              labelFormatter={(label) => label} 
              formatter={(value) => `Rs ${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
              contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #d1d5db' }} 
            />
            <Legend />
            <Line type="monotone" dataKey="sales" stroke="#10b981" strokeWidth={2} name="Sales" />
            <Line type="monotone" dataKey="purchases" stroke="#ef4444" strokeWidth={2} name="Purchases" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/purchases"
            className="btn btn-primary text-center py-4 hover:shadow-lg transition-all"
            title="Add new purchase from supplier"
          >
            📦 New Purchase
          </Link>
          <Link
            to="/sales"
            className="btn btn-primary text-center py-4 hover:shadow-lg transition-all"
            title="Sell products to customers"
          >
            🛒 New Sale
          </Link>
          <Link
            to="/blow-process"
            className="btn btn-primary text-center py-4 hover:shadow-lg transition-all"
            title="Process raw material into finished bottles"
          >
            ⚙️ Blow Process
          </Link>
          <Link
            to="/stock"
            className="btn btn-primary text-center py-4 hover:shadow-lg transition-all"
            title="Check current inventory levels"
          >
            📊 View Stock
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
