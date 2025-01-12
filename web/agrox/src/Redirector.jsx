import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext"

const Index = () => {
	const auth = useAuth();
	return <Navigate to = {auth.token ? '/products' : '/login'}/>
};

export default Index;
