import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import { client, doLogin } from './Services'
import { useAuth } from './AuthContext';
import { Navigate, useNavigate } from 'react-router';


const Login = () => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState(null);
	const [loading, setLoading] = useState(false);

	const nav = useNavigate();

	const auth = useAuth();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError(null);

		try {
			const response = await doLogin(email, password);

			const { access_token } = response.data;
			auth.setToken(access_token)
			console.log('Login successful, token:', access_token);

			setLoading(false);
			nav('/');
		} catch (err) {
			setLoading(false);
			if (err.response) {
				setError('Login failed: ' + err.response.data.msg);
			} else {
				setError('An error occurred. Please try again.');
			}
		}
	};

	return (
		<Container className='mt-5'>
			<Row className="justify-content-center">
				<Col md={6}>
					<h2 className="text-center mb-4">Login</h2>

					{error && <Alert variant="danger">{error}</Alert>}

					<Form onSubmit={handleSubmit}>
						<Form.Group controlId="formEmail">
							<Form.Label>Email address</Form.Label>
							<Form.Control
								type="text"
								placeholder="Enter email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								required
							/>
						</Form.Group>

						<Form.Group controlId="formPassword">
							<Form.Label>Password</Form.Label>
							<Form.Control
								type="password"
								placeholder="Enter password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								required
							/>
						</Form.Group>

						<Button
							variant="primary"
							type="submit"
							className="w-100 mt-5"
							disabled={loading}
						>
							Zaloguj
						</Button>
					</Form>
				</Col>
			</Row>
		</Container>
	);
};

export default Login;
