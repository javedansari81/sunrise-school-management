/**
 * Comprehensive tests for the ExpenseManagement component
 * Tests CRUD operations, filtering, and configuration integration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ExpenseManagement from '../../src/pages/admin/ExpenseManagement';
import { ConfigurationProvider } from '../../src/contexts/ConfigurationContext';
import * as api from '../../src/services/api';

// Mock the API
jest.mock('../services/api', () => ({
  expenseAPI: {
    getExpenses: jest.fn(),
    createExpense: jest.fn(),
    updateExpense: jest.fn(),
    deleteExpense: jest.fn(),
    approveExpense: jest.fn(),
    getStatistics: jest.fn(),
  }
}));

const mockedAPI = api as jest.Mocked<typeof api>;

// Mock configuration data
const mockConfiguration = {
  expense_categories: [
    { id: 1, name: 'Infrastructure', is_active: true },
    { id: 2, name: 'Maintenance', is_active: true },
    { id: 3, name: 'Utilities', is_active: true },
    { id: 4, name: 'Supplies', is_active: true }
  ],
  expense_statuses: [
    { id: 1, name: 'Pending', color_code: '#ff9800', is_active: true },
    { id: 2, name: 'Approved', color_code: '#4caf50', is_active: true },
    { id: 3, name: 'Rejected', color_code: '#f44336', is_active: true },
    { id: 4, name: 'Paid', color_code: '#2196f3', is_active: true }
  ],
  payment_methods: [
    { id: 1, name: 'Cash', is_active: true },
    { id: 2, name: 'Cheque', is_active: true },
    { id: 3, name: 'Bank Transfer', is_active: true },
    { id: 4, name: 'UPI', is_active: true }
  ],
  session_years: [
    { id: 4, name: '2024-25', is_current: true, is_active: true }
  ]
};

// Mock expense data
const mockExpenses = [
  {
    id: 1,
    expense_date: '2024-01-15',
    expense_category_id: 1,
    expense_category_name: 'Infrastructure',
    description: 'Office furniture purchase',
    amount: 25000.00,
    tax_amount: 4500.00,
    total_amount: 29500.00,
    vendor_name: 'ABC Furniture Ltd',
    vendor_contact: '9876543210',
    payment_method_id: 3,
    payment_method_name: 'Bank Transfer',
    expense_status_id: 2,
    expense_status_name: 'Approved',
    expense_status_color: '#4caf50',
    priority: 'Medium',
    is_emergency: false,
    requested_by: 1,
    requester_name: 'John Doe',
    approved_by: 2,
    approver_name: 'Admin User',
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    expense_date: '2024-01-20',
    expense_category_id: 2,
    expense_category_name: 'Maintenance',
    description: 'HVAC system repair',
    amount: 15000.00,
    tax_amount: 2700.00,
    total_amount: 17700.00,
    vendor_name: 'Cool Air Services',
    vendor_contact: '9876543211',
    payment_method_id: 2,
    payment_method_name: 'Cheque',
    expense_status_id: 1,
    expense_status_name: 'Pending',
    expense_status_color: '#ff9800',
    priority: 'High',
    is_emergency: false,
    requested_by: 1,
    requester_name: 'John Doe',
    approved_by: null,
    approver_name: null,
    created_at: '2024-01-20T14:30:00Z'
  }
];

const mockStatistics = {
  total_expenses: 2,
  approved_expenses: 1,
  pending_expenses: 1,
  rejected_expenses: 0,
  total_amount: 47200.00,
  approved_amount: 29500.00,
  pending_amount: 17700.00,
  category_breakdown: [
    { category: 'Infrastructure', count: 1, amount: 29500.00 },
    { category: 'Maintenance', count: 1, amount: 17700.00 }
  ]
};

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = createTheme();
  
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ConfigurationProvider>
          {children}
        </ConfigurationProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('ExpenseManagement Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default API responses
    (mockedAPI.expenseAPI.getExpenses as jest.Mock).mockResolvedValue({
      expenses: mockExpenses,
      total: 2,
      page: 1,
      per_page: 20,
      total_pages: 1,
      summary: { total_amount: 47200.00, pending_amount: 17700.00, approved_amount: 29500.00, count: 2 }
    });

    (mockedAPI.expenseAPI.getStatistics as jest.Mock).mockResolvedValue(mockStatistics);
    
    // Mock configuration context
    jest.spyOn(require('../contexts/ConfigurationContext'), 'useConfiguration').mockReturnValue({
      configuration: mockConfiguration,
      isLoading: false,
      isLoaded: true,
      error: null,
      loadConfiguration: jest.fn(),
      refreshConfiguration: jest.fn(),
      clearError: jest.fn(),
      getUserTypes: jest.fn(() => []),
      getSessionYears: jest.fn(() => []),
      getCurrentSessionYear: jest.fn(() => mockConfiguration.session_years[0]),
      getGenders: jest.fn(() => []),
      getClasses: jest.fn(() => []),
      getPaymentTypes: jest.fn(() => []),
      getPaymentStatuses: jest.fn(() => []),
      getPaymentMethods: jest.fn(() => mockConfiguration.payment_methods),
      getLeaveTypes: jest.fn(() => []),
      getLeaveStatuses: jest.fn(() => []),
      getExpenseCategories: jest.fn(() => mockConfiguration.expense_categories),
      getExpenseStatuses: jest.fn(() => mockConfiguration.expense_statuses),
      getEmploymentStatuses: jest.fn(() => []),
      getQualifications: jest.fn(() => [])
    });
  });

  test('renders expense management page with statistics', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Check if the page title is rendered
    expect(screen.getByText('Expense Management')).toBeInTheDocument();

    // Wait for statistics to load
    await waitFor(() => {
      expect(screen.getByText('Total Expenses')).toBeInTheDocument();
      expect(screen.getByText('Pending Approval')).toBeInTheDocument();
      expect(screen.getByText('Approved')).toBeInTheDocument();
      expect(screen.getByText('Rejected')).toBeInTheDocument();
    });

    // Check if Add Expense button is present
    expect(screen.getByText('Add Expense')).toBeInTheDocument();
  });

  test('displays expense list with proper data', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Wait for expenses to load
    await waitFor(() => {
      expect(screen.getByText('Office furniture purchase')).toBeInTheDocument();
      expect(screen.getByText('HVAC system repair')).toBeInTheDocument();
    });

    // Check if expense details are displayed correctly
    expect(screen.getByText('ABC Furniture Ltd')).toBeInTheDocument();
    expect(screen.getByText('Cool Air Services')).toBeInTheDocument();
    expect(screen.getByText('₹29,500')).toBeInTheDocument();
    expect(screen.getByText('₹17,700')).toBeInTheDocument();
  });

  test('opens add expense dialog when Add Expense button is clicked', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Click Add Expense button
    const addButton = screen.getByText('Add Expense');
    await userEvent.click(addButton);

    // Check if dialog is opened
    await waitFor(() => {
      expect(screen.getByText('Add New Expense')).toBeInTheDocument();
    });

    // Check if form fields are present
    expect(screen.getByLabelText(/Expense Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Amount/i)).toBeInTheDocument();
  });

  test('filters expenses by category', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Office furniture purchase')).toBeInTheDocument();
    });

    // Find and click category filter
    const categoryFilter = screen.getByLabelText('Category');
    await userEvent.click(categoryFilter);

    // Select Infrastructure category
    const infrastructureOption = screen.getByText('Infrastructure');
    await userEvent.click(infrastructureOption);

    // Verify API was called with filter
    await waitFor(() => {
      expect(mockedAPI.expenseAPI.getExpenses).toHaveBeenCalledWith(
        expect.objectContaining({
          get: expect.any(Function)
        })
      );
    });
  });

  test('creates new expense successfully', async () => {
    // Mock successful creation
    (mockedAPI.expenseAPI.createExpense as jest.Mock).mockResolvedValue({
      id: 3,
      expense_date: '2024-01-25',
      description: 'Test expense',
      amount: 5000.00,
      total_amount: 5900.00
    });

    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Open add dialog
    const addButton = screen.getByText('Add Expense');
    await userEvent.click(addButton);

    // Fill form
    await waitFor(() => {
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    });

    const descriptionField = screen.getByLabelText(/Description/i);
    const amountField = screen.getByLabelText(/Amount/i);

    await userEvent.type(descriptionField, 'Test expense description');
    await userEvent.type(amountField, '5000');

    // Submit form
    const createButton = screen.getByText('Create Expense');
    await userEvent.click(createButton);

    // Verify API was called
    await waitFor(() => {
      expect(mockedAPI.expenseAPI.createExpense).toHaveBeenCalled();
    });
  });

  test('approves expense successfully', async () => {
    // Mock successful approval
    (mockedAPI.expenseAPI.approveExpense as jest.Mock).mockResolvedValue({
      id: 2,
      expense_status_id: 2,
      approved_by: 1
    });

    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Wait for expenses to load
    await waitFor(() => {
      expect(screen.getByText('HVAC system repair')).toBeInTheDocument();
    });

    // Find and click approve button for pending expense
    const approveButtons = screen.getAllByTitle('Approve');
    expect(approveButtons.length).toBeGreaterThan(0);

    await userEvent.click(approveButtons[0]);

    // Verify API was called
    await waitFor(() => {
      expect(mockedAPI.expenseAPI.approveExpense).toHaveBeenCalledWith(
        2,
        { expense_status_id: 2, approval_comments: 'Approved' }
      );
    });
  });

  test('deletes expense successfully', async () => {
    // Mock successful deletion
    (mockedAPI.expenseAPI.deleteExpense as jest.Mock).mockResolvedValue({
      message: 'Expense deleted successfully'
    });

    // Mock window.confirm
    window.confirm = jest.fn(() => true);

    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Wait for expenses to load
    await waitFor(() => {
      expect(screen.getByText('HVAC system repair')).toBeInTheDocument();
    });

    // Find and click delete button for pending expense
    const deleteButtons = screen.getAllByTitle('Delete');
    expect(deleteButtons.length).toBeGreaterThan(0);

    await userEvent.click(deleteButtons[0]);

    // Verify API was called
    await waitFor(() => {
      expect(mockedAPI.expenseAPI.deleteExpense).toHaveBeenCalledWith(2);
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    (mockedAPI.expenseAPI.getExpenses as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText('Error fetching expenses')).toBeInTheDocument();
    });
  });

  test('displays loading state correctly', async () => {
    // Mock delayed API response
    (mockedAPI.expenseAPI.getExpenses as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        expenses: [],
        total: 0,
        page: 1,
        per_page: 20,
        total_pages: 0,
        summary: {}
      }), 1000))
    );

    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Should show loading spinner
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('validates form inputs correctly', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Open add dialog
    const addButton = screen.getByText('Add Expense');
    await userEvent.click(addButton);

    // Try to submit empty form
    await waitFor(() => {
      expect(screen.getByText('Create Expense')).toBeInTheDocument();
    });

    const createButton = screen.getByText('Create Expense');
    await userEvent.click(createButton);

    // Should show validation errors (handled by browser/MUI)
    const requiredFields = screen.getAllByText(/required/i);
    expect(requiredFields.length).toBeGreaterThan(0);
  });

  test('auto-calculates total amount', async () => {
    render(
      <TestWrapper>
        <ExpenseManagement />
      </TestWrapper>
    );

    // Open add dialog
    const addButton = screen.getByText('Add Expense');
    await userEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/Amount/i)).toBeInTheDocument();
    });

    // Fill amount and tax
    const amountField = screen.getByLabelText(/Amount \(₹\)/i);
    const taxField = screen.getByLabelText(/Tax Amount/i);
    const totalField = screen.getByLabelText(/Total Amount/i);

    await userEvent.type(amountField, '10000');
    await userEvent.type(taxField, '1800');

    // Total should be auto-calculated
    await waitFor(() => {
      expect(totalField).toHaveValue(11800);
    });
  });
});
