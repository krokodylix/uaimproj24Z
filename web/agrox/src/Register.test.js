import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Register from './Register';
import { doRegister } from './Services';
import { BrowserRouter as Router } from 'react-router';

jest.mock('./Services', () => ({
  doRegister: jest.fn(),
}));

describe('Register Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the register form correctly', () => {
    render(
      <Router>
        <Register />
      </Router>
    );
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Zarejestruj/i })).toBeInTheDocument();
  });

  it('submits the form with valid inputs and navigates to login', async () => {
    doRegister.mockResolvedValueOnce({}); 
    render(
      <Router>
        <Register />
      </Router>
    );
    userEvent.type(screen.getByLabelText(/Username/i), 'testuser');
    userEvent.type(screen.getByLabelText(/Email address/i), 'testuser@example.com');
    userEvent.type(screen.getByLabelText(/Password/i), 'password123');
    fireEvent.click(screen.getByRole('button', { name: /Zarejestruj/i }));
    expect(screen.getByRole('button', { name: /Zarejestruj/i })).toBeDisabled();
    await waitFor(() => {
      expect(doRegister).toHaveBeenCalled();
      expect(window.location.pathname).toBe('/login');
    });
  });
});

