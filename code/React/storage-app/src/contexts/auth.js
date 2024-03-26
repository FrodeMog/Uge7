// Authentication react context

import React, { createContext, useState, useEffect } from 'react';
import api from '../api/api.js';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loggedInUser, setLoggedInUser] = useState(JSON.parse(localStorage.getItem('loggedInUser')));

    const isAdmin = loggedInUser && loggedInUser.type === 'admin_user';

    const handleContextLogin = async (username,password) => {
        try {
        const response = await api.post('/login_user/', { username, password });
        const logged_in_user = response.data;
        console.log(logged_in_user);
        setLoggedInUser(logged_in_user); // Set the logged-in user
        localStorage.setItem('loggedInUser', JSON.stringify(logged_in_user)); // Store the logged-in user in localStorage
        } catch (error) {
        
        }
    };

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('loggedInUser'));
        if (user) {
            setLoggedInUser(user);
        }
    }, []);

    return (
        <AuthContext.Provider value={{ username, setUsername, password, setPassword, loggedInUser, setLoggedInUser, handleContextLogin, isAdmin }}>
        {children}
        </AuthContext.Provider>
    );
}
export { AuthContext, AuthProvider };