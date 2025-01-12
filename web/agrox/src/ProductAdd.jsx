import React, { useState } from 'react';
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
	const auth = useAuth()

	const handleSubmit = async (e) => {
	  e.preventDefault();

	  setError(null);
		setLoading(true);
		await addProduct(auth, product)
	};

	return < ProductForm product={product} setProduct={setProduct} onSubmit={handleSubmit} error={error} loading={loading} title='Dodaj produkt'/>
}


export default ProductAdd;
