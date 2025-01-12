import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router';
import { useAuth } from './AuthContext';
import ProductForm from './ProductForm';
import { addProduct, editProduct } from './Services';

const ProductAdd = () => {
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState();
	const { state: initialProduct } = useLocation()
	const [product, setProduct] = useState(initialProduct);
	const auth = useAuth()
	const nav = useNavigate()

	const handleSubmit = async (e) => {
	  e.preventDefault();

	  setError(null);
		setLoading(true);
		await editProduct(auth, product.id, product)
		nav('/products');
		setLoading(false);
	};

	return < ProductForm product={product} setProduct={setProduct} onSubmit={handleSubmit} error={error} loading={loading} title='Edytuj produkt'/>
}


export default ProductAdd;
