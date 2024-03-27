// Navbar
import React, { useState, useContext } from 'react';
import { AuthContext } from '../contexts/auth.js';
import Register from './Register'; 
import Login from './Login';
// import navbar specific css
import './NavBar.css';
// import navigate
import { useNavigate } from 'react-router-dom';


const NavBar = () => {
    const navigate = useNavigate();

    // get the logged in user
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    return (
      <nav className="navbar navbar-dark bg-primary">
          <div className="container-fluid">
          <a className="navbar-brand" href="#" onClick={() => navigate('/')}>
            Storage App
          </a>
              {loggedInUser && <button className="btn btn-primary" onClick={() => navigate('/products')}>Products</button>}
              {loggedInUser && <button className="btn btn-primary" onClick={() => navigate('/transactions')}>Transactions</button>}
              {isAdmin && <button className="btn btn-primary" onClick={() => navigate('/users')}>Users</button>}
              {isAdmin && <button className="btn btn-primary" onClick={() => navigate('/create')}>Create</button>}
              {loggedInUser ? (
                <div>
                    <span className="navbar-text">
                        Logged in as: {loggedInUser.username}
                    </span>
                    <button className="btn btn-primary" onClick={() => { // Logout button
                        setLoggedInUser(null);
                        localStorage.removeItem('loggedInUser'); // Remove the user data from localStorage
                    }}>Logout</button>
                </div>
            ) : (
                <div className="d-flex justify-content-end align-items-center">
                    <Login /> 
                    <Register /> 
                </div>
            )}
          </div>
      </nav>
  );
}

export default NavBar;