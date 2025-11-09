import React, { useState, useEffect } from 'react';
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

  // Debug: Log items on mount and when they change
  useEffect(() => {
    console.log('📦 LineItemsForm - Items prop received:', items);
    console.log('📦 LineItemsForm - Items count:', items?.length);
    if (items && items.length > 0) {
      console.log('📦 First item:', items[0]);
    }
  }, [items]);

  // Log currentItem state changes
  useEffect(() => {
    console.log('💾 CurrentItem state updated:', currentItem);
  }, [currentItem]);

  // Add a new line item
  const handleAddItem = () => {
    console.log('➕ ADD BUTTON CLICKED');
    console.log('currentItem state:', JSON.stringify(currentItem));
    console.log('item_id:', `"${currentItem.item_id}"`);
    console.log('item_id length:', currentItem.item_id.length);
    console.log('item_id trimmed:', `"${currentItem.item_id?.trim()}"`);
    
    // Simpler validation
    const itemId = currentItem.item_id?.trim();
    const qty = parseInt(currentItem.quantity);
    const price = parseFloat(currentItem.unit_price);
    
    console.log('Parsed values:', { itemId, qty, price });
    
    if (!itemId) {
      console.log('❌ FAIL: item_id is empty');
      toast.error('Please select an item');
      return;
    }
    
    if (!currentItem.quantity || isNaN(qty) || qty <= 0) {
      console.log('❌ FAIL: Invalid quantity:', currentItem.quantity);
      toast.error('Quantity must be greater than 0');
      return;
    }
    
    if (!currentItem.unit_price || isNaN(price) || price <= 0) {
      console.log('❌ FAIL: Invalid price:', currentItem.unit_price);
      toast.error('Unit price must be greater than 0');
      return;
    }

    console.log('✅ ALL VALIDATIONS PASSED');
    
    const newItem = {
      item_id: itemId,
      quantity: qty,
      unit_price: price
    };

    console.log('✅ Adding item:', newItem);
    onLineItemsChange([...lineItems, newItem]);
    setCurrentItem({
      item_id: '',
      quantity: '',
      unit_price: ''
    });
    console.log('✅ Form reset');
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
          {/* Item Selection Row - NATIVE SELECT WITH INPUT CLASS */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Item *</label>
            <div style={{ position: 'relative', zIndex: 100 }}>
              <select
                value={currentItem.item_id}
                onChange={(e) => {
                  console.log('🔄 SELECT CHANGED EVENT FIRED');
                  console.log('   New value:', `"${e.target.value}"`);
                  console.log('   Selected index:', e.target.selectedIndex);
                  console.log('   Selected option:', e.target.options[e.target.selectedIndex]?.text);
                  setCurrentItem({ ...currentItem, item_id: e.target.value });
                }}
                className="input"
                required
                style={{ position: 'relative', zIndex: 101 }}
              >
              <option value="">📦 Select Item...</option>
              {items && items.length > 0 ? (
                items.map(item => (
                  <option key={item.id} value={item.id}>
                    {item.name} (ID: {item.id}) - Stock: {item.current_stock}
                  </option>
                ))
              ) : (
                <option disabled>No items available</option>
              )}
              </select>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              ✓ {items?.length || 0} items loaded | Selected: <strong>{currentItem.item_id || 'none'}</strong>
            </div>
          </div>

          {/* Quantity and Price Row */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Qty *</label>
              <input
                type="number"
                value={currentItem.quantity}
                onChange={(e) => setCurrentItem({ ...currentItem, quantity: e.target.value })}
                placeholder="0"
                className="input"
                min="1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Unit Price *</label>
              <input
                type="number"
                value={currentItem.unit_price}
                onChange={(e) => setCurrentItem({ ...currentItem, unit_price: e.target.value })}
                placeholder="0.00"
                className="input"
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className="flex flex-col justify-end">
              <button
                type="button"
                onClick={handleAddItem}
                className="btn btn-primary"
              >
                <Plus size={16} className="inline mr-1" /> Add
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
