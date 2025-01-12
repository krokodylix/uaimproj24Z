import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProductForm from './ProductForm'; // Adjust path as necessary

const mockSetProduct = jest.fn();
const mockOnSubmit = jest.fn();

describe('ProductForm Component', () => {
  beforeEach(() => {
    mockSetProduct.mockClear();
    mockOnSubmit.mockClear();
  });

  it('should render the form with price and description inputs', () => {
    render(
      <ProductForm
        product={{ price: '', description: '', image: '' }}
        setProduct={mockSetProduct}
        onSubmit={mockOnSubmit}
        loading={false}
        error={null}
        title="Add Product"
      />
    );
    expect(screen.getByLabelText(/price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/product description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/product image/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /wyślij/i })).toBeInTheDocument();
  });

  it('should handle input change for price and description fields', () => {
    render(
      <ProductForm
        product={{ price: '', description: '', image: '' }}
        setProduct={mockSetProduct}
        onSubmit={mockOnSubmit}
        loading={false}
        error={null}
        title="Add Product"
      />
    );
    fireEvent.change(screen.getByLabelText(/price/i), { target: { value: '123' } });

    expect(mockSetProduct).toHaveBeenCalled();
  });

  it('should display error message if error is passed as prop', () => {
    render(
      <ProductForm
        product={{ price: '', description: '', image: '' }}
        setProduct={mockSetProduct}
        onSubmit={mockOnSubmit}
        loading={false}
        error="An error occurred"
        title="Add Product"
      />
    );
    expect(screen.getByText(/an error occurred/i)).toBeInTheDocument();
  });

  it('should disable the submit button while loading', () => {
    render(
      <ProductForm
        product={{ price: '', description: '', image: '' }}
        setProduct={mockSetProduct}
        onSubmit={mockOnSubmit}
        loading={true}
        error={null}
        title="Add Product"
      />
    );
    expect(screen.getByRole('button', { name: /wyślij/i })).toBeDisabled();
  });

  it('should call onSubmit function when the form is submitted', () => {
    render(
      <ProductForm
        product={{ price: '100', description: 'Product Description', image: '' }}
        setProduct={mockSetProduct}
        onSubmit={mockOnSubmit}
        loading={false}
        error={null}
        title="Add Product"
      />
    );
    fireEvent.submit(screen.getByRole('button'));
    expect(mockOnSubmit).toHaveBeenCalled();
  });
});
