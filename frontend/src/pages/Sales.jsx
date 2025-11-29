import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Download, FileDown, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { formatCurrency, formatCurrencySimple, formatDate } from '../utils/currency';
import { generateSaleNumber } from '../utils/idGenerator';
import Pagination from '../components/Pagination';
import LineItemsForm from '../components/LineItemsForm';

const Sales = () => {
  const { user } = useAuth();
  const [sales, setSales] = useState([]);
  const [filteredSales, setFilteredSales] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCustomer, setFilterCustomer] = useState('');
  const [filterPaymentStatus, setFilterPaymentStatus] = useState('');
  const [filterPaymentMethod, setFilterPaymentMethod] = useState('');
  const [selectedBills, setSelectedBills] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');

  // Helper function to get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const [formData, setFormData] = useState({
    bill_number: '',
    customer_id: '',
    line_items: [],  // CHANGED: Now array of items
    due_date: getTodayDate(),
    payment_status: 'paid',
    payment_method: '',
    notes: ''
  });

  // Initialize the bill number on component mount and when due_date changes
  useEffect(() => {
    const initializeBillNumber = async () => {
      const billNumber = await generateSaleNumber(formData.due_date);
      setFormData(prev => ({ ...prev, bill_number: billNumber }));
    };
    initializeBillNumber();
  }, [formData.due_date]);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);

      const token = localStorage.getItem("token");
      if (!token) {
        console.log("No token found, redirecting to login");
        window.location.href = "/login";
        return;
      }

      console.log('📡 API Base URL:', api.defaults.baseURL);
      console.log('🔑 Token present:', !!token);
      
      // Fetch each endpoint separately to see which one fails
      console.log('📡 Fetching sales...');
      const salesRes = await api.get('/sales/');
      console.log('✅ Sales fetched:', salesRes.status, salesRes.data.length, 'items');
      
      console.log('📡 Fetching customers...');
      const customersRes = await api.get('/customers/');
      console.log('✅ Customers fetched:', customersRes.status, customersRes.data.length, 'items');
      
      console.log('📡 Fetching items...');
      const itemsRes = await api.get('/stocks/items');
      console.log('✅ Items fetched:', itemsRes.status, itemsRes.data.length, 'items');
      
      // Set state
      setSales(Array.isArray(salesRes.data) ? salesRes.data : []);
      setCustomers(Array.isArray(customersRes.data) ? customersRes.data : []);
      setItems(Array.isArray(itemsRes.data) ? itemsRes.data : []);
      
      console.log('✅ State updated:');
      console.log('   Sales:', Array.isArray(salesRes.data) ? salesRes.data.length : 0);
      console.log('   Customers:', Array.isArray(customersRes.data) ? customersRes.data.length : 0);
      console.log('   Items:', Array.isArray(itemsRes.data) ? itemsRes.data.length : 0);
    } catch (error) {
      console.error('❌ Error fetching data:', error);
      console.error('📋 Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        isNetworkError: !error.response,
        errorCode: error.code
      });
      
      let errorMsg = 'Failed to fetch data';
      if (error.response) {
        errorMsg = `${error.response.status} ${error.response.statusText}`;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      toast.error(errorMsg);
      setSales([]);
      setCustomers([]);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter sales based on search term, customer, and payment status
  useEffect(() => {
    let filtered = [...sales];
    
    if (searchTerm) {
      filtered = filtered.filter(sale => 
        sale.bill_number.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (filterCustomer) {
      filtered = filtered.filter(sale => sale.customer_id === filterCustomer);
    }
    
    if (filterPaymentStatus) {
      filtered = filtered.filter(sale => sale.payment_status === filterPaymentStatus);
    }

    if (filterPaymentMethod) {
      filtered = filtered.filter(sale => sale.payment_method === filterPaymentMethod);
    }

    // Filter by date range (using due_date which is the user-selected transaction date)
    if (filterStartDate) {
      filtered = filtered.filter(sale => new Date(sale.due_date) >= new Date(filterStartDate));
    }
    if (filterEndDate) {
      filtered = filtered.filter(sale => new Date(sale.due_date) <= new Date(filterEndDate));
    }
    
    setFilteredSales(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchTerm, filterCustomer, filterPaymentStatus, filterPaymentMethod, filterStartDate, filterEndDate, sales]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (!formData.customer_id) {
        toast.error('Please select a customer');
        return;
      }
      if (!formData.line_items || formData.line_items.length === 0) {
        toast.error('Please add at least one item');
        return;
      }
      const saleData = {
        bill_number: formData.bill_number,
        customer_id: String(formData.customer_id),
        due_date: formData.due_date || getTodayDate(),
        line_items: formData.line_items.map(item => ({
          item_id: String(item.item_id),
          quantity: Number(item.quantity),
          unit_price: parseFloat(item.unit_price)
        })),
        payment_status: formData.payment_status || "pending",
        payment_method: formData.payment_method || "cash"
      };
      console.log("🧾 Sale data being sent:", saleData);
      if (editMode) {
        await api.put(`/sales/${formData.bill_number}`, saleData);
        toast.success('Sale updated successfully');
      } else {
        await api.post('/sales', saleData);
        toast.success('Sale created successfully');
      }
      setShowModal(false);
      fetchData();
      resetForm();
    } catch (error) {
      console.error('Create/Update sale error:', error);
      const detail = error.response?.data?.detail;
      let errorMsg = editMode ? "Failed to update sale" : "Failed to create sale";
      if (Array.isArray(detail)) {
        errorMsg = detail.map(d => `${d.loc?.join(' → ')}: ${d.msg}`).join(', ');
      } else if (typeof detail === 'string') {
        errorMsg = detail;
      }
      toast.error(errorMsg);
    }
  };

  const downloadSelectedPDF = async () => {
    if (!selectedBills || selectedBills.length === 0) {
      toast('No bills selected');
      return;
    }
    try {
      // Download each bill as professional Care Packages format invoice
      for (const billNumber of selectedBills) {
        const response = await api.get(`/invoices/invoice/sale/${billNumber}`, {
          responseType: 'blob'
        });

        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `invoice_${billNumber}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 300));
      }
      toast.success(`Downloaded ${selectedBills.length} invoice(s)`);
    } catch (error) {
      console.error('Download selected error:', error);
      toast.error('Failed to download selected invoices');
    }
  };

  const renderPaymentStatus = (status) => {
    switch (status) {
      case 'paid':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">✅ Paid</span>;
      case 'pending':
        return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-semibold">⏳ Pending</span>;
      case 'partial':
        return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">🌓 Partial</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-semibold">{status}</span>;
    }
  };

  const downloadSalePDF = async (bill_number) => {
  try {
    const response = await api.get(`/invoices/invoice/sale/${bill_number}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `invoice_${bill_number}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    toast.success('Invoice downloaded successfully');
  } catch (error) {
    console.error('Download error:', error);
    toast.error('Failed to download invoice.');
  }
  };

  const downloadExcelAll = async () => {
    try {
      const response = await api.get('/reports/export-sales-excel', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sales-all-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('All sales exported to Excel!');
    } catch (error) {
      toast.error('Failed to download Excel');
      console.error(error);
    }
  };

  const downloadExcelSelected = async () => {
    if (!selectedBills || selectedBills.length === 0) {
      toast.error('No sales selected');
      return;
    }
    try {
      const response = await api.get(`/reports/export-sales-excel?bill_numbers=${selectedBills.join(',')}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sales-selected-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Selected sales exported to Excel!');
    } catch (error) {
      toast.error('Failed to download Excel');
      console.error(error);
    }
  };

  const handleEditSale = (sale) => {
    setFormData({
      bill_number: sale.bill_number,
      customer_id: sale.customer_id,
      line_items: sale.line_items || [],
      due_date: sale.due_date || '',
      payment_status: sale.payment_status,
      payment_method: sale.payment_method || 'cash',
      notes: sale.notes || ''
    });
    setEditMode(true);
    setShowModal(true);
  };

  const handleDeleteSale = async (bill_number) => {
    if (!window.confirm('Are you sure you want to delete this sale? This cannot be undone.')) {
      return;
    }
    try {
      await api.delete(`/sales/${bill_number}`);
      toast.success('Sale deleted successfully');
      fetchData();
    } catch (error) {
      console.error('Delete sale error:', error);
      toast.error('Failed to delete sale');
    }
  };

  const resetForm = async () => {
    const todayDate = getTodayDate();
    const billNumber = await generateSaleNumber(todayDate);
    setFormData({
      bill_number: billNumber,
      customer_id: '',
      line_items: [],
      due_date: todayDate,
      payment_status: 'paid',
      payment_method: '',
      notes: ''
    });
    setEditMode(false);
  };

  const getCustomerName = (id) => {
    const customer = customers.find(c => c.id === id);
    return customer ? customer.name : `Customer ${id}`;
  };


  const getItemName = (id) => {
    const item = items.find(i => i.id === id);
    return item ? item.name : `Item ${id}`;
  };

  // Compute available stock for selected item and derive save-button state
  const saveDisabled = !formData.customer_id || !formData.line_items || formData.line_items.length === 0;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-4 text-gray-700 font-medium">Loading sales data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sales</h1>
          <p className="text-gray-600 mt-1">Record and manage all sales transactions</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={downloadSelectedPDF}
            disabled={selectedBills.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedBills.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:text-blue-800 border border-blue-300'
            }`}
            title="Download selected bills as combined PDF"
          >
            <Download className="w-4 h-4" /> PDF
          </button>
          <button
            onClick={downloadExcelAll}
            className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300"
            title="Download all sales as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel All
          </button>
          <button
            onClick={downloadExcelSelected}
            disabled={selectedBills.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedBills.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300'
            }`}
            title="Download selected sales as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel Selected
          </button>
          <button
            onClick={() => { setShowModal(true); resetForm(); }}
            className="btn btn-primary flex items-center gap-2 ml-auto"
          >
            <Plus className="w-5 h-5" /> New Sale
          </button>
        </div>
      </div>

      <div className="card">
        {/* Search and Filter Section */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Start Date
            </label>
            <input
              type="date"
              value={filterStartDate}
              onChange={(e) => setFilterStartDate(e.target.value)}
              className="input w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 End Date
            </label>
            <input
              type="date"
              value={filterEndDate}
              onChange={(e) => setFilterEndDate(e.target.value)}
              className="input w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              👤 Filter by Customer
            </label>
            <select
              value={filterCustomer}
              onChange={(e) => setFilterCustomer(e.target.value)}
              className="input w-full"
            >
              <option value="">All Customers</option>
              {customers.map(customer => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💳 Payment Status
            </label>
            <select
              value={filterPaymentStatus}
              onChange={(e) => setFilterPaymentStatus(e.target.value)}
              className="input w-full"
            >
              <option value="">All Status</option>
              <option value="paid">✅ Paid</option>
              <option value="pending">⏳ Pending</option>
              {/* <option value="partial">Partial</option> */}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💰 Payment Method
            </label>
            <select
              value={filterPaymentMethod}
              onChange={(e) => setFilterPaymentMethod(e.target.value)}
              className="input w-full"
            >
              <option value="">All Methods</option>
              <option value="cash">💵 Cash</option>
              <option value="allied bank">🏦 Allied Bank</option>
              <option value="easypaisa">📱 Easypaisa</option>
            </select>
          </div>
        </div>
        
        <div className="mb-4 text-sm text-gray-600">
          Showing <span className="font-semibold">{filteredSales.length}</span> of <span className="font-semibold">{sales.length}</span> sales
        </div>

        <div className="table-container overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  <input type="checkbox" checked={selectedBills.length > 0 && selectedBills.length === filteredSales.length} onChange={(e) => {
                    if (e.target.checked) setSelectedBills(filteredSales.map(s => s.bill_number));
                    else setSelectedBills([]);
                  }} />
                </th>
                  {['Bill Number','Customer','Item','Quantity','Unit Price','Total','Status','Paid Amount','Method','Date','Actions'].map(header => (
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
              {filteredSales.length === 0 ? (
                <tr>
                  <td colSpan="11" className="text-center py-8 text-gray-500 text-sm">
                    {sales.length === 0 ? (
                      <>
                        No sales records found.
                        <button
                          onClick={() => setShowModal(true)}
                          className="text-primary-600 ml-1 underline"
                        >
                          Create your first sale
                        </button>
                      </>
                    ) : (
                      'No sales match your filters. Try adjusting your search criteria.'
                    )}
                  </td>
                </tr>
              ) : (
                filteredSales
                  .slice((currentPage - 1) * pageSize, currentPage * pageSize)
                  .flatMap((sale, saleIdx) => 
                    sale.line_items && sale.line_items.length > 0
                      ? sale.line_items.map((item, itemIdx) => (
                          <tr key={`${saleIdx}-${itemIdx}`}>
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm">
                                <input type="checkbox" checked={selectedBills.includes(sale.bill_number)} onChange={(e) => {
                                  if (e.target.checked) setSelectedBills(prev => [...prev, sale.bill_number]);
                                  else setSelectedBills(prev => prev.filter(b => b !== sale.bill_number));
                                }} />
                              </td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm font-medium text-black">{sale.bill_number}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm text-black">{getCustomerName(sale.customer_id)}</td>
                            )}
                            <td className="px-4 py-2 text-sm text-black">{getItemName(item.item_id)}</td>
                            <td className="px-4 py-2 text-sm text-black">{item.quantity}</td>
                            <td className="px-4 py-2 text-sm text-black">Rs {parseFloat(item.unit_price).toLocaleString()}</td>
                            <td className="px-4 py-2 text-sm font-semibold text-green-600">Rs {(item.quantity * parseFloat(item.unit_price)).toLocaleString()}</td>
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm text-black">{renderPaymentStatus(sale.payment_status)}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm text-black">
                                {sale.payment_status === 'pending' 
                                  ? 'Rs ' + formatCurrencySimple(parseFloat(sale.total_price) - (parseFloat(sale.paid_amount) || 0)) + ' (Pending)'
                                  : sale.payment_status === 'paid' && sale.paid_amount == 0 
                                  ? 'Rs ' + formatCurrencySimple(sale.total_price)
                                  : 'Rs ' + formatCurrencySimple(sale.paid_amount)
                                }
                              </td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm text-black">{sale.payment_method || '–'}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm text-black">{formatDate(sale.due_date || sale.date)}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={sale.line_items.length} className="px-4 py-2 text-sm">
                                <div className="flex gap-2">
                                  <button onClick={() => handleEditSale(sale)} className="text-amber-600 hover:text-amber-800" title="Edit Sale">
                                    <Edit2 className="w-4 h-4" />
                                  </button>
                                  <button onClick={() => handleDeleteSale(sale.bill_number)} className="text-red-600 hover:text-red-800" title="Delete Sale">
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </td>
                            )}
                          </tr>
                        ))
                      : (
                        <tr key={saleIdx}>
                          <td className="px-4 py-2 text-sm">
                            <input type="checkbox" checked={selectedBills.includes(sale.bill_number)} onChange={(e) => {
                              if (e.target.checked) setSelectedBills(prev => [...prev, sale.bill_number]);
                              else setSelectedBills(prev => prev.filter(b => b !== sale.bill_number));
                            }} />
                          </td>
                          <td className="px-4 py-2 text-sm font-medium text-black">{sale.bill_number}</td>
                          <td className="px-4 py-2 text-sm text-black">{getCustomerName(sale.customer_id)}</td>
                          <td colSpan="4" className="px-4 py-2 text-sm text-gray-500">No items</td>
                          <td className="px-4 py-2 text-sm text-black">{renderPaymentStatus(sale.payment_status)}</td>
                          <td className="px-4 py-2 text-sm text-black">Rs 0</td>
                          <td className="px-4 py-2 text-sm text-black">{sale.payment_method || '–'}</td>
                          <td className="px-4 py-2 text-sm text-black">{formatDate(sale.due_date || sale.date)}</td>
                          <td className="px-4 py-2 text-sm">
                            <div className="flex gap-2">
                              <button onClick={() => handleEditSale(sale)} className="text-amber-600 hover:text-amber-800" title="Edit Sale">
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button onClick={() => handleDeleteSale(sale.bill_number)} className="text-red-600 hover:text-red-800" title="Delete Sale">
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                  )
              )}
            </tbody>
          </table>
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(filteredSales.length / pageSize)}
          onPageChange={setCurrentPage}
          pageSize={pageSize}
          onPageSizeChange={setPageSize}
          totalRecords={filteredSales.length}
        />
      </div>

      {/* Modal for New Sale */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{editMode ? 'Edit Sale' : 'New Sale'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">

              {/* Bill Number and Customer - 2 column layout */}
              <div className="grid grid-cols-2 gap-4">
                {/* Bill Number */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bill Number</label>
                  <input
                    type="text"
                    value={formData.bill_number}
                    onChange={(e) => setFormData({ ...formData, bill_number: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                {/* Customer */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Customer</label>
                  <select
                    value={formData.customer_id}
                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">Select Customer</option>
                    {customers.map(c => (
                      <option key={c.id} value={c.id}>👤 {c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <button 
                  type="button" 
                  onClick={() => window.location.href = '/customers'} 
                  className="text-sm text-primary-600 underline"
                >
                  + Create New Customer
                </button>
              </div>

              <LineItemsForm 
                lineItems={formData.line_items}
                onLineItemsChange={(lineItems) => setFormData({ ...formData, line_items: lineItems })}
                items={items}
                isSale={true}
                onNewItemCreated={(newItem) => {
                  console.log('✅ New item created in LineItemsForm:', newItem);
                  setItems([...items, newItem]);
                }}
              />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
                  <select
                    value={formData.payment_status}
                    onChange={(e) => setFormData({ ...formData, payment_status: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="paid">✅ Paid</option>
                    <option value="pending">⏳ Pending</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
                  <select
                    value={formData.payment_method}
                    onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">Select Method</option>
                    <option value="cash">💰 Cash</option>
                    <option value="allied bank">🏦 Allied Bank</option>
                    <option value="easypaisa">💵 Easypaisa</option>
                  </select>
                </div>
              </div>

              {/* Other fields below */}
              {[ 
                // { label: 'Quantity', key: 'quantity', type: 'number' },  // Moved above
                // { label: 'Unit Price', key: 'unit_price', type: 'number', step: '0.01' },  // Moved above
                // { label: 'Cost Basis', key: 'cost_basis', type: 'number', step: '0.01' },  // Commented out - not needed
                { label: 'Due Date', key: 'due_date', type: 'date' }
              ].map(field => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{field.label}</label>
                  <input
                    type={field.type}
                    step={field.step || undefined}
                    value={formData[field.key]}
                    onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
                    className="input"
                    required={field.key !== 'due_date'}
                  />
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes (Admin only)</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Add internal notes here..."
                  className="input"
                  rows="3"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  className="btn btn-primary flex-1"
                  disabled={editMode ? false : saveDisabled}
                >
                  {editMode ? 'Update Sale' : 'Save Sale'}
                </button>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Quick Add Item Modal removed as requested */}
    </div>
  );
};

export default Sales;
