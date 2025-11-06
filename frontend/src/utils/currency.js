export const formatCurrency = (value, locale = 'en-PK', currency = 'PKR') => {
  if (value == null || isNaN(value)) return 'N/A';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatCurrencySimple = (value) => {
  if (value == null || isNaN(value)) return 'N/A';
  // Format as number with commas, no decimals for whole numbers
  const num = parseFloat(value);
  return new Intl.NumberFormat('en-PK', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(num);
};

export const formatNumber = (value) => {
  if (value == null || isNaN(value)) return 'N/A';
  return new Intl.NumberFormat('en-PK').format(value);
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'N/A';
  
  const day = date.getDate();
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[date.getMonth()];
  const year = date.getFullYear().toString().slice(-2);
  
  return `${day}-${month}-${year}`;
};
