// Say hello to logged in users with a button to products
//

import React, { useState, useContext } from 'react';

import { AuthContext } from '../contexts/auth.js';

//import navigate to redirect
import { useNavigate } from 'react-router-dom';

const Home = () => {
    const navigate = useNavigate();
    const { loggedInUser } = useContext(AuthContext);
    
    return (
        <div>
            <h1>Hello {loggedInUser.username} </h1>
           <p>
            You are home
           </p>
        </div>
    );
}

export default Home;