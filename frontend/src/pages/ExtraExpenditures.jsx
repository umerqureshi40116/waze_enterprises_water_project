import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Trash2, Download, FileDown, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { formatCurrency, formatCurrencySimple } from '../utils/currency';
import { generateExpenseId } from '../utils/idGenerator';
import Pagination from '../components/Pagination';

const ExtraExpenditures = () => {
  const { user } = useAuth();
  const [expenditures, setExpenditures] = useState([]);
  const [filteredExpenditures, setFilteredExpenditures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExpenditures, setSelectedExpenditures] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Helper function to get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const [formData, setFormData] = useState({
    id: '',
    expense_type: '',
    description: '',
    amount: '',
    date: getTodayDate(),
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  // Filter expenditures based on search
  useEffect(() => {
    let filtered = expenditures;

    if (searchTerm) {
      filtered = filtered.filter(e =>
        e.expense_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredExpenditures(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchTerm, expenditures]);

  const fetchData = async () => {
    try {
      const response = await api.get('/extra-expenditures/');
      setExpenditures(Array.isArray(response.data) ? response.data : []);
      setFilteredExpenditures(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to fetch data');
      setExpenditures([]);
      setFilteredExpenditures([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        amount: parseFloat(formData.amount)
      };

      if (editMode) {
        await api.put(`/extra-expenditures/${formData.id}`, submitData);
        toast.success('Expenditure updated successfully');
      } else {
        const newExpense = { ...submitData, id: await generateExpenseId() };
        await api.post('/extra-expenditures/', newExpense);
        toast.success('Expenditure recorded successfully');
      }
      setShowModal(false);
      fetchData();
      resetForm();
    } catch (error) {
      const msg = error.response?.data?.detail || `Failed to ${editMode ? 'update' : 'record'} expenditure`;
      toast.error(msg);
    }
  };

  const handleDelete = async (expenseId) => {
    if (!window.confirm('Are you sure you want to delete this expenditure record?')) return;

    try {
      await api.delete(`/extra-expenditures/${expenseId}`);
      toast.success('Expenditure deleted successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete expenditure');
    }
  };

  const handleEditExpenditure = (expenditure) => {
    setFormData({
      id: expenditure.id,
      expense_type: expenditure.expense_type,
      description: expenditure.description,
      amount: expenditure.amount,
      date: expenditure.date,
      notes: expenditure.notes || ''
    });
    setEditMode(true);
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      id: '',
      expense_type: '',
      description: '',
      amount: '',
      date: getTodayDate(),
      notes: ''
    });
    setEditMode(false);
  };

  const downloadExcelAll = async () => {
    try {
      const response = await api.get('/extra-expenditures/export/excel', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `extra-expenditures-all-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Excel file downloaded successfully');
    } catch (error) {
      toast.error('Failed to download Excel file');
    }
  };

  const downloadExcelSelected = async () => {
    if (selectedExpenditures.length === 0) {
      toast.error('Please select at least one expenditure');
      return;
    }
    try {
      const expenseIds = selectedExpenditures.join(',');
      const response = await api.get(`/extra-expenditures/export/excel?expense_ids=${expenseIds}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `extra-expenditures-selected-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Excel file downloaded successfully');
    } catch (error) {
      toast.error('Failed to download Excel file');
    }
  };

  // Download single expenditure as PDF
  const downloadExpenditurePDF = async (expenditure_id) => {
    try {
      const response = await api.get(`/extra-expenditures/pdf/${expenditure_id}`, {
        responseType: 'blob',
      });
      // Check if response is valid PDF
      if (response.data && response.data.size > 0) {
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `expense_record_${expenditure_id}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        // Delay revokeObjectURL to allow download to complete
        setTimeout(() => window.URL.revokeObjectURL(url), 100);
        toast.success('Expense record downloading...');
      } else {
        toast.error('Invalid PDF response');
      }
    } catch (error) {
      console.error('Download error:', error);
      // Check if it's a network error vs actual failure
      if (error.response && error.response.status >= 400) {
        toast.error('Failed to download expense record');
      }
      // Otherwise assume download initiated (IDM may have intercepted)
    }
  };

  // Download selected expenditures as PDFs
  const downloadSelectedExpenditurePDF = async () => {
    if (selectedExpenditures.length === 0) {
      toast.error('Please select at least one expenditure');
      return;
    }
    let successCount = 0;
    let failureCount = 0;
    
    for (const expenditureId of selectedExpenditures) {
      try {
        const response = await api.get(`/extra-expenditures/pdf/${expenditureId}`, {
          responseType: 'blob',
        });
        // Check if response is valid PDF
        if (response.data && response.data.size > 0) {
          const url = window.URL.createObjectURL(response.data);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `expense_record_${expenditureId}.pdf`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          // Delay revokeObjectURL to allow download to complete
          setTimeout(() => window.URL.revokeObjectURL(url), 100);
          successCount++;
        } else {
          failureCount++;
        }
      } catch (error) {
        console.error(`Download error for expenditure ${expenditureId}:`, error);
        // Only count as failure if it's an actual HTTP error
        if (error.response && error.response.status >= 400) {
          failureCount++;
        } else {
          // Assume download initiated (IDM may have intercepted)
          successCount++;
        }
      }
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    // Show appropriate message
    if (successCount > 0 && failureCount === 0) {
      toast.success(`Downloading ${successCount} expense record(s)...`);
    } else if (successCount > 0) {
      toast.warning(`Downloaded ${successCount}, failed ${failureCount}`);
    } else {
      toast.error('Failed to download expense records');
    }
  };

  const totalAmount = filteredExpenditures.reduce((sum, exp) => sum + parseFloat(exp.amount || 0), 0);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Operating Expenses</h1>
          <p className="text-gray-600 mt-2">Track additional expenses like lunch, electricity bills, etc.</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={downloadExcelAll}
            className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300"
            title="Download all expenditures as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel All
          </button>
          <button
            onClick={downloadExcelSelected}
            disabled={selectedExpenditures.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedExpenditures.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300'
            }`}
            title="Download selected expenditures as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel Selected
          </button>
          <button
            onClick={() => downloadSelectedExpenditurePDF()}
            disabled={selectedExpenditures.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedExpenditures.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:text-blue-800 border border-blue-300'
            }`}
            title="Download selected expenditures as PDF"
          >
            <FileDown className="w-4 h-4" /> PDF Selected
          </button>
          <button
            onClick={() => { setShowModal(true); resetForm(); }}
            className="btn btn-primary flex items-center gap-2 ml-auto"
          >
            <Plus className="w-5 h-5" /> New Expenditure
          </button>
        </div>
      </div>

      <div className="card">
        {/* Search Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🔍 Search
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by type, description, or ID..."
            className="input w-full"
          />
        </div>

        {/* Summary */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Total Expenditures</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalAmount)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Records</p>
              <p className="text-2xl font-bold text-gray-900">{filteredExpenditures.length}</p>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell w-10">
                  <input
                    type="checkbox"
                    checked={selectedExpenditures.length === filteredExpenditures.length && filteredExpenditures.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedExpenditures(filteredExpenditures.map(e => e.id));
                      } else {
                        setSelectedExpenditures([]);
                      }
                    }}
                    className="w-4 h-4"
                  />
                </th>
                <th className="table-header-cell">Expense ID</th>
                <th className="table-header-cell">Type</th>
                <th className="table-header-cell">Description</th>
                <th className="table-header-cell">Amount</th>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Notes</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {filteredExpenditures
                .slice((currentPage - 1) * pageSize, currentPage * pageSize)
                .map((expenditure) => (
                <tr key={expenditure.id}>
                  <td className="table-cell w-10">
                    <input
                      type="checkbox"
                      checked={selectedExpenditures.includes(expenditure.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedExpenditures([...selectedExpenditures, expenditure.id]);
                        } else {
                          setSelectedExpenditures(selectedExpenditures.filter(id => id !== expenditure.id));
                        }
                      }}
                      className="w-4 h-4"
                    />
                  </td>
                  <td className="table-cell font-mono text-sm">{expenditure.id}</td>
                  <td className="table-cell">
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded">
                      {expenditure.expense_type}
                    </span>
                  </td>
                  <td className="table-cell">{expenditure.description}</td>
                  <td className="table-cell font-semibold text-red-600">Rs {formatCurrencySimple(expenditure.amount)}</td>
                  <td className="table-cell">{new Date(expenditure.date).toLocaleDateString()}</td>
                  <td className="table-cell text-sm text-gray-600">{expenditure.notes}</td>
                  <td className="table-cell">
                    <div className="flex gap-2">
                      <button onClick={() => downloadExpenditurePDF(expenditure.id)} className="text-blue-600 hover:text-blue-800" title="Download PDF">
                        📥
                      </button>
                      {user?.role === 'admin' && (
                        <>
                          <button
                            onClick={() => handleEditExpenditure(expenditure)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Edit"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(expenditure.id)}
                            className="text-red-600 hover:text-red-800"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(filteredExpenditures.length / pageSize)}
          onPageChange={setCurrentPage}
          pageSize={pageSize}
          onPageSizeChange={setPageSize}
          totalRecords={filteredExpenditures.length}
        />

        {filteredExpenditures.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No expenditures found</p>
          </div>
        )}
      </div>

      {/* Slide-out Panel for Form */}
      {showModal && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 bg-black bg-opacity-30 z-40 transition-opacity"
            onClick={() => { setShowModal(false); resetForm(); }}
          />

          {/* Slide-out Panel */}
          <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl z-50 overflow-y-auto transform transition-transform duration-300 ease-out">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">{editMode ? 'Edit Expenditure' : 'New Expenditure'}</h2>
              <button
                onClick={() => { setShowModal(false); resetForm(); }}
                className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>

            {/* Form Content */}
            <div className="px-6 py-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Expense ID</label>
                  <input
                    type="text"
                    value={formData.id}
                    className="input bg-gray-50"
                    disabled
                  />
                  <p className="text-xs text-gray-500 mt-1">Auto-generated</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Expense Type *</label>
                  <input
                    type="text"
                    value={formData.expense_type}
                    onChange={(e) => setFormData({ ...formData, expense_type: e.target.value })}
                    placeholder="e.g., Lunch, Electricity Bill, Office Supplies..."
                    className="input"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Enter the type of expense manually</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Detailed description of the expense..."
                    className="input"
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amount (PKR) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    placeholder="Enter amount..."
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    placeholder="Additional notes..."
                    className="input"
                    rows="2"
                  />
                </div>

                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn btn-primary flex-1">
                    {editMode ? 'Update Expenditure' : 'Record Expenditure'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowModal(false); resetForm(); }}
                    className="btn btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ExtraExpenditures;
