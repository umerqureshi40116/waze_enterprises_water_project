import api from '../api/axios';

/**
 * Generate incremental bill numbers without date
 * Format: PREFIX-XXX (e.g., SALE-001, PURCH-001)
 * The number increments sequentially starting from 1
 * @param {string} prefix - Bill number prefix (e.g., 'SALE', 'PURCH')
 * @param {string} selectedDate - Optional date string (not used in format, kept for compatibility)
 */

export const generateBillNumber = async (prefix = 'BILL', selectedDate = null) => {
  try {
    // Fetch the count of existing records from the backend
    const response = await api.get(`/reports/count/${prefix.toLowerCase()}`);
    const count = response.data.count || 0;
    const nextNumber = count + 1;
    
    // Format with leading zeros (e.g., 001, 002, etc.)
    const paddedNumber = String(nextNumber).padStart(3, '0');
    
    return `${prefix}-${paddedNumber}`;
  } catch (error) {
    console.error('Error generating bill number:', error);
    // Fallback to a simple format if API fails
    const random = Math.floor(Math.random() * 1000);
    return `${prefix}-${String(random).padStart(3, '0')}`;
  }
};

// Specific generators
export const generateSaleNumber = async (selectedDate = null) => await generateBillNumber('SALE', selectedDate);
export const generatePurchaseNumber = async (selectedDate = null) => await generateBillNumber('PURCH', selectedDate);
export const generateBlowId = async (selectedDate = null) => await generateBillNumber('BLOW', selectedDate);
export const generateWasteId = async (selectedDate = null) => await generateBillNumber('WASTE', selectedDate);
export const generateExpenseId = async (selectedDate = null) => await generateBillNumber('EXP', selectedDate);
