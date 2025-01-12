import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { doRegister } from './Services';

const Register = () => {
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
	};

	return (
		<Container className='mt-5'>
			<Row className="justify-content-center">
				<Col md={6}>
					<h2 className="text-center">Rejestracja</h2>

					{error && <Alert variant="danger">{error}</Alert>}

					<Form onSubmit={handleSubmit} className='mt-5'>
						<Form.Group controlId="formUsername">
							<Form.Label>Username</Form.Label>
							<Form.Control
								type="text"
								value={username}
								onChange={(e) => setUsername(e.target.value)}
								placeholder="Wpisz nazwę użytkownika"
								required
							/>
						</Form.Group>

						<Form.Group controlId="formEmail">
							<Form.Label>Email address</Form.Label>
							<Form.Control
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="Wpisz email"
								required
							/>
						</Form.Group>

						<Form.Group controlId="formPassword">
							<Form.Label>Password</Form.Label>
							<Form.Control
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								placeholder="Wpisz hasło"
								required
							/>
						</Form.Group>

						<Button
							variant="primary"
							type="submit"
							className="w-100 mt-5"
							disabled={loading}
						>
							Zarejestruj
						</Button>
					</Form>
				</Col>
			</Row>
		</Container>
	);
};

export default Register;
