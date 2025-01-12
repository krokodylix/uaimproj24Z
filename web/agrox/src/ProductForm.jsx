import { Form, Button, Col, Row, Alert, Container } from 'react-bootstrap';

const ProductForm = ({ product, setProduct, onSubmit, loading, error, title }) => {

	const handleInputChange = (e) => {
		const { name, value } = e.target;
		setProduct((prevProduct) => ({
			...prevProduct,
			[name]: value
		}));
	};

	const handleImageChange = (e) => {
		const file = e.target.files[0];
		if (file) {
			const reader = new FileReader();
			reader.onloadend = () => {
				setProduct((prevProduct) => ({
					...prevProduct,
					image: reader.result.split(',')[1]
				}));
			};
			reader.readAsDataURL(file);
		}
	};


	return (
		<Container className='mt-5'>
			<Row className='justify-content-center'>
				<Col md={6}>
					<h2>{title}</h2>
					{error && <Alert variant="danger">{error}</Alert>}
					<Form onSubmit={onSubmit}>
						<Form.Group controlId="price">
							<Form.Label>Price</Form.Label>
							<Form.Control
								type="number"
								name="price"
								value={product.price}
								onChange={handleInputChange}
								placeholder="Enter price"
								required
							/>
						</Form.Group>

						<Form.Group controlId="description">
							<Form.Label>Product Description</Form.Label>
							<Form.Control
								as="textarea"
								name="description"
								value={product.description}
								onChange={handleInputChange}
								rows={3}
								placeholder="Enter product description"
								required
							/>
						</Form.Group>

						<Form.Group controlId="image">
							<Form.Label>Product Image</Form.Label>
							<Form.Control
								type="file"
								accept="image/png"
								onChange={handleImageChange}
							/>

							{product.image && (
								<div className="mt-3">
									<img
										src={`data:image/png;base64,${product.image}`}
										alt="Product"
										style={{ width: '100px', height: '100px', objectFit: 'cover' }}
									/>
								</div>
							)}
						</Form.Group>

						<Button variant="primary" type="submit" className='mt-5' disabled={loading}>
							Wyślij
						</Button>
					</Form>
				</Col>
			</Row>
		</Container>
	);
};

export default ProductForm;

