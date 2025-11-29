import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Package, TrendingUp, TrendingDown, AlertCircle, Plus } from 'lucide-react';

const Stock = () => {
  const [stocks, setStocks] = useState([]);
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('current');
  const [showModal, setShowModal] = useState(false);
  const [items, setItems] = useState([]);
  const [movementFilterItem, setMovementFilterItem] = useState(''); // Add filter state
  const [formData, setFormData] = useState({
    item_id: '',
    quantity_change: 0,
    adjustment_type: 'add',
    reason: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [stocksRes, movementsRes, itemsRes] = await Promise.all([
        api.get('/stocks'),
        api.get('/stocks/movements'),
        api.get('/stocks/items')
      ]);
      setStocks(stocksRes.data);
      setMovements(movementsRes.data);
      setItems(itemsRes.data);
    } catch (error) {
      toast.error('Failed to fetch stock data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'quantity_change' ? parseInt(value) || 0 : value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.item_id || formData.quantity_change === 0) {
      toast.error('Please select an item and enter a valid quantity');
      return;
    }
    
    if (!formData.reason || formData.reason.trim() === '') {
      toast.error('Please provide a reason for the adjustment');
      return;
    }
    
    try {
      const quantityChange = formData.adjustment_type === 'add' 
        ? formData.quantity_change 
        : -formData.quantity_change;
        
      // Create a stock movement for adjustment
      await api.post('/stocks/movements', {
        item_id: formData.item_id,
        movement_type: 'adjustment',
        quantity_change: quantityChange,
        reference_id: null,
        notes: `Stock adjustment: ${formData.reason}`
      });
      
      toast.success(`Stock ${formData.adjustment_type === 'add' ? 'added' : 'removed'} successfully`);
      setShowModal(false);
      setFormData({ item_id: '', quantity_change: 0, adjustment_type: 'add', reason: '' });
      fetchData(); // Refresh data
    } catch (error) {
      toast.error('Failed to adjust stock: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  const lowStockItems = stocks.filter(s => s.quantity < 100);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock & Inventory</h1>
          <p className="text-gray-600 mt-2">Monitor your inventory levels</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          Adjust Stock
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Items</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stocks.length}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Low Stock Alerts</p>
              <p className="text-2xl font-bold text-orange-600 mt-2">{lowStockItems.length}</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-full">
              <AlertCircle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Movements</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{movements.length}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('current')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'current'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Current Stock
            </button>
            <button
              onClick={() => setActiveTab('movements')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'movements'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Stock Movements
            </button>
          </nav>
        </div>

        {/* Current Stock Table */}
        {activeTab === 'current' && (
          <div className="mt-6 table-container">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Item Name</th>
                  <th className="table-header-cell">Type</th>
                  <th className="table-header-cell">Size</th>
                  <th className="table-header-cell">Grade</th>
                  <th className="table-header-cell">Quantity</th>
                  <th className="table-header-cell">Unit</th>
                  <th className="table-header-cell">Status</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {stocks.map((stock) => (
                  <tr key={stock.item_id}>
                    <td className="table-cell font-medium">{stock.item_name}</td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        stock.item_type === 'preform' ? 'bg-purple-100 text-purple-800' :
                        stock.item_type === 'bottle' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {stock.item_type}
                      </span>
                    </td>
                    <td className="table-cell">{stock.size}</td>
                    <td className="table-cell">
                      <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-semibold rounded">
                        Grade {stock.grade}
                      </span>
                    </td>
                    <td className="table-cell font-bold text-lg">{stock.quantity}</td>
                    <td className="table-cell text-gray-600">{stock.unit}</td>
                    <td className="table-cell">
                      {stock.quantity < 100 ? (
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full">
                          Low Stock
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                          In Stock
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Stock Movements Table */}
        {activeTab === 'movements' && (
          <div className="mt-6">
            {/* Filter by Item Name */}
            <div className="mb-4 flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Item Name</label>
                <select
                  value={movementFilterItem}
                  onChange={(e) => setMovementFilterItem(e.target.value)}
                  className="input w-full"
                >
                  <option value="">All Items</option>
                  {items.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.name} ({item.size}, Grade {item.grade})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="table-container">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Date</th>
                  <th className="table-header-cell">Item</th>
                  <th className="table-header-cell">Type</th>
                  <th className="table-header-cell">Change</th>
                  <th className="table-header-cell">Reference</th>
                  <th className="table-header-cell">Balance Before</th>
                  <th className="table-header-cell">Balance Available</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {movements
                  .filter(movement => !movementFilterItem || movement.item_id === movementFilterItem)
                  .map((movement) => (
                  <tr key={movement.id}>
                    <td className="table-cell">{new Date(movement.movement_date).toLocaleDateString()}</td>
                    <td className="table-cell">{movement.item_id}</td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        movement.movement_type === 'purchase' ? 'bg-green-100 text-green-800' :
                        movement.movement_type === 'sale' ? 'bg-blue-100 text-blue-800' :
                        movement.movement_type === 'production' ? 'bg-purple-100 text-purple-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {movement.movement_type}
                      </span>
                    </td>
                    <td className={`table-cell font-bold ${movement.quantity_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {movement.quantity_change > 0 ? '+' : ''}{movement.quantity_change}
                    </td>
                    <td className="table-cell text-gray-600">{movement.reference_id}</td>
                    <td className="table-cell">{movement.before_quantity}</td>
                    <td className="table-cell font-semibold">{movement.after_quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>
      
      {/* Add Stock Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Adjust Stock</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Item</label>
                <select
                  name="item_id"
                  value={formData.item_id}
                  onChange={handleInputChange}
                  className="input"
                  required
                >
                  <option value="">Select an item</option>
                  {items.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.name} ({item.size}, Grade {item.grade}) - Current: {item.current_stock || 0}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Type</label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="adjustment_type"
                      value="add"
                      checked={formData.adjustment_type === 'add'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <span className="text-green-600 font-medium">Add Stock</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="adjustment_type"
                      value="remove"
                      checked={formData.adjustment_type === 'remove'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <span className="text-red-600 font-medium">Remove Stock</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  name="quantity_change"
                  value={formData.quantity_change}
                  onChange={handleInputChange}
                  className="input"
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Reason (Required)</label>
                <textarea
                  name="reason"
                  value={formData.reason}
                  onChange={handleInputChange}
                  className="input"
                  rows="3"
                  placeholder="e.g., Physical count discrepancy, Damaged goods, etc."
                  required
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button type="submit" className="btn btn-primary flex-1">
                  Adjust Stock
                </button>
                <button
                  type="button"
                  onClick={() => { 
                    setShowModal(false); 
                    setFormData({ item_id: '', quantity_change: 0, adjustment_type: 'add', reason: '' });
                  }}
                  className="btn bg-gray-200 text-gray-800 hover:bg-gray-300 flex-1"
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

export default Stock;
