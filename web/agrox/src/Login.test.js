import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Login from './Login';
import { doLogin } from './Services'; 
import { BrowserRouter as Router } from 'react-router';
import { useAuth } from './AuthContext';

jest.mock('./Services');
jest.mock('./AuthContext');

describe('Login Component', () => {
  let setTokenMock;
  beforeEach(() => {
    setTokenMock = jest.fn();
    useAuth.mockReturnValue({ setToken: setTokenMock });
  });

  it('renders the login form correctly', () => {
    render(
      <Router>
        <Login />
      </Router>
    );
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /zaloguj/i })).toBeInTheDocument();
  });

  it('shows error message when login fails', async () => {
    doLogin.mockRejectedValueOnce({
      response: { data: { msg: 'Invalid credentials' } },
    });
    render(
      <Router>
        <Login />
      </Router>
    );
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'incorrect-password' } });
    fireEvent.click(screen.getByRole('button', { name: /zaloguj/i }));
    await waitFor(() => expect(screen.getByText(/login failed: invalid credentials/i)).toBeInTheDocument());
  });

  it('navigates to home page after successful login', async () => {
    doLogin.mockResolvedValueOnce({
      data: { access_token: 'dummy-token' },
    });
    render(
      <Router>
        <Login />
      </Router>
    );
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'correct-password' } });
    fireEvent.click(screen.getByRole('button', { name: /zaloguj/i }));
    await waitFor(() => expect(setTokenMock).toHaveBeenCalledWith('dummy-token'));
  });
});
