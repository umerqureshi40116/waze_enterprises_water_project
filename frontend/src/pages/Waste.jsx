import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Trash2, FileDown } from 'lucide-react';
import { generateWasteId } from '../utils/idGenerator';
import { useAuth } from '../context/AuthContext';
import { formatDate } from '../utils/currency';

const Waste = () => {
  const { user } = useAuth();
  const [wastes, setWastes] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedWastes, setSelectedWastes] = useState([]);
  const [formData, setFormData] = useState({
    id: '',
    item_id: '',
    quantity: '',
    price_per_unit: '',
    notes: ''
  });

  // Initialize waste ID on component mount
  useEffect(() => {
    const initializeWasteId = async () => {
      const wasteId = await generateWasteId();
      setFormData(prev => ({ ...prev, id: wasteId }));
    };
    initializeWasteId();
  }, []);

  // ✅ Utility to format as PKR
  const formatCurrency = (value) => {
    if (value == null || isNaN(value)) return 'N/A';
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 2
    }).format(value);
  };

  // Get item name by ID
  const getItemName = (itemId) => {
    const item = items.find(i => i.id === itemId);
    return item ? item.name : itemId;
  };

  // Get item stock quantity by ID
  const getItemStock = (itemId) => {
    const item = items.find(i => i.id === itemId);
    return item ? item.current_stock : 0;
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [wastesRes, itemsRes] = await Promise.all([
        api.get('/wastes/'),
        api.get('/stocks/items')
      ]);
      setWastes(wastesRes.data);
      setItems(itemsRes.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await api.put(`/wastes/${formData.id}`, formData);
        toast.success('Waste updated successfully');
      } else {
        await api.post('/wastes/', formData);
        toast.success('Waste recorded successfully');
      }
      setShowModal(false);
      fetchData();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${editMode ? 'update' : 'record'} waste`);
    }
  };

  const handleDelete = async (wasteId) => {
    if (window.confirm('Are you sure you want to delete this waste record?')) {
      try {
        await api.delete(`/wastes/${wasteId}`);
        toast.success('Waste deleted successfully');
        fetchData();
      } catch (error) {
        toast.error('Failed to delete waste');
      }
    }
  };

  const handleEditWaste = (waste) => {
    setFormData({
      id: waste.id,
      item_id: waste.item_id,
      quantity: waste.quantity,
      price_per_unit: waste.price_per_unit,
      notes: waste.notes || ''
    });
    setEditMode(true);
    setShowModal(true);
  };

  const resetForm = async () => {
    const wasteId = await generateWasteId();
    setFormData({
      id: wasteId,
      item_id: '',
      quantity: '',
      price_per_unit: '',
      notes: ''
    });
    setEditMode(false);
  };

  const downloadExcelAll = async () => {
    try {
      const response = await api.get('/reports/export-waste-excel', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `waste-records-all-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Excel file downloaded successfully');
    } catch (error) {
      toast.error('Failed to download Excel file');
    }
  };

  const downloadExcelSelected = async () => {
    if (selectedWastes.length === 0) {
      toast.error('Please select at least one waste record');
      return;
    }
    try {
      const wasteIds = selectedWastes.join(',');
      const response = await api.get(`/reports/export-waste-excel?waste_ids=${wasteIds}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `waste-records-selected-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Excel file downloaded successfully');
    } catch (error) {
      toast.error('Failed to download Excel file');
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Waste Management</h1>
          <p className="text-gray-600 mt-2">Record damaged items sold at low price</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={downloadExcelAll}
            className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300"
            title="Download all waste records as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel All
          </button>
          <button
            onClick={downloadExcelSelected}
            disabled={selectedWastes.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedWastes.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300'
            }`}
            title="Download selected waste records as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel Selected
          </button>
          <button
            onClick={() => {
              setShowModal(true);
              resetForm();
            }}
            className="btn btn-primary flex items-center gap-2 ml-auto"
          >
            <Plus className="w-5 h-5" /> Record Waste
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell w-10">
                  <input
                    type="checkbox"
                    checked={selectedWastes.length === wastes.length && wastes.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedWastes(wastes.map(w => w.id));
                      } else {
                        setSelectedWastes([]);
                      }
                    }}
                    className="w-4 h-4"
                  />
                </th>
                <th className="table-header-cell">Waste ID</th>
                <th className="table-header-cell">Item</th>
                <th className="table-header-cell">Quantity</th>
                <th className="table-header-cell">Price/Unit</th>
                <th className="table-header-cell">Total Recovery</th>
                <th className="table-header-cell">Notes</th>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {wastes.map((waste) => (
                <tr key={waste.id}>
                  <td className="table-cell w-10">
                    <input
                      type="checkbox"
                      checked={selectedWastes.includes(waste.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedWastes([...selectedWastes, waste.id]);
                        } else {
                          setSelectedWastes(selectedWastes.filter(w => w !== waste.id));
                        }
                      }}
                      className="w-4 h-4"
                    />
                  </td>
                  <td className="table-cell font-medium">{waste.id}</td>
                  <td className="table-cell">{getItemName(waste.item_id)}</td>
                  <td className="table-cell">{waste.quantity}</td>
                  <td className="table-cell">{formatCurrency(waste.price_per_unit)}</td>
                  <td className="table-cell font-semibold text-green-600">
                    {formatCurrency(waste.total_price)}
                  </td>
                  <td className="table-cell text-gray-600">{waste.notes}</td>
                  <td className="table-cell">
                    {formatDate(waste.date)}
                  </td>
                  <td className="table-cell">
                    <div className="flex gap-2">
                      {user?.role === 'admin' && (
                        <>
                          <button onClick={() => handleEditWaste(waste)} className="text-orange-600 hover:text-orange-800" title="Edit">
                            📝
                          </button>
                          <button onClick={() => handleDelete(waste.id)} className="text-red-600 hover:text-red-800" title="Delete">
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
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{editMode ? 'Edit Waste' : 'Record Waste'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Waste ID</label>
                <input
                  type="text"
                  value={formData.id}
                  onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                  className="input"
                  required
                  disabled={editMode}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Item</label>
                <select
                  value={formData.item_id}
                  onChange={(e) => setFormData({ ...formData, item_id: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">Select Item</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} - 📊 Stock: {item.current_stock}
                    </option>
                  ))}
                </select>
                {formData.item_id && (
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-900 font-medium">
                    📦 Available Stock: <span className="font-bold text-lg text-blue-600">{getItemStock(formData.item_id)}</span> units
                  </div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recovery Price Per Unit (PKR)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price_per_unit}
                  onChange={(e) =>
                    setFormData({ ...formData, price_per_unit: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="input"
                  rows="3"
                  placeholder="Reason for waste..."
                ></textarea>
              </div>
              <div className="flex gap-4 pt-4">
                <button type="submit" className="btn btn-primary flex-1">
                  {editMode ? 'Update Waste' : 'Record'}
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
      )}
    </div>
  );
};

export default Waste;
