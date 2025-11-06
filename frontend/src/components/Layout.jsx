import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  ShoppingCart,
  TrendingUp,
  Package,
  Trash2,
  Archive,
  Users,
  UserCheck,
  FileText,
  LogOut,
  Droplet,
  UserCog,
  Box,
  DollarSign
} from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Purchases', href: '/purchases', icon: ShoppingCart },
    { name: 'Sales', href: '/sales', icon: TrendingUp },
    { name: 'Blow Process', href: '/blow-process', icon: Package },
    { name: 'Waste Recovery', href: '/waste', icon: Trash2 },
    { name: 'Operating Expenses', href: '/extra-expenditures', icon: DollarSign },
    { name: 'Stock', href: '/stock', icon: Archive },
    { name: 'Items', href: '/items', icon: Box },
    { name: 'Suppliers', href: '/suppliers', icon: Users },
    { name: 'Customers', href: '/customers', icon: UserCheck },
  ];

  // Add admin-only options
  if (user?.role === 'admin') {
    navigation.push({ name: 'Reports', href: '/reports', icon: FileText });
    navigation.push({ name: 'Users', href: '/users', icon: UserCog });
  }

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-20 border-b border-gray-200">
            <Droplet className="w-8 h-8 text-primary-600 mr-2" />
            <h1 className="text-xl font-bold text-gray-900">Waze Enterprises</h1>
          </div>

          {/* User Info */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-primary-600 font-semibold">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                        isActive(item.href)
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={logout}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
