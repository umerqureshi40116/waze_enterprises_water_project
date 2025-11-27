import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { formatCurrency } from '../utils/currency';
import ItemSelect from './ItemSelect';
import api from '../api/axios';

const LineItemsForm = ({ 
  lineItems, 
  onLineItemsChange, 
  items,
  isSale = false,  // If true, show blow_price column
  onNewItemCreated = null  // Callback when a new item is created
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
    console.log('item_id raw:', currentItem.item_id);
    console.log('item_id type:', typeof currentItem.item_id);
    
    // Simpler validation - ensure string conversion
    const itemId = String(currentItem.item_id || '').trim();
    const qty = parseInt(currentItem.quantity);
    const price = parseFloat(currentItem.unit_price);
    
    console.log('✅ Parsed values:', { itemId, itemIdType: typeof itemId, qty, price });
    
    if (!itemId || itemId === '') {
      console.log('❌ FAIL: item_id is empty or blank');
      console.log('   itemId:', `"${itemId}"`);
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
    const updatedItems = [...lineItems, newItem];
    console.log('📤 CALLING onLineItemsChange with:', updatedItems);
    console.log('📤 Current lineItems length:', lineItems.length);
    console.log('📤 New lineItems length:', updatedItems.length);
    onLineItemsChange(updatedItems);
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
    const itemIdStr = String(itemId);
    const item = items.find(i => String(i.id) === itemIdStr);
    return item ? item.name : itemId;
  };

  return (
    <div className="w-full border-2 border-blue-300 rounded-lg p-4 bg-blue-50 shadow-sm">
      <h3 className="text-lg font-bold mb-4 text-blue-900">📦 Line Items</h3>
      
      {/* Input Row - Compact when items exist */}
      <div className="p-3 bg-white rounded-lg border-2 border-blue-200 shadow-md mb-4">
        <div className={lineItems.length > 0 ? "space-y-2" : "space-y-3"}>
          {/* Item Selection Row */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Item * (type to search or add new)</label>
            <ItemSelect
              items={items}
              value={currentItem.item_id ? items.find(i => i.id === currentItem.item_id)?.name || '' : ''}
              onChange={async (selectedName) => {
                console.log('🔄 ItemSelect CHANGED:', selectedName);
                
                try {
                  // Try to find existing item by name
                  const existingItem = items.find(i => i.name.toLowerCase() === selectedName.toLowerCase());
                  
                  if (existingItem) {
                    console.log('✅ Found existing item:', existingItem.id);
                    setCurrentItem({ ...currentItem, item_id: existingItem.id });
                  } else {
                    // Auto-create new item
                    console.log('📝 Creating new item:', selectedName);
                    const response = await api.post('/stocks/items/auto-create', { name: selectedName });
                    console.log('✅ Auto-create response:', response.data);
                    const newItem = response.data.item;
                    if (!newItem || !newItem.id) {
                      throw new Error('Invalid response: missing item data');
                    }
                    console.log('✅ Auto-created item:', newItem.id);
                    setCurrentItem({ ...currentItem, item_id: newItem.id });
                    
                    // Call parent callback to update items list
                    if (onNewItemCreated) {
                      onNewItemCreated(newItem);
                      console.log('✅ Called onNewItemCreated callback');
                    }
                  }
                } catch (error) {
                  console.error('❌ Full error object:', error);
                  console.error('❌ Error response data:', error.response?.data);
                  console.error('❌ Error message:', error.message);
                  toast.error(error.response?.data?.detail || error.message || 'Error processing item selection');
                }
              }}
              placeholder="📦 Select or type item name..."
            />
          </div>

          {/* Quantity and Price Row - Compact */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Qty</label>
              <input
                type="number"
                value={currentItem.quantity}
                onChange={(e) => setCurrentItem({ ...currentItem, quantity: e.target.value })}
                placeholder="0"
                className="input text-sm py-1"
                min="1"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Price</label>
              <input
                type="number"
                value={currentItem.unit_price}
                onChange={(e) => setCurrentItem({ ...currentItem, unit_price: e.target.value })}
                placeholder="0.00"
                className="input text-sm py-1"
                step="0.01"
                min="0"
              />
            </div>

            <div className="flex flex-col justify-end">
              <button
                type="button"
                onClick={handleAddItem}
                className="btn btn-primary text-sm py-1"
              >
                <Plus size={14} className="inline mr-1" /> Add
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Line Items Table - More Compact */}
      {lineItems.length > 0 && (
        <div className="overflow-x-auto mb-2">
          <table className="w-full text-xs">
            <thead className="bg-blue-100 border-b">
              <tr>
                <th className="text-left p-1 text-xs">Item</th>
                <th className="text-right p-1 text-xs">Qty</th>
                <th className="text-right p-1 text-xs">Price</th>
                <th className="text-right p-1 text-xs">Total</th>
                <th className="text-center p-1 text-xs">🗑️</th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map((item, index) => (
                <tr key={index} className="border-b hover:bg-gray-100">
                  <td className="p-1 text-xs font-medium">{getItemName(item.item_id)}</td>
                  <td className="text-right p-1 text-xs">{item.quantity}</td>
                  <td className="text-right p-1 text-xs">Rs {item.unit_price.toLocaleString()}</td>
                  <td className="text-right p-1 text-xs font-semibold text-blue-600">
                    Rs {getLineTotal(item).toLocaleString()}
                  </td>
                  <td className="text-center p-1">
                    <button
                      type="button"
                      onClick={() => handleRemoveItem(index)}
                      className="text-red-500 hover:text-red-700 text-xs"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
              <tr className="bg-blue-50 font-bold text-xs">
                <td colSpan={3} className="text-right p-1">
                  TOTAL:
                </td>
                <td className="text-right p-1 text-blue-600">
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
        <div className="text-center py-3 text-gray-400 text-sm">
          <p>No items yet. Add line items above.</p>
        </div>
      )}
    </div>
  );
};

export default LineItemsForm;