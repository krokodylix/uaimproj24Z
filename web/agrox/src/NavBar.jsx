import React from 'react';
import { Navbar, Nav, NavDropdown, Button, Container } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { useAuth } from './AuthContext';

const NavBar = () => {
	const nav = useNavigate()

	const auth = useAuth()


	const handleLogin = () => {
		nav('/login')
	};

	const handleRegister = () => {
		nav('/register')
	};

	const handleLogout = () => {
		auth.setToken()
	};


	return (
		<Navbar bg="light">
			<Container>
				<Navbar.Brand href="/">Agrallusion</Navbar.Brand>
				<Navbar.Toggle aria-controls="navbar-nav" />
				<Navbar.Collapse id="navbar-nav">
					<Nav className="ml-auto">
						{auth.user ? (
							<>
								<NavDropdown title={`${auth.user.username}`} id="user-dropdown">
									<NavDropdown.Item disabled>Email: {auth.user.email}</NavDropdown.Item>
									<NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
								</NavDropdown>
								<Nav.Link href="/products">Produkty</Nav.Link>
								<Nav.Link href="/orders">Moje zamówienia</Nav.Link>
								{ auth.is_admin() && (
									<>
										<NavDropdown title='Administracja'>
											<NavDropdown.Item href='/admin/product_add'> Dodaj produkt </NavDropdown.Item>
											<NavDropdown.Item href='/admin/report'> Generuj raport </NavDropdown.Item>
										</NavDropdown>
									</>
								)}
							</>
						) : (
							<>
								<Button variant="outline-primary" onClick={handleLogin}> Login </Button>
								<Button variant="outline-secondary" onClick={handleRegister}> Register </Button>
							</>
						)}
					</Nav>
				</Navbar.Collapse>
			</Container>
		</Navbar>
	);
};

export default NavBar;
