import React, { useState } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { DollarSign, X } from 'lucide-react';

const PaymentModal = ({ isOpen, onClose, transaction, transactionType, onSubmit }) => {
  const [paymentAmount, setPaymentAmount] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const remainingAmount = parseFloat(transaction.total_amount || transaction.total_price) - parseFloat(transaction.paid_amount || 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const amount = parseFloat(paymentAmount);
    if (amount <= 0 || amount > remainingAmount) {
      toast.error(`Please enter a valid amount (max: ${remainingAmount.toFixed(2)} PKR)`);
      return;
    }

    setLoading(true);
    try {
      await onSubmit(amount);
      setPaymentAmount('');
    } catch (error) {
      console.error('Payment submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="mb-6 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Bill Number:</span>
            <span className="font-medium">{transaction.bill_number}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total Amount:</span>
            <span className="font-medium">
              {(transaction.total_amount || transaction.total_price).toFixed(2)} PKR
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Paid Amount:</span>
            <span className="font-medium">
              {(transaction.paid_amount || 0).toFixed(2)} PKR
            </span>
          </div>
          <div className="flex justify-between text-sm border-t pt-2">
            <span className="text-gray-600 font-semibold">Remaining:</span>
            <span className="font-bold text-red-600">
              {remainingAmount.toFixed(2)} PKR
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment Amount (PKR)
            </label>
            <input
              type="number"
              step="0.01"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(e.target.value)}
              className="input"
              placeholder="Enter amount"
              max={remainingAmount}
              required
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum: {remainingAmount.toFixed(2)} PKR
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary flex-1 flex items-center justify-center gap-2"
            >
              <DollarSign className="w-4 h-4" />
              {loading ? 'Recording...' : 'Record Payment'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="btn bg-gray-200 text-gray-800 hover:bg-gray-300 flex-1"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PaymentModal;
