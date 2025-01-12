import { Navigate } from "react-router";
import { useAuth } from "./AuthContext"

const Index = () => {
	const auth = useAuth();
	return <Navigate to = {auth.token ? '/products' : '/login'}/>
};

export default Index;
