/**
 * India Metric and Currency Formatting Utilities
 * Standardizes INR (₹) currency representations and Indian metric formatting across the application.
 */

export const formatINR = (amount: number | string | undefined | null, includeDecimals = true): string => {
  if (amount === undefined || amount === null || isNaN(Number(amount))) {
    return includeDecimals ? '₹0.00' : '₹0';
  }
  const num = Number(amount);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: includeDecimals ? 2 : 0,
    maximumFractionDigits: includeDecimals ? 2 : 0,
  }).format(num);
};

export const formatCurrency = formatINR;

export const formatDateIN = (dateStr: string | Date | undefined | null): string => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return String(dateStr);
  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

export const formatDateTimeIN = (dateStr: string | Date | undefined | null): string => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return String(dateStr);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
};
