import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './Login'
import ProductList from './ProductList'
import { AuthProvider } from './AuthContext';
import NavBar from './NavBar';
import { Container, Row } from 'react-bootstrap';
import Register from './Register';
import ProductAdd from './ProductAdd';
import ProductEdit from './ProductEdit';
import OrderForm from './OrderAdd';
import SalesReport from './AdminReport';
import OrderList from './OrderList';
import Index from './Redirector';

function App() {
	return (
		<Container fluid>
			<BrowserRouter>
				<AuthProvider>
					<NavBar />
					<Routes>
						<Route exact path="/login" element={<Login />} />
						<Route exact path="/register" element={<Register />} />

						<Route exact path="/admin/product_add" element={<ProductAdd />} />
						<Route exact path="/admin/product_edit/:id" element={<ProductEdit />} />
						<Route exact path="/admin/report" element={<SalesReport />} />

						<Route exact path="/products" element={<ProductList />} />
						<Route exact path="/orders" element={<OrderList />} />
						<Route exact path="/order_add" element={<OrderForm />} />

						<Route index element={<Index/>} />
					</Routes>
				</AuthProvider>
			</BrowserRouter>
		</Container>
	);
}

export default App;
