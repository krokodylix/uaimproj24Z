import { useState, useEffect } from "react";
import { Card, Button, Container, Row, Col } from 'react-bootstrap';
import { useNavigate } from "react-router";
import { useAuth } from "./AuthContext";
import { delProduct, getProducts } from "./Services";

const ProductView = ({ product, isAdmin, onListUpdated }) => {
	const nav = useNavigate()
	const auth = useAuth()

	const handleEdit = e => {
		e.preventDefault();
		nav(`/admin/product_edit/${product.id}`, { state: product });
	}

	const handleOrder = e => {
		e.preventDefault();
		nav('/order_add', { state: product });
	}

	const handleDelete = async e => {
		e.preventDefault();
		await delProduct(auth, product.id);
		onListUpdated();
	}


	return <Col key={product.id} sm={12} md={6} lg={4} className="mb-4">
		<Card style={{ width: '24rem' }}>
			<Card.Img variant="top" src={`data:image/png;base64,${product.image}`} alt="" style={{ maxHeight: '256px', objectFit: 'cover' }} />
			<Card.Body>
				<Card.Title>Produkt {product.id}</Card.Title>
				<Card.Text>
					{product.description}
				</Card.Text>
				<div className="d-flex justify-content-between align-items-center">
					<span className="h4">{product.price}</span>
					<div>
						<Button variant="primary" onClick={handleOrder}> Zamów </Button>
						{isAdmin &&
							<>
								<Button variant="secondary" onClick={handleEdit} className="ml-4">
									Edytuj
								</Button>
								<Button variant="danger" onClick={handleDelete} className="ml-4">
									Usuń
								</Button>
							</>
						}
					</div>
				</div>
			</Card.Body>
		</Card>
	</Col>
}

const ProductList = () => {
	const [products, setProducts] = useState([])
	const auth = useAuth()

	const onListUpdated = () => {
		(async () => {
			const response = await getProducts(auth)
			setProducts(response.data);
		})();
	};

	useEffect(onListUpdated, [])

	if (!products) {
		return
	}

	return <Container>
		<Row>
		{products.map(p => <ProductView product={p} isAdmin={auth.is_admin()} onListUpdated={onListUpdated} />)}
		</Row>
	</Container>
}

export default ProductList
