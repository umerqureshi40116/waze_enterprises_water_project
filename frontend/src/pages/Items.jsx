import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Edit2, Trash2, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Items = () => {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [formData, setFormData] = useState({
    id: '',
    name: 'PET Preform',
    type: 'preform',
    size: '500ml',
    grade: 'A',
    unit: ''
  });

  // Item name options
  const itemNameOptions = {
    preform: 'PET Preform',
    bottle: 'Water Bottle'
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await api.get('/stocks/items');
      console.log('Fetched items:', response.data);
      setItems(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching items:', error);
      toast.error('Failed to fetch items');
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate item ID based on form data
  const generateItemId = () => {
    const typePrefix = formData.type.charAt(0).toUpperCase() + formData.type.slice(1);
    const sizeClean = formData.size.replace('ml', '');
    return `Item_${typePrefix}_${sizeClean}_${formData.grade}`;
  };

  // Update ID whenever type, size, grade, or name changes
  useEffect(() => {
    if (!editMode && formData.type && formData.size && formData.grade && formData.name) {
      setFormData(prev => ({ ...prev, id: generateItemId() }));
    }
  }, [formData.type, formData.size, formData.grade, formData.name, editMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        const encodedId = encodeURIComponent(selectedItem.id);
        await api.put(`/stocks/items/${encodedId}`, formData);
        toast.success('Item updated successfully');
      } else {
        await api.post('/stocks/items', formData);
        toast.success('Item created successfully');
      }
      setShowModal(false);
      fetchItems();
      resetForm();
    } catch (error) {
      console.error('Save item error:', error);
      const msg = error.response?.data?.detail || `Failed to ${editMode ? 'update' : 'create'} item`;
      toast.error(msg);
    }
  };

  const handleEdit = (item) => {
    setSelectedItem(item);
    
    // Extract base name from full name "PET Preform 500ml A" -> "PET Preform"
    const nameParts = item.name.split(' ');
    const baseName = nameParts.slice(0, -2).join(' '); // Remove size and grade
    
    setFormData({
      id: item.id,
      name: baseName || item.name,
      type: item.type,
      size: item.size,
      grade: item.grade,
      unit: item.unit  // Now just a simple unit like 'pcs'
    });
    setEditMode(true);
    setShowModal(true);
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this item? This cannot be undone.')) {
      return;
    }

    try {
      console.log('Deleting item with ID:', itemId);
      const encodedId = encodeURIComponent(itemId);
      console.log('Encoded ID:', encodedId);
      console.log('DELETE URL:', `/stocks/items/${encodedId}`);
      await api.delete(`/stocks/items/${encodedId}`);
      toast.success('Item deleted successfully');
      fetchItems();
    } catch (error) {
      console.error('Delete error details:', error);
      const msg = error.response?.data?.detail || 'Failed to delete item';
      toast.error(msg);
    }
  };

  const resetForm = () => {
    setFormData({
      id: '',
      name: 'PET Preform',
      type: 'preform',
      size: '500ml',
      grade: 'A',
      unit: ''
    });
    setEditMode(false);
    setSelectedItem(null);
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'preform':
        return 'bg-blue-100 text-blue-800';
      case 'bottle':
        return 'bg-green-100 text-green-800';
      case 'sold':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-4 text-gray-700 font-medium">Loading items...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Items Management</h1>
          <p className="text-gray-600 mt-1">Manage all item types and configurations</p>
        </div>
        {user?.role === 'admin' && (
          <button
            onClick={() => { setShowModal(true); resetForm(); }}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" /> New Item
          </button>
        )}
      </div>

      {/* Quick Add Suggestions */}
      {user?.role === 'admin' && items.length < 5 && (
        <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Start</h3>
          <p className="text-sm text-gray-600 mb-4">Start with these common items:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {[
              { name: 'PET Preform', type: 'preform', size: '500ml', grade: 'A' },
              { name: 'Water Bottle', type: 'bottle', size: '500ml', grade: 'A' },
              { name: 'PET Preform', type: 'preform', size: '1000ml', grade: 'A' },
              { name: 'Mineral Bottle', type: 'bottle', size: '1000ml', grade: 'A' }
            ].map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setFormData({
                    id: '',
                    name: preset.name,
                    type: preset.type,
                    size: preset.size,
                    grade: preset.grade,
                    unit: 'pcs'
                  });
                  setEditMode(false);
                  setShowModal(true);
                }}
                className="p-2 text-left bg-white rounded-lg border border-blue-200 hover:border-blue-400 hover:shadow transition text-sm"
              >
                <div className="font-medium text-gray-900">{preset.name}</div>
                <div className="text-xs text-gray-500">{preset.size} • {preset.type}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item) => (
            <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <Package className="w-5 h-5 text-primary-600" />
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getTypeColor(item.type)}`}>
                    {item.type}
                  </span>
                </div>
                {user?.role === 'admin' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        console.log('Edit button clicked, item:', item);
                        handleEdit(item);
                      }}
                      className="text-blue-600 hover:text-blue-800"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {
                        console.log('Delete button clicked, item:', item);
                        console.log('item.id:', item.id);
                        handleDelete(item.id);
                      }}
                      className="text-red-600 hover:text-red-800"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
              
              <h3 className="font-semibold text-lg text-gray-900 mb-1">{item.name}</h3>
              <p className="text-xs text-gray-500 mb-3 font-mono">{item.id}</p>
              
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span className="font-semibold">{item.size}</span>
                </div>
                <div className="flex justify-between">
                  <span>Grade:</span>
                  <span className="font-semibold">{item.grade}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unit:</span>
                  <span className="font-semibold">{item.unit}</span>
                </div>
                <div className="flex justify-between border-t pt-2 mt-2">
                  <span>Current Stock:</span>
                  <span className="font-bold text-primary-600">{item.current_stock}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {items.length === 0 && (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No items found</p>
            {user?.role === 'admin' && (
              <button
                onClick={() => setShowModal(true)}
                className="mt-4 text-primary-600 hover:text-primary-800 font-semibold"
              >
                Create your first item
              </button>
            )}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {editMode ? 'Edit Item' : 'New Item'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Item ID <span className="text-xs text-gray-500">(Auto-generated)</span>
                </label>
                <input
                  type="text"
                  value={formData.id}
                  className="input bg-gray-50"
                  disabled
                />
                <p className="text-xs text-gray-500 mt-1">Generated based on type, size, grade, and name</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value, name: itemNameOptions[e.target.value] })}
                  className="input"
                  required
                  disabled={editMode}
                >
                  <option value="preform">Preform</option>
                  <option value="bottle">Bottle</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Preform = Raw material | Bottle = Produced
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Size
                  </label>
                  <div className="flex gap-2">
                    <select
                      value={formData.size}
                      onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                      className="input flex-1"
                      required
                    >
                      <option value="">Select size...</option>
                      <option value="50ml">50ml</option>
                      <option value="100ml">100ml</option>
                      <option value="150ml">150ml</option>
                      <option value="200ml">200ml</option>
                      <option value="250ml">250ml</option>
                      <option value="500ml">500ml</option>
                      <option value="750ml">750ml</option>
                      <option value="1000ml">1000ml</option>
                      <option value="1500ml">1500ml</option>
                      <option value="2000ml">2000ml</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Grade
                  </label>
                  <select
                    value={formData.grade}
                    onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="A">Grade A</option>
                    <option value="B">Grade B</option>
                    <option value="C">Grade C</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit Type
                </label>
                <input
                  type="text"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  className="input"
                  placeholder="e.g., pcs, kg, liters"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Unit of measurement (pieces, kg, liters, etc.)
                </p>
              </div>

              <div className="flex gap-4 pt-4">
                <button type="submit" className="btn btn-primary flex-1">
                  {editMode ? 'Update Item' : 'Create Item'}
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

export default Items;
