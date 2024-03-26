import React, {useState, useEffect, useContext} from 'react';
import api from './api/api.js';
import './App.css';

//import the AuthContext
import { AuthContext } from './contexts/auth.js';
import Products from './components/Products.js';
import Add_Products from './components/Add_products.js';
import NavBar from './components/NavBar.js';
import Home from './components/Home.js';
import Users from './components/Users.js';
// router
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// userprotectedroute
import UserProtectedRoute from './components/UserProtectedRoute.js';
import AdminProtectedRoute from './components/AdminProtectedRoute.js';

const App = () => {
  
  const { loggedInUser } = useContext(AuthContext);

  return (
    <div className="App">
    <BrowserRouter>
      <NavBar />
        <Routes>
          <Route path="/" element={
            <UserProtectedRoute>
              <Home />
            </UserProtectedRoute>
          } />
          <Route path="/products" element={
            <UserProtectedRoute>
              <Products />
            </UserProtectedRoute>
          } />
          < Route path="/users" element={
            <AdminProtectedRoute>
              <Users />
            </AdminProtectedRoute>
          } />
          <Route path="/add_products" element={
            <AdminProtectedRoute>
              <Add_Products />
            </AdminProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>

    </div>
  );
}


export default App;