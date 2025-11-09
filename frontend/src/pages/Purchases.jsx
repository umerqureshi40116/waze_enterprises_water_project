import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Trash2, Download, FileDown, X, Edit2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { formatCurrency, formatCurrencySimple, formatDate } from '../utils/currency';
import { generatePurchaseNumber } from '../utils/idGenerator';
import Pagination from '../components/Pagination';
import LineItemsForm from '../components/LineItemsForm';

const Purchases = () => {
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [filteredPurchases, setFilteredPurchases] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSupplier, setFilterSupplier] = useState('');
  const [filterPaymentStatus, setFilterPaymentStatus] = useState('');
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
    supplier_id: '',
    line_items: [],
    due_date: getTodayDate(),
    payment_status: 'paid',
    payment_method: 'cash',
    paid_amount: 0,
    notes: ''
  });

  // removed quick-add item state

  useEffect(() => {
    // Initialize bill number
    const initializeBillNumber = async () => {
      const billNumber = await generatePurchaseNumber(formData.due_date);
      setFormData(prev => ({ ...prev, bill_number: billNumber }));
    };
    initializeBillNumber();
    
    // Fix existing paid purchases on component mount
    const fixPaidAmounts = async () => {
      try {
        await api.post('/purchases/fix/paid-amounts');
      } catch (error) {
        console.log('Paid amounts already fixed or no fixes needed');
      }
    };
    
    fixPaidAmounts();
    fetchData();
  }, []);

  // Regenerate bill number when due_date changes
  useEffect(() => {
    const generateNewBillNumber = async () => {
      const billNumber = await generatePurchaseNumber(formData.due_date);
      setFormData(prev => ({ ...prev, bill_number: billNumber }));
    };
    generateNewBillNumber();
  }, [formData.due_date]);

  const fetchData = async () => {
    try {
      const [purchasesRes, suppliersRes, itemsRes] = await Promise.all([
        api.get('/purchases/'),
        api.get('/suppliers/'),
        api.get('/stocks/items')
      ]);

      setPurchases(Array.isArray(purchasesRes.data) ? purchasesRes.data : []);
      setFilteredPurchases(Array.isArray(purchasesRes.data) ? purchasesRes.data : []);
      setSuppliers(Array.isArray(suppliersRes.data) ? suppliersRes.data : []);
      setItems(Array.isArray(itemsRes.data) ? itemsRes.data : []);
      
      console.log('Items fetched:', itemsRes.data);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to fetch data');
      setPurchases([]);
      setFilteredPurchases([]);
      setSuppliers([]);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter purchases based on search and filters
  useEffect(() => {
    let filtered = [...purchases];

    // Search by bill number
    if (searchTerm) {
      filtered = filtered.filter(p => 
        p.bill_number.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by supplier
    if (filterSupplier) {
      filtered = filtered.filter(p => p.supplier_id === filterSupplier);
    }

    // Filter by payment status
    if (filterPaymentStatus) {
      filtered = filtered.filter(p => p.payment_status === filterPaymentStatus);
    }

    // Filter by date range (using due_date which is the user-selected transaction date)
    if (filterStartDate) {
      filtered = filtered.filter(p => new Date(p.due_date) >= new Date(filterStartDate));
    }
    if (filterEndDate) {
      filtered = filtered.filter(p => new Date(p.due_date) <= new Date(filterEndDate));
    }

    setFilteredPurchases(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchTerm, filterSupplier, filterPaymentStatus, filterStartDate, filterEndDate, purchases]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('📝 SUBMIT CLICKED');
      console.log('formData:', formData);
      console.log('formData.line_items:', formData.line_items);
      console.log('formData.line_items length:', formData.line_items?.length);
      
      if (!formData.line_items || formData.line_items.length === 0) {
        console.log('❌ NO ITEMS IN FORM DATA');
        toast.error('Please add at least one item');
        return;
      }
      
      console.log('✅ Items found:', formData.line_items.length);
      
      if (!formData.supplier_id) {
        console.log('❌ NO SUPPLIER SELECTED');
        toast.error('Please select a supplier');
        return;
      }
      
      console.log('✅ All validations passed');
      const purchaseData = {
        bill_number: formData.bill_number,
        supplier_id: String(formData.supplier_id),
        due_date: formData.due_date || getTodayDate(),
        line_items: formData.line_items.map(item => ({
          item_id: String(item.item_id),
          quantity: Number(item.quantity),
          unit_price: parseFloat(item.unit_price)
        })),
        payment_status: formData.payment_status || "pending",
        paid_amount: formData.payment_status === 'paid' 
          ? formData.line_items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
          : parseFloat(formData.paid_amount) || 0,
        notes: formData.notes || ""
      };
      console.log("📦 formData.due_date =", formData.due_date);
      console.log("📦 purchaseData being sent:", purchaseData);
      if (editMode) {
        await api.put(`/purchases/${formData.bill_number}`, purchaseData);
        toast.success('Purchase updated successfully');
      } else {
        await api.post('/purchases/', purchaseData);
        toast.success('Purchase created successfully');
      }
      setShowModal(false);
      fetchData();
      resetForm();
    } catch (error) {
      console.error('Create/Update purchase error:', error);
      const detail = error.response?.data?.detail;
      let errorMsg = editMode ? "Failed to update purchase" : "Failed to create purchase";
      if (Array.isArray(detail)) {
        errorMsg = detail.map(d => `${d.loc?.join(' → ')}: ${d.msg}`).join(', ');
      } else if (typeof detail === 'string') {
        errorMsg = detail;
      }
      toast.error(errorMsg);
    }
  };

  const handleDelete = async (billNumber) => {
    if (window.confirm('Are you sure you want to delete this purchase?')) {
      try {
        await api.delete(`/purchases/${billNumber}`);
        toast.success('Purchase deleted successfully');
        fetchData();
      } catch (error) {
        toast.error('Failed to delete purchase');
      }
    }
  };

  const handleEditPurchase = (purchase) => {
    setFormData({
      bill_number: purchase.bill_number,
      supplier_id: purchase.supplier_id,
      line_items: purchase.line_items || [],
      due_date: purchase.due_date || '',
      payment_status: purchase.payment_status,
      payment_method: purchase.payment_method || 'cash',
      paid_amount: purchase.paid_amount || 0,
      notes: purchase.notes || ''
    });
    setEditMode(true);
    setShowModal(true);
  };

  const resetForm = async () => {
    const todayDate = getTodayDate();
    const billNumber = await generatePurchaseNumber(todayDate);
    setFormData({
      bill_number: billNumber,
      supplier_id: '',
      line_items: [],
      due_date: todayDate,
      payment_status: 'paid',
      payment_method: 'cash',
      paid_amount: 0,
      notes: ''
    });
    setEditMode(false);
  };

  const downloadPDF = async (billNumber) => {
    try {
      const response = await api.get(`/reports/pdf/bill/${billNumber}?bill_type=purchase`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${billNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const downloadSelectedPDF = async () => {
    if (!selectedBills || selectedBills.length === 0) {
      toast('No bills selected');
      return;
    }
    try {
      const response = await api.post('/purchases/pdf/purchases', { bill_numbers: selectedBills }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `combined-purchases-${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download selected purchases error:', error);
      toast.error('Failed to download selected purchases');
    }
  };

  const downloadExcelAll = async () => {
    try {
      const response = await api.get('/reports/export-purchases-excel', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `purchases-all-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('All purchases exported to Excel!');
    } catch (error) {
      toast.error('Failed to download Excel');
      console.error(error);
    }
  };

  const downloadExcelSelected = async () => {
    if (!selectedBills || selectedBills.length === 0) {
      toast.error('No purchases selected');
      return;
    }
    try {
      const response = await api.get(`/reports/export-purchases-excel?bill_numbers=${selectedBills.join(',')}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `purchases-selected-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Selected purchases exported to Excel!');
    } catch (error) {
      toast.error('Failed to download Excel');
      console.error(error);
    }
  };

  const renderPaymentStatus = (status) => {
    switch (status) {
      case 'paid':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">✅ Paid</span>;
      case 'pending':
        return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-semibold">⏳ Pending</span>;
      case 'partial':
        return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">💰 Partial</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-semibold">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Purchases</h1>
          <p className="text-gray-600 mt-2">Manage your purchase orders</p>
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
            title="Download selected purchases as combined PDF"
          >
            <Download className="w-4 h-4" /> PDF
          </button>
          <button
            onClick={downloadExcelAll}
            className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300"
            title="Download all purchases as Excel file"
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
            title="Download selected purchases as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel Selected
          </button>
          <button
            onClick={() => { setShowModal(true); resetForm(); }}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" /> New Purchase
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Start Date
            </label>
            <input
              type="date"
              value={filterStartDate}
              onChange={(e) => setFilterStartDate(e.target.value)}
              className="input"
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
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              👤 Filter by Supplier
            </label>
            <select
              value={filterSupplier}
              onChange={(e) => setFilterSupplier(e.target.value)}
              className="input"
            >
              <option value="">All Suppliers</option>
              {suppliers.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
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
              className="input"
            >
              <option value="">All Status</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
              {/* <option value="partial">Partial</option> */}
            </select>
          </div>
        </div>
        <div className="mt-3 text-sm text-gray-600">
          Showing {filteredPurchases.length} of {purchases.length} purchases
        </div>
      </div>

      {/* Purchases Table */}
      <div className="card">
        <div className="table-container overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  <input type="checkbox" checked={selectedBills.length > 0 && selectedBills.length === filteredPurchases.length} onChange={(e) => {
                    if (e.target.checked) setSelectedBills(filteredPurchases.map(p => p.bill_number));
                    else setSelectedBills([]);
                  }} />
                </th>
                {['Bill Number','Supplier','Item','Quantity','Unit Price','Total','Status','Paid Amount','Date','Actions'].map(header => (
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
              {filteredPurchases.length === 0 ? (
                <tr>
                  <td colSpan="10" className="text-center py-8 text-gray-500 text-sm">
                    {purchases.length === 0 ? (
                      <>
                        No purchase records found.
                        <button
                          onClick={() => setShowModal(true)}
                          className="text-primary-600 ml-1 underline"
                        >
                          Create your first purchase
                        </button>
                      </>
                    ) : (
                      'No purchases match your filters. Try adjusting your search criteria.'
                    )}
                  </td>
                </tr>
              ) : (
                filteredPurchases
                  .slice((currentPage - 1) * pageSize, currentPage * pageSize)
                  .flatMap((purchase, purchaseIdx) => 
                    purchase.line_items && purchase.line_items.length > 0
                      ? purchase.line_items.map((item, itemIdx) => (
                          <tr key={`${purchaseIdx}-${itemIdx}`}>
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm">
                                <input type="checkbox" checked={selectedBills.includes(purchase.bill_number)} onChange={(e) => {
                                  if (e.target.checked) setSelectedBills(prev => [...prev, purchase.bill_number]);
                                  else setSelectedBills(prev => prev.filter(b => b !== purchase.bill_number));
                                }} />
                              </td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm font-medium text-black">{purchase.bill_number}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm text-black">{suppliers.find(s => s.id === purchase.supplier_id)?.name || purchase.supplier_id}</td>
                            )}
                            <td className="px-4 py-2 text-sm text-black">{items.find(i => i.id === item.item_id)?.name || item.item_id}</td>
                            <td className="px-4 py-2 text-sm text-black">{item.quantity}</td>
                            <td className="px-4 py-2 text-sm text-black">Rs {parseFloat(item.unit_price).toLocaleString()}</td>
                            <td className="px-4 py-2 text-sm font-semibold text-green-600">Rs {(item.quantity * parseFloat(item.unit_price)).toLocaleString()}</td>
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm text-black">{renderPaymentStatus(purchase.payment_status)}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm text-black">
                                {purchase.payment_status === 'pending' 
                                  ? 'Rs ' + formatCurrencySimple((purchase.line_items?.reduce((sum, li) => sum + (li.quantity * li.unit_price), 0) || 0) - (parseFloat(purchase.paid_amount) || 0)) + ' (Pending)'
                                  : purchase.payment_status === 'paid' && purchase.paid_amount == 0 
                                  ? 'Rs ' + formatCurrencySimple(purchase.line_items?.reduce((sum, li) => sum + (li.quantity * li.unit_price), 0) || 0)
                                  : 'Rs ' + formatCurrencySimple(purchase.paid_amount)
                                }
                              </td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm text-black">{formatDate(purchase.due_date || purchase.date)}</td>
                            )}
                            {itemIdx === 0 && (
                              <td rowSpan={purchase.line_items.length} className="px-4 py-2 text-sm">
                                <div className="flex gap-2">
                                  {user?.role === 'admin' && (
                                    <>
                                      <button onClick={() => handleEditPurchase(purchase)} className="text-amber-600 hover:text-amber-800" title="Edit Purchase">
                                        <Edit2 className="w-4 h-4" />
                                      </button>
                                      <button onClick={() => handleDelete(purchase.bill_number)} className="text-red-600 hover:text-red-800" title="Delete Purchase">
                                        <Trash2 className="w-4 h-4" />
                                      </button>
                                    </>
                                  )}
                                </div>
                              </td>
                            )}
                          </tr>
                        ))
                      : (
                        <tr key={purchaseIdx}>
                          <td className="px-4 py-2 text-sm">
                            <input type="checkbox" checked={selectedBills.includes(purchase.bill_number)} onChange={(e) => {
                              if (e.target.checked) setSelectedBills(prev => [...prev, purchase.bill_number]);
                              else setSelectedBills(prev => prev.filter(b => b !== purchase.bill_number));
                            }} />
                          </td>
                          <td className="px-4 py-2 text-sm font-medium text-black">{purchase.bill_number}</td>
                          <td className="px-4 py-2 text-sm text-black">{suppliers.find(s => s.id === purchase.supplier_id)?.name || purchase.supplier_id}</td>
                          <td colSpan="4" className="px-4 py-2 text-sm text-gray-500">No items</td>
                          <td className="px-4 py-2 text-sm text-black">{renderPaymentStatus(purchase.payment_status)}</td>
                          <td className="px-4 py-2 text-sm text-black">Rs 0</td>
                          <td className="px-4 py-2 text-sm text-black">{formatDate(purchase.due_date || purchase.date)}</td>
                          <td className="px-4 py-2 text-sm">
                            <div className="flex gap-2">
                              {user?.role === 'admin' && (
                                <>
                                  <button onClick={() => handleEditPurchase(purchase)} className="text-amber-600 hover:text-amber-800" title="Edit Purchase">
                                    <Edit2 className="w-4 h-4" />
                                  </button>
                                  <button onClick={() => handleDelete(purchase.bill_number)} className="text-red-600 hover:text-red-800" title="Delete Purchase">
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </>
                              )}
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
          totalPages={Math.ceil(filteredPurchases.length / pageSize)}
          onPageChange={setCurrentPage}
          pageSize={pageSize}
          onPageSizeChange={setPageSize}
          totalRecords={filteredPurchases.length}
        />
      </div>

      {/* Slide-out Panel for Form */}
      {/* Modal for New Purchase */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{editMode ? 'Edit Purchase' : 'New Purchase'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">

              {/* Bill Number and Supplier - 2 column layout */}
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
                    disabled={editMode}
                  />
                </div>

                {/* Supplier */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Supplier</label>
                  <select
                    value={formData.supplier_id}
                    onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">Select Supplier</option>
                    {suppliers.map(s => (
                      <option key={s.id} value={s.id}>🏢 {s.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <button 
                  type="button" 
                  onClick={() => window.location.href = '/suppliers'} 
                  className="text-sm text-primary-600 underline"
                >
                  + Create New Supplier
                </button>
              </div>

              <LineItemsForm 
                lineItems={formData.line_items}
                onLineItemsChange={(lineItems) => setFormData({ ...formData, line_items: lineItems })}
                items={items}
                isSale={false}
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="input"
                  rows="2"
                  placeholder="Add any notes..."
                ></textarea>
              </div>

              <div className="flex gap-4 pt-4">
                <button type="submit" className="btn btn-primary flex-1">{editMode ? 'Update Purchase' : 'Save Purchase'}</button>
                <button type="button" onClick={() => { setShowModal(false); resetForm(); }} className="btn btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Quick Add Item Modal removed as requested */}
    </div>
  );
};

export default Purchases;
