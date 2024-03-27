import React, {useState, useEffect, useContext} from 'react';
import api from './api/api.js';
import './App.css';

//import the AuthContext
import { AuthContext } from './contexts/auth.js';
import Products from './components/Products.js';
import Create from './components/Create.js';
import NavBar from './components/NavBar.js';
import Home from './components/Home.js';
import Users from './components/Users.js';
import Transactions from './components/Transactions.js';
import Categories from './components/Categories.js';
import Logs from './components/Logs.js';
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
        <Route path="/" element={<Home />} />
        <Route path="/logs" element={
              <AdminProtectedRoute>
                  <Logs />
              </AdminProtectedRoute>
          } />
        <Route path="/transactions" element={
            <UserProtectedRoute>
              <Transactions />
            </UserProtectedRoute>
          } />
          <Route path="/products" element={
            <UserProtectedRoute>
              <Products />
            </UserProtectedRoute>
          } />
          <Route path="/categories" element={
              <AdminProtectedRoute>
                  <Categories />
              </AdminProtectedRoute>
          } />
          < Route path="/users" element={
            <AdminProtectedRoute>
              <Users />
            </AdminProtectedRoute>
          } />
          <Route path="/create" element={
            <AdminProtectedRoute>
              <Create />
            </AdminProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>

    </div>
  );
}


export default App;