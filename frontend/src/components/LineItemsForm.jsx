import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
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
      
      {/* Input Row */}
      <div className="grid grid-cols-12 gap-3 mb-4 p-4 bg-white rounded-lg border-2 border-blue-200 shadow-md relative z-10">
        <div className="col-span-4 relative z-20">
          <label className="block text-sm font-bold mb-2 text-gray-800">Item *</label>
          <select
            value={currentItem.item_id}
            onChange={(e) => setCurrentItem({ ...currentItem, item_id: e.target.value })}
            className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900 cursor-pointer relative z-30"
            style={{ 
              pointerEvents: 'auto',
              zIndex: 30,
              appearance: 'none',
              backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27currentColor%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpolyline points=%276 9 12 15 18 9%27%3e%3c/polyline%3e%3c/svg%3e")',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 0.5rem center',
              backgroundSize: '1.5em 1.5em',
              paddingRight: '2.5rem'
            }}
          >
            <option value="">📦 Select item...</option>
            {items && items.length > 0 ? (
              items.map(item => (
                <option key={item.id} value={item.id}>
                  {item.name} (ID: {item.id}) - 📊 Stock: {item.current_stock}
                </option>
              ))
            ) : (
              <option disabled>No items available</option>
            )}
          </select>
        </div>

        <div className="col-span-2 relative z-20">
          <label className="block text-sm font-bold mb-2 text-gray-800">Qty *</label>
          <input
            type="number"
            value={currentItem.quantity}
            onChange={(e) => setCurrentItem({ ...currentItem, quantity: e.target.value })}
            placeholder="0"
            className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900"
            style={{ pointerEvents: 'auto', zIndex: 20 }}
            min="1"
          />
        </div>

        <div className="col-span-2 relative z-20">
          <label className="block text-sm font-bold mb-2 text-gray-800">Unit Price *</label>
          <input
            type="number"
            value={currentItem.unit_price}
            onChange={(e) => setCurrentItem({ ...currentItem, unit_price: e.target.value })}
            placeholder="0.00"
            className="w-full p-3 border-2 border-gray-300 rounded text-sm bg-white text-gray-900"
            style={{ pointerEvents: 'auto', zIndex: 20 }}
            step="0.01"
            min="0"
          />
        </div>

        <div className="col-span-4 flex items-end relative z-20">
          <button
            type="button"
            onClick={handleAddItem}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded flex items-center justify-center gap-2 text-sm font-medium"
            style={{ zIndex: 20 }}
          >
            <Plus size={16} /> Add Item
          </button>
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
