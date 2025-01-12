import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, ListGroup, Spinner, Alert } from 'react-bootstrap';
import { getOrders } from './Services';
import { useAuth } from './AuthContext';
import { transportTypeText } from './EnumValues';

const OrdersList = () => {
	const [orders, setOrders] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const auth = useAuth();

	useEffect(() => {
		console.log(auth)
		const fetchOrders = async () => {
			try {
				const response = await getOrders(auth)
				setOrders(response.data);
				setLoading(false);
			} catch (err) {
				setError('Error fetching orders');
				setLoading(false);
			}
		};
		if (auth.token) {
			fetchOrders();
		}
	}, [auth.token]);

	if (loading) {
		return (
			<Container className="text-center my-5">
				<Spinner animation="border" />
			</Container>
		);
	}

	if (error) {
		return (
			<Container className="my-5">
				<Alert variant="danger">{error}</Alert>
			</Container>
		);
	}

	return (
		<Container className="my-5">
			<Row>
				{orders.map((order, index) => (
					<Col key={index} sm={12} md={6} lg={4} className="mb-4">
						<Card>
							<Card.Body>
								<Card.Title>Zamowienie {order.order_id}</Card.Title>
								<ListGroup variant="flush">
									<ListGroup.Item><strong>Opis produktu:</strong> {order.product_description}</ListGroup.Item>
									<ListGroup.Item><strong>Data dostawy: </strong> {order.delivery_date}</ListGroup.Item>
									<ListGroup.Item><strong>Addres:</strong> {order.address}</ListGroup.Item>
									<ListGroup.Item><strong>Dostawa:</strong> {transportTypeText[order.transport_type]}</ListGroup.Item>
									<ListGroup.Item><strong>Województwo:</strong> {order.province}</ListGroup.Item>
								</ListGroup>
							</Card.Body>
						</Card>
					</Col>
				))}
			</Row>
		</Container>
	);
};

export default OrdersList;
