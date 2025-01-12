import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SalesReport from './AdminReport';
import { getReport } from './Services';
import { useAuth } from './AuthContext';

jest.mock('./Services');
jest.mock('./AuthContext');

describe('AdminReport Component', () => {
  
  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { id: 1, name: 'Test User' },
    });
  });

  it('should render SalesReport component correctly', () => {
    render(<SalesReport />);
    expect(screen.getByText('Generate Sales Report')).toBeInTheDocument();
    expect(screen.getByLabelText('Data początkowa')).toBeInTheDocument();
    expect(screen.getByLabelText('Data końcowa')).toBeInTheDocument();
    expect(screen.getByText('Generuj raport')).toBeInTheDocument();
  });

  it('should update the form input values', () => {
    render(<SalesReport />);
    const startDateInput = screen.getByLabelText('Data początkowa');
    const endDateInput = screen.getByLabelText('Data końcowa');
    fireEvent.change(startDateInput, { target: { value: '2025-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-01-10' } });
    expect(startDateInput.value).toBe('2025-01-01');
    expect(endDateInput.value).toBe('2025-01-10');
  });


  it('should display the error message if the API call fails', async () => {
    getReport.mockRejectedValueOnce(new Error('API Error'));
    render(<SalesReport />);
    const startDateInput = screen.getByLabelText('Data początkowa');
    const endDateInput = screen.getByLabelText('Data końcowa');
    const submitButton = screen.getByText('Generuj raport');
    fireEvent.change(startDateInput, { target: { value: '2025-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-01-10' } });
    fireEvent.click(submitButton);
    await waitFor(() => expect(screen.getByText('Błąd generowania raportu')).toBeInTheDocument());
  });

  it('should display the report when the API call is successful', async () => {
    const mockReportData = {
      total_orders: 100,
      total_sum: 5000,
      orders_per_province: {
        "Province A": 30,
        "Province B": 70,
      },
    };
    getReport.mockResolvedValueOnce({ data: mockReportData });
    render(<SalesReport />);
    const startDateInput = screen.getByLabelText('Data początkowa');
    const endDateInput = screen.getByLabelText('Data końcowa');
    const submitButton = screen.getByText('Generuj raport');
    fireEvent.change(startDateInput, { target: { value: '2025-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-01-10' } });
    fireEvent.click(submitButton);
    await waitFor(() => expect(screen.getByText('Raport')).toBeInTheDocument());
  });

  it('should disable the submit button when loading', async () => {
    render(<SalesReport />);
    const startDateInput = screen.getByLabelText('Data początkowa');
    const endDateInput = screen.getByLabelText('Data końcowa');
    const submitButton = screen.getByText('Generuj raport');
    fireEvent.change(startDateInput, { target: { value: '2025-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-01-10' } });
    fireEvent.click(submitButton);
    expect(submitButton).toBeDisabled();
  });
});
