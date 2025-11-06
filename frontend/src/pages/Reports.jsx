import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { formatCurrency, formatDate } from '../utils/currency';
import { DollarSign, TrendingUp, TrendingDown, FileText, Download, Calendar } from 'lucide-react';

const Reports = () => {
  const [profitReport, setProfitReport] = useState(null);
  const [balanceSheet, setBalanceSheet] = useState(null);
  const [weeklyReports, setWeeklyReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [downloadingDaily, setDownloadingDaily] = useState(false);

  useEffect(() => {
    fetchReports();
  }, [selectedMonth, selectedYear]);

  const fetchReports = async () => {
    try {
      const [profitRes, balanceRes, weeklyRes] = await Promise.all([
        api.get(`/reports/profit?month=${selectedMonth}&year=${selectedYear}`),
        api.get('/reports/balance-sheet'),
        api.get('/reports/weekly-reports?limit=12')
      ]);
      setProfitReport(profitRes.data);
      setBalanceSheet(balanceRes.data);
      setWeeklyReports(weeklyRes.data.reports || []);
    } catch (error) {
      toast.error('Failed to fetch reports');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      setExporting(true);
      const response = await api.get('/reports/export-excel', {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `weekly-report-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      
      toast.success('Report exported successfully!');
    } catch (error) {
      toast.error('Failed to export report');
      console.error(error);
    } finally {
      setExporting(false);
    }
  };

  const handleGenerateWeekly = async () => {
    try {
      setLoading(true);
      await api.post('/reports/generate-weekly');
      toast.success('Weekly report generated successfully!');
      fetchReports();
    } catch (error) {
      toast.error('Failed to generate weekly report');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadWeeklyReport = async (weekOffset) => {
    try {
      const response = await api.get(`/reports/export-excel?week_offset=${weekOffset}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const fileName = `weekly-report-${new Date(Date.now() + weekOffset * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}.xlsx`;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      
      toast.success('Report downloaded!');
    } catch (error) {
      toast.error('Failed to download report');
      console.error(error);
    }
  };

  const downloadDailyReport = async () => {
    try {
      setDownloadingDaily(true);
      const response = await api.get(`/reports/export-excel?date=${selectedDate}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `daily-report-${selectedDate}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      
      toast.success(`Daily report for ${selectedDate} downloaded!`);
    } catch (error) {
      toast.error('Failed to download daily report');
      console.error(error);
    } finally {
      setDownloadingDaily(false);
    }
  };

  if (loading && !profitReport) {
    return <div className="flex justify-center items-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-2">Financial reports and analytics (Admin Only)</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => {
              setSelectedMonth(new Date().getMonth() + 1);
              setSelectedYear(new Date().getFullYear());
              setSelectedDate(new Date().toISOString().split('T')[0]);
            }}
            className="btn btn-secondary flex items-center gap-2"
            disabled={loading}
          >
            🔄 Reset
          </button>
          <button 
            onClick={handleGenerateWeekly}
            className="btn btn-secondary flex items-center gap-2"
            disabled={loading}
          >
            <Calendar className="w-5 h-5" /> Generate Weekly
          </button>
          <button 
            onClick={handleExportExcel}
            className="btn btn-primary flex items-center gap-2"
            disabled={exporting || loading}
          >
            <Download className="w-5 h-5" /> {exporting ? 'Exporting...' : 'Export Excel'}
          </button>
        </div>
      </div>

      {/* Month/Year Selector */}
      <div className="card">
        <div className="flex gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Month</label>
            <select value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} className="input">
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>{new Date(2000, i).toLocaleString('default', { month: 'long' })}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
            <select value={selectedYear} onChange={(e) => setSelectedYear(e.target.value)} className="input">
              {[2023, 2024, 2025].map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Daily Report Download */}
      <div className="card bg-gradient-to-r from-indigo-50 to-blue-50 border-2 border-indigo-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              Download Daily Report
            </h3>
            <p className="text-sm text-gray-600 mt-1">Generate and download a complete report for a specific date</p>
          </div>
          <div className="flex gap-3 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Date</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input"
              />
            </div>
            <button
              onClick={downloadDailyReport}
              disabled={downloadingDaily}
              className="btn btn-primary flex items-center gap-2"
              title="Download report for selected date"
            >
              <Download className="w-5 h-5" />
              {downloadingDaily ? 'Downloading...' : 'Download Daily Report'}
            </button>
          </div>
        </div>
      </div>

      {/* Profit Report */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <DollarSign className="w-6 h-6" />
          Profit & Loss Statement
        </h2>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center py-3 border-b">
            <span className="font-medium text-gray-700">Sales Revenue</span>
            <span className="text-green-600 font-bold">{formatCurrency(profitReport?.sales_revenue)}</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b">
            <span className="font-medium text-gray-700">Waste Recovery</span>
            <span className="text-green-600 font-bold">{formatCurrency(profitReport?.waste_recovery)}</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b border-green-500">
            <span className="font-bold text-gray-900">Total Revenue</span>
            <span className="text-green-600 font-bold text-xl">{formatCurrency(profitReport?.total_revenue)}</span>
          </div>

          <div className="flex justify-between items-center py-3 border-b mt-6">
            <span className="font-medium text-gray-700">Purchase Costs</span>
            <span className="text-red-600 font-bold">{formatCurrency(profitReport?.purchase_costs)}</span>
          </div>
          <div className="flex justify-between items-center py-3 border-b border-red-500">
            <span className="font-bold text-gray-900">Total Costs</span>
            <span className="text-red-600 font-bold text-xl">{formatCurrency(profitReport?.total_costs)}</span>
          </div>
          
          <div className={`flex justify-between items-center py-4 mt-6 rounded-lg px-4 ${
            profitReport?.profit >= 0 ? 'bg-green-50' : 'bg-red-50'
          }`}>
            <span className="font-bold text-gray-900 text-lg">Net Profit</span>
            <div className="text-right">
              <span className={`font-bold text-2xl ${profitReport?.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(Math.abs(profitReport?.profit || 0))}
              </span>
              <p className="text-sm text-gray-600 mt-1">Margin: {profitReport?.profit_margin?.toFixed(2)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Balance Sheet */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <FileText className="w-6 h-6" />
          Balance Sheet
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Assets</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-gray-700">Accounts Receivable</span>
                <span className="font-bold text-green-600">{formatCurrency(balanceSheet?.accounts_receivable)}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-gray-700">Total Sales (All Time)</span>
                <span className="font-bold text-green-600">{formatCurrency(balanceSheet?.total_sales)}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Liabilities</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-gray-700">Accounts Payable</span>
                <span className="font-bold text-red-600">{formatCurrency(balanceSheet?.accounts_payable)}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-gray-700">Total Purchases (All Time)</span>
                <span className="font-bold text-red-600">{formatCurrency(balanceSheet?.total_purchases)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t-2 border-gray-300">
          <div className="flex justify-between items-center">
            <span className="text-xl font-bold text-gray-900">Net Position</span>
            <span className={`text-2xl font-bold ${
              balanceSheet?.net_position >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(balanceSheet?.net_position)}
            </span>
          </div>
        </div>
      </div>

      {/* Weekly Reports History */}
      {weeklyReports.length > 0 && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Calendar className="w-6 h-6" />
            Weekly Reports History
          </h2>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Week</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900">Revenue</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900">Profit</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900">Margin</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Transactions</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Action</th>
                </tr>
              </thead>
              <tbody>
                {weeklyReports.map((report, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="text-sm">
                        <p className="font-medium text-gray-900">
                          Week {report.week_number}, {report.year}
                        </p>
                        <p className="text-gray-600 text-xs">
                          {formatDate(report.week_start)} - {formatDate(report.week_end)}
                        </p>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="font-semibold text-green-600">{formatCurrency(report.revenue)}</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold ${report.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(report.profit)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold ${report.margin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {report.margin.toFixed(2)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center text-gray-900 font-medium">
                      {report.transactions}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => downloadWeeklyReport(0 - idx)}
                        className="text-blue-600 hover:text-blue-900 font-medium text-sm flex items-center justify-center gap-1"
                      >
                        <Download className="w-4 h-4" /> Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
