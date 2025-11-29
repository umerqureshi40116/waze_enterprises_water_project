import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Download, FileDown, Calendar, Users, Building2 } from 'lucide-react';
import { formatCurrency, formatCurrencySimple, formatDate } from '../utils/currency';

const Ledger = () => {
  const [partyType, setPartyType] = useState('customer'); // 'customer' or 'supplier'
  const [parties, setParties] = useState([]);
  const [selectedParty, setSelectedParty] = useState('');
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [ledgerData, setLedgerData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch parties when partyType changes
  useEffect(() => {
    fetchParties();
  }, [partyType]);

  const fetchParties = async () => {
    try {
      setLoading(true);
      const endpoint = partyType === 'customer' ? '/customers' : '/suppliers';
      const res = await api.get(endpoint);
      setParties(res.data);
      setSelectedParty('');
      setLedgerData(null);
    } catch (error) {
      toast.error(`Failed to fetch ${partyType}s`);
    } finally {
      setLoading(false);
    }
  };

  const fetchLedger = async (e) => {
    e.preventDefault();
    if (!selectedParty) {
      toast.error(`Please select a ${partyType}`);
      return;
    }

    try {
      setLoading(true);
      const endpoint = partyType === 'customer' 
        ? `/reports/ledger/customer/${selectedParty}`
        : `/reports/ledger/supplier/${selectedParty}`;
      
      const res = await api.get(endpoint, {
        params: { year: selectedYear, month: selectedMonth }
      });
      
      setLedgerData(res.data);
      toast.success('Ledger loaded successfully');
    } catch (error) {
      toast.error('Failed to load ledger');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    if (!selectedParty) {
      toast.error(`Please select a ${partyType}`);
      return;
    }

    try {
      const endpoint = partyType === 'customer'
        ? `/reports/ledger/customer/${selectedParty}/pdf`
        : `/reports/ledger/supplier/${selectedParty}/pdf`;
      
      const res = await api.get(endpoint, {
        params: { year: selectedYear, month: selectedMonth },
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(res.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ledger_${selectedParty}_${selectedYear}_${selectedMonth}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
      console.error(error);
    }
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

  if (loading && !ledgerData) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-4 text-gray-700 font-medium">Loading ledger data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Account Ledger</h1>
          <p className="text-gray-600 mt-1">View detailed transaction history for customers and suppliers</p>
        </div>
        {ledgerData && (
          <button
            onClick={downloadPDF}
            className="btn btn-primary flex items-center gap-2"
          >
            <Download className="w-4 h-4" /> Download PDF
          </button>
        )}
      </div>

      {/* Filter Form */}
      <div className="card">
        <form onSubmit={fetchLedger} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Party Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">📋 Select Type</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value="customer"
                    checked={partyType === 'customer'}
                    onChange={(e) => setPartyType(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">👤 Customer</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value="supplier"
                    checked={partyType === 'supplier'}
                    onChange={(e) => setPartyType(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">🏢 Supplier</span>
                </label>
              </div>
            </div>

            {/* Party Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {partyType === 'customer' ? '👤 Customer' : '🏢 Supplier'}
              </label>
              <select
                value={selectedParty}
                onChange={(e) => setSelectedParty(e.target.value)}
                className="input w-full"
              >
                <option value="">Select {partyType === 'customer' ? 'Customer' : 'Supplier'}...</option>
                {parties.map((party) => (
                  <option key={party.id} value={party.id}>
                    {party.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Month Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">📅 Month</label>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                className="input w-full"
              >
                {months.map((month, index) => (
                  <option key={index} value={index + 1}>
                    {month}
                  </option>
                ))}
              </select>
            </div>

            {/* Year Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">📆 Year</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                className="input w-full"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary flex items-center gap-2"
            >
              <Calendar className="w-4 h-4" />
              {loading ? 'Loading...' : 'Generate Report'}
            </button>
          </div>
        </form>
      </div>

      {/* Ledger Display */}
      {ledgerData && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
              <p className="text-sm text-blue-600 font-medium">Opening Balance</p>
              <p className="text-2xl font-bold text-blue-900 mt-2">
                Rs {formatCurrencySimple(ledgerData.opening_balance)}
              </p>
            </div>
            <div className="card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
              <p className="text-sm text-green-600 font-medium">Total Debit</p>
              <p className="text-2xl font-bold text-green-900 mt-2">
                Rs {formatCurrencySimple(ledgerData.total_debit)}
              </p>
            </div>
            <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
              <p className="text-sm text-orange-600 font-medium">Total Credit</p>
              <p className="text-2xl font-bold text-orange-900 mt-2">
                Rs {formatCurrencySimple(ledgerData.total_credit)}
              </p>
            </div>
            <div className="card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
              <p className="text-sm text-purple-600 font-medium">Closing Balance</p>
              <p className="text-2xl font-bold text-purple-900 mt-2">
                Rs {formatCurrencySimple(ledgerData.closing_balance)}
              </p>
            </div>
          </div>

          {/* Party Info Card */}
          <div className="card border-l-4 border-primary-500 bg-blue-50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Party Name</p>
                <p className="font-semibold text-gray-900">{ledgerData.party_name}</p>
              </div>
              <div>
                <p className="text-gray-600">Party Type</p>
                <p className="font-semibold text-gray-900">{ledgerData.party_type === 'customer' ? '👤 Customer' : '🏢 Supplier'}</p>
              </div>
              <div>
                <p className="text-gray-600">Period</p>
                <p className="font-semibold text-gray-900">{months[ledgerData.month - 1]} {ledgerData.year}</p>
              </div>
            </div>
          </div>

          {/* Transactions Table */}
          <div className="card">
            <div className="mb-4 text-sm text-gray-600">
              Showing <span className="font-semibold">{ledgerData.transactions?.length || 0}</span> transaction(s)
            </div>
            <div className="table-container overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['Date', 'Reference', 'Description', 'Debit', 'Credit', 'Balance', 'Status'].map(header => (
                      <th
                        key={header}
                        scope="col"
                        className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {ledgerData.transactions && ledgerData.transactions.length > 0 ? (
                    ledgerData.transactions.map((transaction, index) => (
                      <tr key={index} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-2 text-sm text-gray-900">
                          {formatDate(transaction.date)}
                        </td>
                        <td className="px-4 py-2 text-sm font-mono text-gray-700 bg-gray-50">
                          {transaction.reference_number}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-900">
                          {transaction.description}
                        </td>
                        <td className="px-4 py-2 text-sm text-right">
                          {transaction.debit > 0 ? (
                            <span className="font-semibold text-red-600">
                              Rs {formatCurrencySimple(transaction.debit)}
                            </span>
                          ) : (
                            <span className="text-gray-400">–</span>
                          )}
                        </td>
                        <td className="px-4 py-2 text-sm text-right">
                          {transaction.credit > 0 ? (
                            <span className="font-semibold text-green-600">
                              Rs {formatCurrencySimple(transaction.credit)}
                            </span>
                          ) : (
                            <span className="text-gray-400">–</span>
                          )}
                        </td>
                        <td className="px-4 py-2 text-sm text-right font-bold text-gray-900">
                          Rs {formatCurrencySimple(transaction.balance)}
                        </td>
                        <td className="px-4 py-2 text-sm text-center">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            transaction.payment_status === 'paid'
                              ? 'bg-green-100 text-green-800'
                              : transaction.payment_status === 'partial'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {transaction.payment_status === 'paid' && '✅ Paid'}
                            {transaction.payment_status === 'partial' && '🌓 Partial'}
                            {transaction.payment_status === 'pending' && '⏳ Pending'}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="px-4 py-8 text-center text-gray-500 text-sm">
                        No transactions found for this period
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!ledgerData && (
        <div className="card text-center py-12">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2 font-medium">No ledger data loaded</p>
          <p className="text-sm text-gray-500">Select a customer/supplier and date range to generate a ledger</p>
        </div>
      )}
    </div>
  );
};

export default Ledger;
