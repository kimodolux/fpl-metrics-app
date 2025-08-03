import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

type PrivateRouteProps = {
  children: React.ReactNode;
};

export const PrivateRoute = ({ children }: PrivateRouteProps) => {
  const { isAuthenticated } = useAuthStore();

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};