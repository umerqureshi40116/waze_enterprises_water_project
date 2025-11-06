import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const Pagination = ({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  pageSize, 
  onPageSizeChange,
  totalRecords 
}) => {
  const pageSizeOptions = [10, 25, 50, 100];
  
  const startRecord = (currentPage - 1) * pageSize + 1;
  const endRecord = Math.min(currentPage * pageSize, totalRecords);

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePageSizeChange = (newSize) => {
    onPageSizeChange(newSize);
    onPageChange(1); // Reset to first page
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      // Calculate range around current page
      const startPage = Math.max(2, currentPage - 1);
      const endPage = Math.min(totalPages - 1, currentPage + 1);
      
      if (startPage > 2) pages.push('...');
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      if (endPage < totalPages - 1) pages.push('...');
      
      // Always show last page
      pages.push(totalPages);
    }
    
    return pages;
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-white border-t border-gray-200 rounded-b-lg">
      {/* Records info */}
      <div className="text-sm text-gray-600">
        Showing {totalRecords > 0 ? startRecord : 0} to {endRecord} of{' '}
        <span className="font-semibold text-gray-900">{totalRecords}</span> records
      </div>

      {/* Page size selector */}
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">Per page:</label>
        <select
          value={pageSize}
          onChange={(e) => handlePageSizeChange(Number(e.target.value))}
          className="input text-sm w-20"
        >
          {pageSizeOptions.map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center gap-1">
        {/* Previous button */}
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className="p-2 rounded-md border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Previous page"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        {/* Page numbers */}
        <div className="flex items-center gap-1">
          {getPageNumbers().map((page, idx) => (
            <button
              key={idx}
              onClick={() => {
                if (typeof page === 'number') {
                  onPageChange(page);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }
              }}
              disabled={page === '...'}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                page === currentPage
                  ? 'bg-primary-600 text-white'
                  : page === '...'
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {page}
            </button>
          ))}
        </div>

        {/* Next button */}
        <button
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className="p-2 rounded-md border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Next page"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Page info */}
      <div className="text-sm text-gray-600">
        Page <span className="font-semibold text-gray-900">{currentPage}</span> of{' '}
        <span className="font-semibold text-gray-900">{totalPages}</span>
      </div>
    </div>
  );
};

export default Pagination;
