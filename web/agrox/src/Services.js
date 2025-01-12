import axios from "axios";

export const client = axios.create({
	baseURL: "http://localhost:5000",
});

const headers = (auth) => { console.log('aaa' + auth.token); return { headers: { Authorization: `Bearer ${auth.token}` } }; };

export const doRegister = (username, email, password) => client.post('register', { username, email, password })
export const doLogin = (email, password) => client.post('login', { email, password })

export const getProducts = (auth) => client.get('products', headers(auth))
export const getUser = (auth) => client.get('user', headers(auth))
export const addOrder = (auth, order) => client.post('order', order, headers(auth))
export const getOrders = (auth) => client.get('my_orders', headers(auth))

export const addProduct = (auth, product) => client.post('product', product, headers(auth))
export const editProduct = (auth, id, product) => client.put(`product/${id}`, product, headers(auth))
export const delProduct = (auth, id) => client.delete(`product/${id}`, headers(auth))
export const getReport = (auth, start_date, end_date) => client.get('admin/report', { params: { start_date, end_date }, headers: headers(auth).headers })
