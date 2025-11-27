import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Edit2, Trash2, Download, FileDown } from 'lucide-react';
import { generateBlowId } from '../utils/idGenerator';
import { useAuth } from '../context/AuthContext';

const BlowProcess = () => {
  const { user } = useAuth();
  const [blows, setBlows] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedBlows, setSelectedBlows] = useState([]);
  const [formData, setFormData] = useState({
    id: '',
    from_item_id: '',
    to_item_id: '',
    input_quantity: '',
    blow_cost_per_unit: '',
    notes: ''
  });

  // Initialize blow ID on component mount
  useEffect(() => {
    const initializeBlowId = async () => {
      const blowId = await generateBlowId();
      setFormData(prev => ({ ...prev, id: blowId }));
    };
    initializeBlowId();
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [blowsRes, itemsRes] = await Promise.all([
        api.get('/blows/'),
        api.get('/stocks/items')
      ]);
      setBlows(blowsRes.data);
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
      // Auto-set to_item_id from the preform selection
      const dataToSubmit = {
        ...formData,
        to_item_id: autoSelectedBottle?.id || null  // Will be set by backend if not provided
      };
      
      if (editMode) {
        await api.put(`/blows/${formData.id}`, dataToSubmit);
        toast.success('Blow process updated successfully');
      } else {
        await api.post('/blows/', dataToSubmit);
        toast.success('Blow process completed successfully');
      }
      setShowModal(false);
      fetchData();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${editMode ? 'update' : 'process'} blow`);
    }
  };

  const handleDelete = async (blowId) => {
    if (window.confirm('Are you sure you want to delete this blow process?')) {
      try {
        await api.delete(`/blows/${blowId}`);
        toast.success('Blow process deleted successfully');
        fetchData();
      } catch (error) {
        toast.error('Failed to delete blow process');
      }
    }
  };

  const handleEditBlow = (blow) => {
    setFormData({
      id: blow.id,
      from_item_id: blow.from_item_id,
      to_item_id: blow.to_item_id,  // Keep to_item_id for editing
      input_quantity: blow.input_quantity,
      blow_cost_per_unit: blow.blow_cost_per_unit,
      notes: blow.notes || ''
    });
    setEditMode(true);
    setShowModal(true);
  };

  const resetForm = async () => {
    const blowId = await generateBlowId();
    setFormData({
      id: blowId,
      from_item_id: '',
      to_item_id: '',
      input_quantity: '',
      blow_cost_per_unit: '',
      notes: ''
    });
    setEditMode(false);
  };

  const preforms = items.filter(item => item.type === 'preform');
  const bottles = items.filter(item => item.type === 'bottle');

  // Get available preform quantity for selected item
  const availablePreformQty = (() => {
    try {
      const preform = items.find(i => i.id === formData.from_item_id);
      return preform ? (preform.current_stock ?? 0) : 0;
    } catch (e) {
      return 0;
    }
  })();

  // Get available bottle quantity for selected item
  const availableBottleQty = (() => {
    try {
      const bottle = items.find(i => i.id === formData.to_item_id);
      return bottle ? (bottle.current_stock ?? 0) : 0;
    } catch (e) {
      return 0;
    }
  })();

  const inputQtyNum = Number(formData.input_quantity) || 0;
  
  // Get auto-selected bottle
  const selectedPreform = items.find(i => i.id === formData.from_item_id);
  const autoSelectedBottle = selectedPreform ? items.find(i => 
    i.type === 'bottle' && i.size === selectedPreform.size && i.grade === selectedPreform.grade
  ) : null;
  
  // Save is disabled if: no preform, no matching bottle, no input qty, or insufficient stock
  const saveDisabled = !formData.from_item_id || !autoSelectedBottle || inputQtyNum <= 0 || inputQtyNum > availablePreformQty;

  // ✅ Currency formatter for PKR
  const formatPKR = (amount) => {
    if (!amount) return '₨0.00';
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Get bottle size from bottle item
  const getBottleSize = (bottleItemId) => {
    const bottle = items.find(item => item.id === bottleItemId);
    // Extract size from bottle name (e.g., "500ml bottle" -> 500)
    const match = bottle?.name.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  };

  // Get preform size (assuming it's in the name)
  const getPreformSize = (preformItemId) => {
    const preform = items.find(item => item.id === preformItemId);
    // Extract size from preform name (e.g., "500ml preform" -> 500)
    const match = preform?.name.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  };

  // Calculate output quantity based on conversion ratio (preform size = bottle size)
  const calculateOutputQty = (inputQty, fromItemId, toItemId) => {
    const preformSize = getPreformSize(fromItemId);
    const bottleSize = getBottleSize(toItemId);
    
    if (preformSize === 0 || bottleSize === 0) return 0;
    
    // Ratio: 500ml preform can produce 500ml bottle (1:1 by size, but may vary)
    // If preform size matches bottle size, output = input (assuming 95% efficiency)
    if (preformSize === bottleSize) {
      return Math.floor(inputQty * 0.95); // 95% efficiency
    }
    
    // If sizes don't match, calculate proportionally
    const ratio = preformSize / bottleSize;
    return Math.floor(inputQty * ratio * 0.95);
  };

  // Get available preform quantity for selected item
  const getAvailablePreformQty = () => {
    const preform = items.find(item => item.id === formData.from_item_id);
    return preform?.available_quantity || preform?.quantity || 0;
  };

  const getItemName = (itemId) => {
    const item = items.find(i => i.id === itemId);
    return item ? item.name : itemId;
  };

  const downloadExcelAll = async () => {
    try {
      const response = await api.get('/reports/export-blow-excel', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `blow-processes-all-${new Date().toISOString().split('T')[0]}.xlsx`);
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
    if (selectedBlows.length === 0) {
      toast.error('Please select at least one blow process');
      return;
    }
    try {
      const blowIds = selectedBlows.join(',');
      const response = await api.get(`/reports/export-blow-excel?blow_ids=${blowIds}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `blow-processes-selected-${new Date().toISOString().split('T')[0]}.xlsx`);
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
          <h1 className="text-3xl font-bold text-gray-900">Blow Process</h1>
          <p className="text-gray-600 mt-2">Convert preforms to bottles</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={downloadExcelAll}
            className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300"
            title="Download all blow processes as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel All
          </button>
          <button
            onClick={downloadExcelSelected}
            disabled={selectedBlows.length === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
              selectedBlows.length === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 hover:text-green-800 border border-green-300'
            }`}
            title="Download selected blow processes as Excel file"
          >
            <FileDown className="w-4 h-4" /> Excel Selected
          </button>
          <button
            onClick={() => { setShowModal(true); resetForm(); }}
            className="btn btn-primary flex items-center gap-2 ml-auto"
          >
            <Plus className="w-5 h-5" /> New Blow Process
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
                    checked={selectedBlows.length === blows.length && blows.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedBlows(blows.map(b => b.id));
                      } else {
                        setSelectedBlows([]);
                      }
                    }}
                    className="w-4 h-4"
                  />
                </th>
                <th className="table-header-cell">Process ID</th>
                <th className="table-header-cell">From Item</th>
                <th className="table-header-cell">To Item</th>
                <th className="table-header-cell">Input</th>
                <th className="table-header-cell">Output</th>
                <th className="table-header-cell">Waste</th>
                <th className="table-header-cell">Efficiency</th>
                <th className="table-header-cell">Cost/Unit</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {blows.map((blow) => (
                <tr key={blow.id}>
                  <td className="table-cell w-10">
                    <input
                      type="checkbox"
                      checked={selectedBlows.includes(blow.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedBlows([...selectedBlows, blow.id]);
                        } else {
                          setSelectedBlows(selectedBlows.filter(b => b !== blow.id));
                        }
                      }}
                      className="w-4 h-4"
                    />
                  </td>
                  <td className="table-cell font-medium">{blow.id}</td>
                  <td className="table-cell">{getItemName(blow.from_item_id)}</td>
                  <td className="table-cell">{getItemName(blow.to_item_id)}</td>
                  <td className="table-cell">{blow.input_quantity}</td>
                  <td className="table-cell text-green-600 font-semibold">{blow.output_quantity}</td>
                  <td className="table-cell text-red-600">{blow.waste_quantity}</td>
                  <td className="table-cell">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                      {parseFloat(blow.efficiency_rate).toFixed(2)}%
                    </span>
                  </td>
                  {/* ✅ Display cost in PKR */}
                  <td className="table-cell">{formatPKR(blow.blow_cost_per_unit)}</td>
                  <td className="table-cell">
                    <div className="flex gap-2">
                      {user?.role === 'admin' && (
                        <>
                          <button onClick={() => handleEditBlow(blow)} className="text-orange-600 hover:text-orange-800" title="Edit">
                            📝
                          </button>
                          <button onClick={() => handleDelete(blow.id)} className="text-red-600 hover:text-red-800" title="Delete">
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

      {/* Modal for new blow process */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{editMode ? 'Edit Blow Process' : 'New Blow Process'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Process ID</label>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">From (Preform)</label>
                <select
                  value={formData.from_item_id}
                  onChange={(e) => setFormData({ ...formData, from_item_id: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">Select Preform</option>
                  {preforms.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
                {formData.from_item_id && (
                  <p className="text-sm text-gray-600 mt-1">
                    Available: <span className="font-medium">{availablePreformQty}</span>
                  </p>
                )}
              </div>

              {/* Auto-selected bottle display (no select needed) */}
              {formData.from_item_id && (() => {
                const selectedPreform = items.find(i => i.id === formData.from_item_id);
                const autoBottle = selectedPreform ? items.find(i => 
                  i.type === 'bottle' && i.size === selectedPreform.size && i.grade === selectedPreform.grade
                ) : null;
                
                return (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">To (Bottle - Auto Selected)</label>
                    <div className="input bg-gray-50 flex items-center justify-between">
                      <span className="text-gray-700">
                        {autoBottle ? autoBottle.name : <span className="text-red-600">❌ No matching bottle found</span>}
                      </span>
                      {autoBottle && <span className="text-green-600 text-sm">✓ Auto</span>}
                    </div>
                  </div>
                );
              })()}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Input Quantity</label>
                <input
                  type="number"
                  value={formData.input_quantity}
                  onChange={(e) => {
                    const qty = e.target.value;
                    setFormData({ ...formData, input_quantity: qty });
                  }}
                  className="input"
                  required
                />
                {formData.input_quantity && formData.from_item_id && (
                  <div className="text-sm text-gray-600 mt-1">
                    {inputQtyNum > availablePreformQty ? (
                      <p className="text-red-600 font-medium">❌ Insufficient stock (Available: {availablePreformQty})</p>
                    ) : (
                      <p className="text-green-600 font-medium">✅ Sufficient stock</p>
                    )}
                    {autoSelectedBottle && (
                      <p className="mt-1 text-gray-700">📦 Output: ~{calculateOutputQty(inputQtyNum, formData.from_item_id, autoSelectedBottle.id)} units (95% efficiency)</p>
                    )}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Blow Cost Per Unit (PKR)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.blow_cost_per_unit}
                  onChange={(e) => setFormData({ ...formData, blow_cost_per_unit: e.target.value })}
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
                  rows="2"
                  placeholder="Add any notes..."
                ></textarea>
              </div>

              <div className="flex gap-4 pt-4">
                <button 
                  type="submit" 
                  className="btn btn-primary flex-1"
                  disabled={saveDisabled}
                >
                  {inputQtyNum > availablePreformQty ? '❌ Insufficient Stock' : (editMode ? 'Update Process' : 'Process')}
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

export default BlowProcess;
