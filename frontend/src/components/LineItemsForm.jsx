import React, { useState } from 'react';
import { Plus, Trash2, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { formatCurrency } from '../utils/currency';

const LineItemsForm = ({ 
  lineItems, 
  onLineItemsChange, 
  items,
  isSale = false  // If true, show blow_price column
}) => {
  const [currentItem, setCurrentItem] = useState({
    item_id: '',
    quantity: '',
    unit_price: ''
  });
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Add a new line item
  const handleAddItem = () => {
    if (!currentItem.item_id) {
      toast.error('Please select an item');
      return;
    }
    if (!currentItem.quantity || parseInt(currentItem.quantity) <= 0) {
      toast.error('Quantity must be greater than 0');
      return;
    }
    if (!currentItem.unit_price || parseFloat(currentItem.unit_price) <= 0) {
      toast.error('Unit price must be greater than 0');
      return;
    }

    const newItem = {
      item_id: currentItem.item_id,
      quantity: parseInt(currentItem.quantity),
      unit_price: parseFloat(currentItem.unit_price)
    };

    onLineItemsChange([...lineItems, newItem]);
    setCurrentItem({
      item_id: '',
      quantity: '',
      unit_price: ''
    });
    toast.success('Item added');
  };

  // Remove a line item
  const handleRemoveItem = (index) => {
    onLineItemsChange(lineItems.filter((_, i) => i !== index));
    toast.success('Item removed');
  };

  // Calculate total for a line item
  const getLineTotal = (item) => {
    return item.quantity * item.unit_price;
  };

  // Calculate grand total
  const getGrandTotal = () => {
    return lineItems.reduce((sum, item) => sum + getLineTotal(item), 0);
  };

  const getItemName = (itemId) => {
    const item = items.find(i => i.id === itemId);
    return item ? item.name : itemId;
  };

  return (
    <div className="w-full border-2 border-blue-300 rounded-lg p-4 bg-blue-50 shadow-sm">
      <h3 className="text-lg font-bold mb-4 text-blue-900">📦 Line Items</h3>
      
      {/* Input Row - Simplified Layout */}
      <div className="p-4 bg-white rounded-lg border-2 border-blue-200 shadow-md mb-4">
        <div className="space-y-3">
          {/* Item Selection Row - CUSTOM DROPDOWN */}
          <div className="w-full">
            <label className="block text-sm font-bold mb-2 text-gray-800">Item *</label>
            <div className="relative">
              {/* Custom Dropdown Button */}
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900 text-left flex items-center justify-between hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                style={{ minHeight: '44px' }}
              >
                <span>
                  {currentItem.item_id 
                    ? `${items.find(i => i.id === currentItem.item_id)?.name || 'Unknown'}`
                    : '📦 Select item...'
                  }
                </span>
                <ChevronDown size={18} className={`transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Custom Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border-2 border-gray-300 rounded shadow-lg z-50 max-h-64 overflow-y-auto">
                  <button
                    type="button"
                    onClick={() => {
                      setCurrentItem({ ...currentItem, item_id: '' });
                      setIsDropdownOpen(false);
                    }}
                    className="w-full text-left p-3 hover:bg-blue-100 text-gray-900 border-b"
                  >
                    📦 Select item...
                  </button>
                  
                  {items && items.length > 0 ? (
                    items.map(item => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => {
                          setCurrentItem({ ...currentItem, item_id: item.id });
                          setIsDropdownOpen(false);
                        }}
                        className="w-full text-left p-3 hover:bg-blue-100 text-gray-900 border-b transition"
                      >
                        <div className="font-medium">{item.name}</div>
                        <div className="text-xs text-gray-500">ID: {item.id} | Stock: {item.current_stock}</div>
                      </button>
                    ))
                  ) : (
                    <div className="w-full p-3 text-gray-500 text-sm">No items available</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Quantity and Price Row */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-bold mb-2 text-gray-800">Qty *</label>
              <input
                type="number"
                value={currentItem.quantity}
                onChange={(e) => setCurrentItem({ ...currentItem, quantity: e.target.value })}
                placeholder="0"
                className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900"
                style={{ pointerEvents: 'auto', minHeight: '44px' }}
                min="1"
              />
            </div>

            <div>
              <label className="block text-sm font-bold mb-2 text-gray-800">Unit Price *</label>
              <input
                type="number"
                value={currentItem.unit_price}
                onChange={(e) => setCurrentItem({ ...currentItem, unit_price: e.target.value })}
                placeholder="0.00"
                className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900"
                style={{ pointerEvents: 'auto', minHeight: '44px' }}
                step="0.01"
                min="0"
              />
            </div>

            <div className="flex flex-col justify-end">
              <button
                type="button"
                onClick={handleAddItem}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded flex items-center justify-center gap-2 text-sm font-medium"
              >
                <Plus size={16} /> Add
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Line Items Table */}
      {lineItems.length > 0 && (
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-xs">
            <thead className="bg-blue-100 border-b">
              <tr>
                <th className="text-left p-2">Item</th>
                <th className="text-right p-2">Qty</th>
                <th className="text-right p-2">Unit Price</th>
                <th className="text-right p-2">Line Total</th>
                <th className="text-center p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map((item, index) => (
                <tr key={index} className="border-b hover:bg-gray-100">
                  <td className="p-2 font-medium">{getItemName(item.item_id)}</td>
                  <td className="text-right p-2">{item.quantity}</td>
                  <td className="text-right p-2">Rs {item.unit_price.toLocaleString()}</td>
                  <td className="text-right p-2 font-semibold text-blue-600">
                    Rs {getLineTotal(item).toLocaleString()}
                  </td>
                  <td className="text-center p-2">
                    <button
                      type="button"
                      onClick={() => handleRemoveItem(index)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              <tr className="bg-blue-50 font-bold">
                <td colSpan={3} className="text-right p-2">
                  TOTAL:
                </td>
                <td className="text-right p-2 text-blue-600">
                  Rs {getGrandTotal().toLocaleString()}
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {lineItems.length === 0 && (
        <div className="text-center py-6 text-gray-400">
          <p>No items added yet. Use the form above to add line items.</p>
        </div>
      )}
    </div>
  );
};

export default LineItemsForm;
