import React, { useState } from 'react';
import { Button, Card, Form, Col, Row, Container } from 'react-bootstrap';
import { getReport } from './Services';
import { useAuth } from './AuthContext';

const SalesReport = () => {
	const [startDate, setStartDate] = useState('');
	const [endDate, setEndDate] = useState('');
	const [report, setReport] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const auth = useAuth()

	const fetchSalesReport = async () => {
		setLoading(true);
		setError(null);

		try {
			const response = await getReport(auth, startDate, endDate);
			setReport(response.data);
		} catch (err) {
			setError('Błąd generowania raportu');
		} finally {
			setLoading(false);
		}
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		fetchSalesReport();
	};

	return (
		<Container>
			<Row className="justify-content-center">
				<Col md={6}>
					<h2>Generate Sales Report</h2>
					<Form onSubmit={handleSubmit}>
						<Form.Group controlId="startDate">
							<Form.Label>Data początkowa</Form.Label>
							<Form.Control
								type="date"
								value={startDate}
								onChange={(e) => setStartDate(e.target.value)}
								required
							/>
						</Form.Group>
						<Form.Group controlId="endDate">
							<Form.Label>Data końcowa
							</Form.Label>
							<Form.Control
								type="date"
								value={endDate}
								onChange={(e) => setEndDate(e.target.value)}
								required
							/>
						</Form.Group>
						<Button type="submit" variant="primary" className='mt-5' disabled={loading}>
							Generuj raport
						</Button>
					</Form>
					{error && <div className="mt-5 text-danger">{error}</div>}

					{report && (
						<Card className="mt-5">
							<Card.Body>
								<Card.Title>Raport</Card.Title>
								<Card.Text><strong> Ilość zamówień </strong> {report.total_orders}</Card.Text>
								<Card.Text><strong> Suma zamówień </strong> ${report.total_sum.toFixed(2)}</Card.Text>

								<h5>Ilość zamówień w województwach:</h5>
								<ul>
									{Object.entries(report.orders_per_province).map(([province, cnt]) => {
										return (
											<li key={province}>
												{province}: {cnt}
											</li>
										);
									})}
								</ul>
							</Card.Body>
						</Card>
					)}
				</Col>
			</Row>

		</Container>
	);
};

export default SalesReport;
