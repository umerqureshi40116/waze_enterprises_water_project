import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { Plus, Building2, Phone, MapPin, FileText, Trash2, Edit2 } from 'lucide-react';

const Suppliers = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ id: '', name: '', contact: '', address: '', notes: '' });

  useEffect(() => { fetchSuppliers(); }, []);

  const fetchSuppliers = async () => {
    try {
      const res = await api.get('/suppliers');
      setSuppliers(res.data);
    } catch (error) {
      toast.error('Failed to fetch suppliers');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/suppliers', formData);
      toast.success('Supplier added successfully');
      setShowModal(false);
      fetchSuppliers();
      setFormData({ id: '', name: '', contact: '', address: '', notes: '' });
    } catch (error) {
      toast.error('Failed to add supplier');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Suppliers</h1>
          <p className="text-gray-600 mt-2">Manage your suppliers</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" /> Add Supplier
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {suppliers.map((supplier) => (
          <div key={supplier.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <Building2 className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">{supplier.name}</h3>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">{supplier.id}</span>
              </div>
              
              {supplier.contact && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4 text-green-600" />
                  <span>{supplier.contact}</span>
                </div>
              )}
              
              {supplier.address && (
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-4 h-4 text-red-600" />
                  <span>{supplier.address}</span>
                </div>
              )}
              
              {supplier.notes && (
                <div className="flex items-start gap-2 text-gray-600 pt-2 border-t mt-2">
                  <FileText className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span className="text-xs italic">{supplier.notes}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Supplier</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div><label className="block text-sm font-medium text-gray-700 mb-2">ID</label><input type="text" value={formData.id} onChange={(e) => setFormData({...formData, id: e.target.value})} className="input" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">Name</label><input type="text" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className="input" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">Contact</label><input type="text" value={formData.contact} onChange={(e) => setFormData({...formData, contact: e.target.value})} className="input" /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">Address</label><input type="text" value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} className="input" /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">Notes</label><textarea value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} className="input" rows="2"></textarea></div>
              <div className="flex gap-4 pt-4">
                <button type="submit" className="btn btn-primary flex-1">Add</button>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Suppliers;
