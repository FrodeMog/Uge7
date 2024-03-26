// Navbar
import React, { useState, useContext } from 'react';
import { AuthContext } from '../contexts/auth.js';

// import navbar specific css
import './NavBar.css';


// import navigate
import { useNavigate } from 'react-router-dom';

const NavBar = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // get the logged in user
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);
    
    const handleLogin = async (event) => {
        event.preventDefault();
        handleContextLogin(username, password);
    }
    return (
        <nav className="navbar navbar-dark bg-primary">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            Storage App
          </a>
          <button className="btn btn-primary" onClick={() => navigate('/')}>Home</button>
          <button className="btn btn-primary" onClick={() => navigate('/products')}>Products</button>
          {isAdmin && <button className="btn btn-primary" onClick={() => navigate('/users')}>Users</button>}
          {loggedInUser ? (
          <div>
            <span className="navbar-text">
              Logged in as: {loggedInUser.username}
            </span>
            <button className="btn btn-primary" onClick={() => setLoggedInUser(null)}>Logout</button>
          </div>
          ) : (
            <form className="d-flex" onSubmit={handleLogin}>
              <input className="form-control me-2" type="text" placeholder="Username" aria-label="Username" onChange={e => setUsername(e.target.value)} />
              <input className="form-control me-2" type="password" placeholder="Password" aria-label="Password" onChange={e => setPassword(e.target.value)} />
              <button className="btn btn-primary" type="submit">Login</button>
            </form>
          )}
        </div>
      </nav>
    );
}

export default NavBar;