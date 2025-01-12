import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import OrderForm from './OrderAdd';
import { BrowserRouter as Router, useLocation } from 'react-router';
import { useAuth } from './AuthContext';
import { addOrder } from './Services';

jest.mock('./AuthContext');
jest.mock('./Services');
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useLocation: jest.fn(), // Mock useLocation
}));

describe('OrderForm', () => {
  const mockProduct = {
    id: 1,
    image: 'fake-image',
    description: 'Sample product description',
    price: 100,
  };

  beforeEach(() => {
    useAuth.mockReturnValue({}); // Mock the authentication context
    addOrder.mockResolvedValue({}); // Mock the addOrder function
    useLocation.mockReturnValue({ state: mockProduct }); // Mock useLocation to return a product
  });

  it('renders form with all fields and submit button', () => {
    render(
      <Router>
        <OrderForm />
      </Router>
    );
    expect(screen.getByLabelText(/Województwo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Dostawa/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Adres dostawy/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Data dostawy/i)).toBeInTheDocument();
    expect(screen.getByText(/Create Order/i)).toBeInTheDocument();
  });

  it('allows user to fill out and submit the form', async () => {
    render(
      <Router>
        <OrderForm />
      </Router>
    );
    fireEvent.change(screen.getByLabelText(/Województwo/i), {
      target: { value: 'Mazowieckie' },
    });
    fireEvent.change(screen.getByLabelText(/Dostawa/i), {
      target: { value: 'COURIER' },
    });
    fireEvent.change(screen.getByLabelText(/Adres dostawy/i), {
      target: { value: '123 Main St, Warsaw' },
    });
    fireEvent.change(screen.getByLabelText(/Data dostawy/i), {
      target: { value: '2025-01-15' },
    });
    fireEvent.click(screen.getByText(/Create Order/i));
    await waitFor(() => {
      expect(addOrder).toHaveBeenCalled();
    });
  });

  it('shows validation errors for required fields', () => {
    render(
      <Router>
        <OrderForm />
      </Router>
    );
    fireEvent.click(screen.getByText(/Create Order/i));
    expect(screen.getByLabelText(/Województwo/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/Dostawa/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/Adres dostawy/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/Data dostawy/i)).toHaveAttribute('required');
  });
});
