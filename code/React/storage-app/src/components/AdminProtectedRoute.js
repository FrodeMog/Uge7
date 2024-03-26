import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/auth.js';

function ProtectedRoute({ children }) {
    const { loggedInUser, handleContextLogin, isAdmin } = useContext(AuthContext);

    
    // Check if the loggedInUser is an admin
    if (!loggedInUser) {
        // User not logged in, redirect to login page
        return <Navigate to="/login" />;
    }

    if (!isAdmin) {
        // User not an admin, redirect to home page
        return <Navigate to="/" />;
    }

    return children;
}

export default ProtectedRoute;