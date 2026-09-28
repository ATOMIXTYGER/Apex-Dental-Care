import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { OnlinePaymentModal } from '../components/billing/OnlinePaymentModal';
import { billingApi } from '../api/billing';
import { Invoice } from '../types';

vi.mock('../api/billing', () => ({
  billingApi: {
    createOnlineOrder: vi.fn(),
    verifyOnlinePayment: vi.fn(),
    downloadReceiptPdf: vi.fn(),
  },
}));

describe('OnlinePaymentModal Component', () => {
  const mockInvoice: Invoice = {
    id: 101,
    patient_id: 1,
    invoice_number: 'INV-2026-001',
    issue_date: '2026-09-28',
    due_date: '2026-10-05',
    subtotal: 10000,
    tax_amount: 0,
    discount_amount: 0,
    total: 10000,
    paid_amount: 3000,
    balance: 7000,
    status: 'partially_paid',
    notes: 'Dental treatment',
    created_at: '2026-09-28T10:00:00Z',
    items: [],
    payments: [],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders modal with correct invoice information and outstanding balance', () => {
    render(
      <OnlinePaymentModal
        invoice={mockInvoice}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Online Payment Gateway')).toBeInTheDocument();
    expect(screen.getByText(/INV-2026-001/i)).toBeInTheDocument();
    expect(screen.getByText(/256-Bit SSL Encrypted Payment Gateway/i)).toBeInTheDocument();
    expect(screen.getByText('Full Balance')).toBeInTheDocument();
    expect(screen.getAllByText('₹7,000.00').length).toBeGreaterThanOrEqual(1);
  });

  it('switches to custom partial amount and validates boundaries', () => {
    render(
      <OnlinePaymentModal
        invoice={mockInvoice}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    const partialBtn = screen.getByText('Partial Payment');
    fireEvent.click(partialBtn);

    // Initial partial amount defaults to half balance (3500)
    const amountInput = screen.getByDisplayValue('3500');
    expect(amountInput).toBeInTheDocument();

    // Set an amount higher than balance
    fireEvent.change(amountInput, { target: { value: '8500' } });
    const checkoutBtn = screen.getByRole('button', { name: /Pay ₹8,500.00 Online/i });
    fireEvent.click(checkoutBtn);

    expect(
      screen.getByText(/Payment amount cannot exceed outstanding balance/i)
    ).toBeInTheDocument();

    // Valid partial amount
    fireEvent.change(amountInput, { target: { value: '2500' } });
    const updatedCheckoutBtn = screen.getByRole('button', { name: /Pay ₹2,500.00 Online/i });
    expect(updatedCheckoutBtn).toBeInTheDocument();
  });

  it('calls backend createOnlineOrder with correct payload when checkout initiated', async () => {
    (billingApi.createOnlineOrder as any).mockResolvedValueOnce({
      internal_payment_id: 55,
      order_id: 'order_test_999',
      amount: 7000,
      currency: 'INR',
      key_id: 'rzp_test_sample',
      provider: 'razorpay',
      status: 'PENDING',
      clinic_name: 'Apex Dental Care',
      patient_name: 'John Doe',
      patient_email: 'john@example.com',
      patient_phone: '9876543210',
    });

    // Mock window.Razorpay
    const mockOpen = vi.fn();
    (window as any).Razorpay = vi.fn().mockImplementation(() => ({
      open: mockOpen,
      on: vi.fn(),
    }));

    render(
      <OnlinePaymentModal
        invoice={mockInvoice}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    const checkoutBtn = screen.getByRole('button', { name: /Pay ₹7,000.00 Online/i });
    fireEvent.click(checkoutBtn);

    await waitFor(() => {
      expect(billingApi.createOnlineOrder).toHaveBeenCalledWith(
        101,
        7000,
        expect.stringMatching(/^ord-101-/)
      );
    });
  });
});
