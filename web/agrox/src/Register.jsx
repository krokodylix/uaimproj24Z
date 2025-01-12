import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { doRegister } from './Services';

const Register = () => {
	// Separate state variables for each form field
	const [username, setUsername] = useState('');
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');

	const nav = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');
		setLoading(true);

		try {
			await doRegister(username, email, password);
			setLoading(false);
			nav('/login');
		} catch (err) {
			setLoading(false);
			if (err.response) {
				setError('Login failed: ' + err.response.data.msg);
			} else {
				setError('An error occurred. Please try again.');
			}
		}
		// try {

		// } catch (err) {
		// 	setError(err.message);
		// } finally {
		// 	setLoading(false);
		// }
	};

	return (
		<Container className="mt-5">
			<Row className="justify-content-center">
				<Col md={6}>
					{error && <Alert variant="danger">{error}</Alert>}

					<h2 className="mb-4 text-center">User Registration</h2>
					<Form onSubmit={handleSubmit}>
						<Form.Group controlId="formUsername">
							<Form.Label>Username</Form.Label>
							<Form.Control
								type="text"
								value={username}
								onChange={(e) => setUsername(e.target.value)}
								placeholder="Enter your username"
								required
							/>
						</Form.Group>

						<Form.Group controlId="formEmail">
							<Form.Label>Email address</Form.Label>
							<Form.Control
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="Enter your email"
								required
							/>
						</Form.Group>

						<Form.Group controlId="formPassword">
							<Form.Label>Password</Form.Label>
							<Form.Control
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								placeholder="Enter your password"
								required
							/>
						</Form.Group>

						<Button
							variant="primary"
							type="submit"
							className="w-100"
							disabled={loading}
						>
							{loading ? 'Registering...' : 'Register'}
						</Button>
					</Form>
				</Col>
			</Row>
		</Container>
	);
};

export default Register;
