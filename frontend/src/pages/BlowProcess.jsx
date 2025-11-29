import React, { useState, useEffect, useMemo } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Edit2, Trash2, Download, FileDown, X } from 'lucide-react';
import { generateBlowId } from '../utils/idGenerator';
import { useAuth } from '../context/AuthContext';
import ItemSelect from '../components/ItemSelect';

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
    output_quantity: '',
    waste_quantity: '',
    blow_cost_per_unit: '',
    notes: ''
  });

  // Initialize component on mount and ensure items load when blows are fetched
  useEffect(() => {
    const initializeBlowId = async () => {
      const blowId = await generateBlowId();
      setFormData(prev => ({ ...prev, id: blowId }));
    };
    initializeBlowId();
    fetchData();
  }, []);

  // Ensure items are loaded when component mounts or blows are updated
  useEffect(() => {
    if (blows.length > 0 && items.length === 0) {
      console.log('📦 Blows exist but items not loaded, fetching items...');
      const fetchItems = async () => {
        try {
          const itemsRes = await api.get('/stocks/items');
          setItems(itemsRes.data);
          console.log('📦 Items loaded:', itemsRes.data);
        } catch (error) {
          console.error('Failed to fetch items:', error);
        }
      };
      fetchItems();
    }
  }, [blows, items.length]);

  const fetchData = async () => {
    try {
      const [blowsRes, itemsRes] = await Promise.all([
        api.get('/blows'),
        api.get('/stocks/items')
      ]);
      setBlows(blowsRes.data);
      setItems(itemsRes.data);
      console.log('📊 Items fetched from /stocks/items:', itemsRes.data);
      if (itemsRes.data && itemsRes.data.length > 0) {
        console.log('📊 First item structure:', itemsRes.data[0]);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Convert string values to proper types and calculate waste
      const input = parseInt(formData.input_quantity) || 0;
      const output = parseInt(formData.output_quantity) || 0;
      const waste = Math.max(0, input - output);
      
      console.log('💾 SUBMIT DATA:', {
        input_quantity: input,
        output_quantity: output,
        waste_quantity: waste,
        calculation: `${input} - ${output} = ${waste}`
      });

      // Use manually selected bottle if provided, otherwise use auto-selected bottle
      const dataToSubmit = {
        ...formData,
        input_quantity: input,
        output_quantity: output,
        waste_quantity: waste,
        blow_cost_per_unit: parseFloat(formData.blow_cost_per_unit) || 0,
        to_item_id: formData.to_item_id || autoSelectedBottle?.id || null  // Manual > Auto > Backend determination
      };
      
      if (editMode) {
        await api.put(`/blows/${formData.id}`, dataToSubmit);
        toast.success('Blow process updated successfully');
      } else {
        await api.post('/blows', dataToSubmit);
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
      to_item_id: blow.to_item_id,
      input_quantity: blow.input_quantity,
      output_quantity: blow.output_quantity,
      waste_quantity: blow.waste_quantity,
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
      output_quantity: '',
      waste_quantity: '',
      blow_cost_per_unit: '',
      notes: ''
    });
    setEditMode(false);
  };

  // Allow all items to be selectable - items can come from purchases or pre-seeded
  const preforms = items.filter(item => item.type === 'preform');
  const bottles = items.filter(item => item.type === 'bottle');
  const allItems = items;  // All items available for selection (purchases + preforms + bottles)

  // Get available preform quantity for selected item - FOR DISPLAY ONLY, NOT VALIDATION
  const availablePreformQty = (() => {
    try {
      const preform = items.find(i => i.id === formData.from_item_id);
      if (!preform) return 0;
      return preform.current_stock ?? preform.quantity ?? preform.stock ?? 0;
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
  
  // Save is disabled if: no preform, no bottle (auto or manual), no input qty, or no output qty
  // Waste is auto-calculated, so doesn't need to be validated
  const saveDisabled = !formData.from_item_id || (!formData.to_item_id && !autoSelectedBottle) || inputQtyNum <= 0 || !formData.output_quantity;

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
    // If preform size matches bottle size, output = input
    if (preformSize === bottleSize) {
      return inputQty;
    }
    
    // If sizes don't match, calculate proportionally
    const ratio = preformSize / bottleSize;
    return Math.floor(inputQty * ratio);
  };

  // Get available preform quantity for selected item
  const getAvailablePreformQty = () => {
    const preform = items.find(item => item.id === formData.from_item_id);
    return preform?.available_quantity || preform?.quantity || 0;
  };

  // Create a map for faster lookups
  const itemMap = useMemo(() => {
    const map = {};
    items.forEach(item => {
      map[item.id] = item.name;
    });
    console.log('📊 ItemMap created with', Object.keys(map).length, 'items');
    return map;
  }, [items]);

  const getItemName = (itemId) => {
    if (!itemId) return '—';
    if (itemMap[itemId]) {
      return itemMap[itemId];
    }
    // Log if item not found for debugging
    console.warn('❌ Item not found in itemMap:', itemId, 'Available items:', Object.keys(itemMap));
    return '?';  // Show question mark instead of UUID
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
      document.body.removeChild(link);
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
      document.body.removeChild(link);
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
              <h2 className="text-2xl font-bold text-gray-900">{editMode ? 'Edit Blow Process' : 'New Blow Process'}</h2>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">From (Item - type to search or add)</label>
                  <ItemSelect
                    items={allItems}
                    value={formData.from_item_id ? items.find(i => i.id === formData.from_item_id)?.name || '' : ''}
                    onChange={async (selectedName) => {
                      console.log('🔄 BlowProcess item select (From):', selectedName);
                      
                      try {
                        // Try to find existing preform
                        const existingPreform = preforms.find(i => i.name.toLowerCase() === selectedName.toLowerCase());
                        
                        if (existingPreform) {
                          console.log('✅ Found existing preform:', existingPreform.id);
                          setFormData({ ...formData, from_item_id: existingPreform.id });
                        } else {
                          // Auto-create new preform with default type
                          console.log('📝 Creating new preform:', selectedName);
                          const response = await api.post('/stocks/items/auto-create', { 
                            name: selectedName,
                            type: 'preform'
                          });
                          const newPreform = response.data.item;
                          console.log('✅ Auto-created preform:', newPreform.id);
                          setFormData({ ...formData, from_item_id: newPreform.id });
                          
                          // Refresh items list to include new preform
                          try {
                            const itemsRes = await api.get('/stocks/items');
                            setItems(itemsRes.data);  // ✅ Update state with new items list
                            console.log('✅ Items list refreshed with new preform');
                          } catch (err) {
                            console.warn('Could not refresh items list:', err);
                          }
                        }
                      } catch (error) {
                        console.error('❌ Error with preform selection:', error.response?.data || error.message);
                        toast.error(error.response?.data?.detail || 'Error processing preform selection');
                      }
                    }}
                    placeholder="🔍 Select or type preform name..."
                  />
                  {formData.from_item_id && (
                    <p className="text-sm text-gray-600 mt-1">
                      Available: <span className="font-medium">{availablePreformQty}</span>
                    </p>
                  )}
                </div>

                {/* Bottle selection with auto-suggest or manual override */}
                {formData.from_item_id && (() => {
                  const selectedPreform = items.find(i => i.id === formData.from_item_id);
                  const autoBottle = selectedPreform ? items.find(i => 
                    i.type === 'bottle' && i.size === selectedPreform.size && i.grade === selectedPreform.grade
                  ) : null;
                  
                  // Get all items for ItemSelect (not just bottles)
                  const allSelectableItems = items;
                  
                  return (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">To (Item - type to search or add)</label>
                      <div className="space-y-2">
                        <ItemSelect
                          items={allSelectableItems}
                          value={formData.to_item_id ? items.find(i => i.id === formData.to_item_id)?.name || '' : (autoBottle?.name || '')}
                          onChange={async (selectedName) => {
                            console.log('🔄 BlowProcess item select (To):', selectedName);
                            
                            try {
                              // Try to find existing bottle
                              const existingBottle = bottles.find(i => i.name.toLowerCase() === selectedName.toLowerCase());
                              
                              if (existingBottle) {
                                console.log('✅ Found existing bottle:', existingBottle.id);
                                setFormData({ ...formData, to_item_id: existingBottle.id });
                              } else {
                                // Auto-create new bottle with preform's size/grade if available
                                console.log('📝 Creating new bottle:', selectedName);
                                const bottleData = { 
                                  name: selectedName,
                                  type: 'bottle'
                                };
                                
                                // Inherit size and grade from preform if available
                                if (selectedPreform) {
                                  bottleData.size = selectedPreform.size;
                                  bottleData.grade = selectedPreform.grade;
                                }
                                
                                const response = await api.post('/stocks/items/auto-create', bottleData);
                                const newBottle = response.data.item;
                                console.log('✅ Auto-created bottle:', newBottle.id);
                                setFormData({ ...formData, to_item_id: newBottle.id });
                                
                                // Refresh items list to include new bottle
                                try {
                                  const itemsRes = await api.get('/stocks/items');
                                  setItems(itemsRes.data);  // ✅ Update state with new items list
                                  console.log('✅ Items list refreshed with new bottle');
                                } catch (err) {
                                  console.warn('Could not refresh items list:', err);
                                }
                              }
                            } catch (error) {
                              console.error('❌ Error with bottle selection:', error.response?.data || error.message);
                              toast.error(error.response?.data?.detail || 'Error processing bottle selection');
                            }
                          }}
                          placeholder="🔍 Select or type bottle name..."
                        />
                        {autoBottle && !formData.to_item_id && (
                          <p className="text-xs text-green-600">💡 Tip: Auto-matched to <strong>{autoBottle.name}</strong> (same size/grade as preform)</p>
                        )}
                        {formData.to_item_id && (
                          <p className="text-xs text-blue-600">✓ Bottle selected: <strong>{items.find(i => i.id === formData.to_item_id)?.name}</strong></p>
                        )}
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
                      const input = e.target.value;
                      const output = parseInt(formData.output_quantity) || 0;
                      const waste = Math.max(0, parseInt(input || 0) - output);
                      setFormData({ 
                        ...formData, 
                        input_quantity: input,
                        waste_quantity: waste.toString()
                      });
                    }}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Output Quantity *</label>
                  <input
                    type="number"
                    value={formData.output_quantity}
                    onChange={(e) => {
                      const output = e.target.value;
                      const input = parseInt(formData.input_quantity) || 0;
                      const waste = Math.max(0, input - parseInt(output || 0));
                      setFormData({ 
                        ...formData, 
                        output_quantity: output,
                        waste_quantity: waste.toString()
                      });
                    }}
                    className="input"
                    required
                    placeholder="Enter actual output produced"
                  />
                  <p className="text-xs text-gray-500 mt-1">How many units were actually produced</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Waste Quantity (Auto-calculated)</label>
                  <input
                    type="number"
                    value={formData.waste_quantity}
                    onChange={(e) => setFormData({ ...formData, waste_quantity: e.target.value })}
                    className="input bg-gray-50"
                    placeholder="Auto-calculated from input - output"
                    disabled
                  />
                  <p className="text-xs text-gray-500 mt-1">Automatically calculated: Input ({formData.input_quantity || 0}) - Output ({formData.output_quantity || 0}) = Waste ({formData.waste_quantity || 0})</p>
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
                    {editMode ? 'Update Process' : 'Process'}
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

export default BlowProcess;
