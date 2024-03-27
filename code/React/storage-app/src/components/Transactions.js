import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../contexts/auth.js';
import api from '../api/api.js';
import Toast from 'react-bootstrap/Toast';

const Transactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [products, setProducts] = useState([]);
    const [users, setUsers] = useState([]);
    const [productSearchTerm, setProductSearchTerm] = useState('');
    const [userSearchTerm, setUserSearchTerm] = useState('');
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [sortColumn, setSortColumn] = useState('id'); // start sorted by id
    const [sortDirection, setSortDirection] = useState(false); // false for descending order
    


    useEffect(() => {
        const fetchTransactions = async () => {
            let response;
            if (isAdmin) {
                response = await api.get('/get_transactions/');
            } else {
                response = await api.get(`/get_transactions_by_user_name/${loggedInUser.username}/`);
            }
            setTransactions(response.data);
        };

        const fetchProducts = async () => {
            const response = await api.get('/get_products/');
            setProducts(response.data);
        };

        const fetchUsers = async () => {
            if (isAdmin) {
                const response = await api.get('/get_users/');
                setUsers(response.data);
            } else {
                setUsers([loggedInUser]);
            }
        };

        fetchTransactions();
        fetchProducts();
        fetchUsers();
    }, [loggedInUser]);


    const handleProductSearch = async (event) => {
        event.preventDefault();
        try {
            let response;
            if (productSearchTerm === '') {
                response = await api.get('/get_transactions/');
            } else {
                response = await api.get(`/get_transactions_by_product_name/${productSearchTerm}/`);
            }
            setTransactions(response.data);
        } catch (error) {
            if (error.response && error.response.status === 404) {
                setToastMessage('Product not found');
                setShowToast(true);
            } else {
                console.error(error);
            }
        }
    };
    
    const handleUserSearch = async (event) => {
        event.preventDefault();
        try {
            let response;
            if (userSearchTerm === '') {
                response = await api.get('/get_transactions/');
            } else {
                response = await api.get(`/get_transactions_by_user_name/${userSearchTerm}/`);
            }
            setTransactions(response.data);
        } catch (error) {
            if (error.response && error.response.status === 404) {
                setToastMessage('User not found');
                setShowToast(true);
            } else {
                console.error(error);
            }
        }
    };

    const handleSort = (column) => {
        if (sortColumn === column) {
            setSortDirection(!sortDirection);
        } else {
            setSortColumn(column);
            setSortDirection(true);
        }
    };
    
    const sortedTransactions = [...transactions].sort((a, b) => {
        if (a[sortColumn] < b[sortColumn]) {
            return sortDirection ? -1 : 1;
        }
        if (a[sortColumn] > b[sortColumn]) {
            return sortDirection ? 1 : -1;
        }
        return 0;
    });
    
    
    return (
        <div className="container">
            <h1>Transactions</h1>
            <form onSubmit={handleProductSearch} className="mb-3">
                <div className="input-group">
                    <input
                        type="text"
                        name="product"
                        value={productSearchTerm}
                        onChange={(e) => setProductSearchTerm(e.target.value)}
                        placeholder="Search by product name"
                        className="form-control"
                    />
                    <div className="input-group-append">
                        <button type="submit" className="btn btn-outline-secondary">Search</button>
                    </div>
                </div>
            </form>
            {isAdmin && (
                <form onSubmit={handleUserSearch} className="mb-3">
                    <div className="input-group">
                        <input
                            type="text"
                            name="user"
                            value={userSearchTerm}
                            onChange={(e) => setUserSearchTerm(e.target.value)}
                            placeholder="Search by user name"
                            className="form-control"
                        />
                        <div className="input-group-append">
                            <button type="submit" className="btn btn-outline-secondary">Search</button>
                        </div>
                    </div>
                </form>
            )}
                <div className="d-flex justify-content-center align-items-center mb-4" >
                    <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                        <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                    </Toast>
                </div>
        <table className="table table-sm table-bordered table-striped">
            <thead>
                <tr>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('id')}>
                            ID {sortColumn === 'id' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('product_id')}>
                            Product {sortColumn === 'product_id' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('user_id')}>
                            User {sortColumn === 'user_id' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('quantity')}>
                            Quantity {sortColumn === 'quantity' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('price')}>
                            Cost {sortColumn === 'price' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('currency')}>
                            Currency {sortColumn === 'currency' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('transaction_type')}>
                            Type {sortColumn === 'transaction_type' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                    <th scope="col">
                        <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('date')}>
                            Date {sortColumn === 'date' && (sortDirection ? '↓' : '↑')}
                        </button>
                    </th>
                </tr>
            </thead>
            <tbody>
                {sortedTransactions.map((transaction) => (
                    <tr key={transaction.id}>
                        <td>{transaction.id}</td>
                        <td>{products.find(product => product.id === transaction.product_id)?.name}</td>
                        <td>{users.find(user => user.id === transaction.user_id)?.username}</td>
                        <td>{transaction.quantity}</td>
                        <td>{transaction.price}</td>
                        <td>{transaction.currency}</td>
                        <td>{transaction.transaction_type}</td>
                        <td>{transaction.date}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
    );
};

export default Transactions;