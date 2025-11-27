import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

const ItemSelect = ({ items, value, onChange, placeholder = "Type or select item..." }) => {
  const [inputValue, setInputValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [filteredItems, setFilteredItems] = useState(items || []);
  const containerRef = useRef(null);

  // Initialize input value from prop
  useEffect(() => {
    if (value) {
      setInputValue(value);
    }
  }, [value]);

  // Handle input change and filter items
  const handleInputChange = (e) => {
    const val = e.target.value;
    setInputValue(val);
    setIsOpen(true);

    // Filter items by name (case-insensitive)
    if (val.trim()) {
      const filtered = items.filter(item =>
        item.name.toLowerCase().includes(val.toLowerCase())
      );
      setFilteredItems(filtered);
    } else {
      setFilteredItems(items);
    }
  };

  // Handle item selection from dropdown
  const handleSelectItem = (item) => {
    console.log('Item selected:', item.name);
    setInputValue(item.name);
    onChange(item.name); // Pass the item name to parent
    setIsOpen(false);
  };

  // Handle Enter key for manual entry
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      console.log('Manual entry:', inputValue);
      onChange(inputValue.trim());
      setIsOpen(false);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      <div className="relative">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="input w-full pr-10"
          autoComplete="off"
        />
        <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>

      {/* Debug info */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 text-xs text-gray-500 px-2 py-1">
          {items && items.length > 0 ? `${filteredItems.length} items found` : '❌ No items loaded'}
        </div>
      )}

      {/* Dropdown list */}
      {isOpen && filteredItems.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onMouseDown={(e) => {
                e.preventDefault(); // Prevent blur before click fires
                handleSelectItem(item);
              }}
              className="w-full text-left px-4 py-2 hover:bg-primary-50 transition-colors border-b border-gray-100 last:border-b-0"
            >
              <div className="font-medium text-gray-900">{item.name}</div>
              <div className="text-xs text-gray-500">
                {[item.type, item.size, item.grade].filter(Boolean).join(' • ')}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* No results message */}
      {isOpen && inputValue.trim() && filteredItems.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 p-4 text-center text-gray-500 text-sm">
          <p>No items found</p>
          <p className="text-xs text-gray-400 mt-1">Press Enter to create "{inputValue}"</p>
        </div>
      )}
    </div>
  );
};

export default ItemSelect;