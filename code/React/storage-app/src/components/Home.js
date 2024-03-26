// Say hello to logged in users with a button to products
//

import React, { useState, useContext } from 'react';
import Login from './Login'; // Import the Login component
import { AuthContext } from '../contexts/auth.js';

//import navigate to redirect
import { useNavigate } from 'react-router-dom';

const Home = () => {
    const navigate = useNavigate();
    const { loggedInUser, setLoggedInUser } = useContext(AuthContext); // Add setLoggedInUser
    
    return (
        <div>
            {loggedInUser ? (
                <>
                    <h1>Hello {loggedInUser.username} </h1>
                    <p>You are home</p>
                </>
            ) : (
                <>
                    <h1>Hello</h1>
                    <p>Please log in</p>
                </>
            )}
        </div>
    );
}

export default Home;