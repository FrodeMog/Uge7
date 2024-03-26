/*
Component to show products
*/
import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';

// import the AuthContext
import { AuthContext } from '../contexts/auth.js';



const Products = () => {
    // get user from context
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [products, setProducts] = useState([]);

    useEffect(() => {
        // get products from the api
        const fetchProducts = async () => {
            const response = await api.get('/get_products/');
            setProducts(response.data);
        };
        fetchProducts();
    }, []);

    return (
        <div className="container">
            <h1>Products</h1>
            <table className="table">
                <thead>
                    <tr>
                        <th scope="col">Name</th>
                        <th scope="col">Price</th>
                        <th scope="col">Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((product, index) => (
                        <tr key={index}>
                            <td>{product.name}</td>
                            <td>{product.purchase_price}</td>
                            <td>{product.quantity}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Products;