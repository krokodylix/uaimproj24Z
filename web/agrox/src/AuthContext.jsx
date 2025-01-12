import React, { createContext, useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { getUser } from "./Services";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
	const [token, setToken] = useState(null);
	const [user, setUser] = useState(null);
	const [loading, setLoading] = useState(true); 
	const nav = useNavigate();

	useEffect(() => {
		const storedToken = localStorage.getItem('token');
		setToken(storedToken);
	}, []);

	useEffect(() => {
		(async () => {
			if(token) {
				try {
					setLoading(true); 
					const response = await getUser({token})
					setUser(response.data);
					setLoading(false); 
				} catch (error) {
					if(error.response) {
						setUser()
						setLoading(false); 
					} else {
						throw error
					}
				}
			} else {
				setUser()
				setLoading(false); 
			}
		}) ();
	}, [token]);

	const setTokenExternal = (token) => {
		setToken(token);
		localStorage.setItem('token', token);
		nav('/');
	}

	const is_admin = () => (user && user.is_admin)

	return (
		<AuthContext.Provider value={{ token, setToken: setTokenExternal, loading, user, is_admin }}>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => {
	return useContext(AuthContext);
};
