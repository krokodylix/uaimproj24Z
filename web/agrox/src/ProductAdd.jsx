import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import ProductForm from './ProductForm';
import { addProduct } from './Services';

const ProductAdd = () => {
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState();
	const [product, setProduct] = useState({
		description: '',
		price: '',
	});
	const auth = useAuth();
	const nav = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();

		setError(null);
		setLoading(true);
		await addProduct(auth, product);
		nav('/products');
		setLoading(false);
	};

	return < ProductForm product={product} setProduct={setProduct} onSubmit={handleSubmit} error={error} loading={loading} title='Dodaj produkt' />
}


export default ProductAdd;
