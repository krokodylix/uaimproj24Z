import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router';
import { useAuth } from './AuthContext';
import { districts, deliveryMethods } from './EnumValues'
import { addOrder } from './Services';

const OrderForm = () => {
	const [district, setDistrict] = useState('');
	const [deliveryMethod, setDeliveryMethod] = useState('');
	const [address, setAddress] = useState('');
	const [deliveryDate, setDeliveryDate] = useState('');
	const { state: product } = useLocation()
	const auth = useAuth()
	const nav = useNavigate()

	const handleSubmit = async (e) => {
		e.preventDefault();
		const order = {
			product_id: product.id,
			delivery_date: deliveryDate,
			address: address,
			transport_type: deliveryMethod,
			province: district,
		};
		await addOrder(auth, order);
		nav('/orders');
	};

	return (
		<Container className="mt-5">
			<Row>
				<Col md={6}>
					<Card>
						<Card.Body>
							<Card.Title>Product Details</Card.Title>
							<Card.Img variant="top" src={`data:image/png;base64,${product.image}`} alt="" style={{ maxHeight: '256px', objectFit: 'contain' }} />
							<Card.Text><strong>Description:</strong> {product.description}</Card.Text>
							<Card.Text><strong>Price:</strong> ${product.price}</Card.Text>
						</Card.Body>
					</Card>
				</Col>
				<Col md={6}>
					<Form onSubmit={handleSubmit}>
						<h4>Order Details</h4>

						<Form.Group controlId="district">
							<Form.Label>Województwo</Form.Label>
							<Form.Control as="select" value={district} onChange={(e) => setDistrict(e.target.value)} required>
								<option value=""> Wybierz województwo </option>
								{districts.map((district, index) => (
									<option key={index} value={district}>{district}</option>
								))}
							</Form.Control>
						</Form.Group>

						<Form.Group controlId="deliveryMethod">
							<Form.Label>Dostawa</Form.Label>
							<Form.Control as="select" value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)} required>
								<option value="">Wybierz sposób dostawy</option>
								{deliveryMethods.map((method, index) => (
									<option key={index} value={method}>{method}</option>
								))}
							</Form.Control>
						</Form.Group>

						<Form.Group controlId="address">
							<Form.Label>Adres dostawy</Form.Label>
							<Form.Control
								type="text"
								placeholder="Wpisz adres dostawy"
								value={address}
								onChange={(e) => setAddress(e.target.value)}
								required
							/>
						</Form.Group>

						<Form.Group controlId="deliveryDate">
							<Form.Label>Data dostawy</Form.Label>
							<Form.Control
								type="date"
								value={deliveryDate}
								onChange={(e) => setDeliveryDate(e.target.value)}
								required
							/>
						</Form.Group>

						<Button variant="primary" type="submit" className="w-100 mt-5">
							Create Order
						</Button>
					</Form>
				</Col>
			</Row>
		</Container>
	);
};

export default OrderForm;
