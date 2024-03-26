// Products.js
import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import CategorySidebar from './Category_sidebar.js'; // Import the CategorySidebar component

const Products = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        const fetchProducts = async () => {
            const response = await api.get('/get_products/');
            setProducts(response.data);
        };
        fetchProducts();
    }, []);

    useEffect(() => {
        const fetchCategories = async () => {
            const response = await api.get('/get_categories/');
            setCategories(response.data);
        };
        fetchCategories();
    }, []);

    const [selectedCategory, setSelectedCategory] = useState(null);

    const filteredProducts = selectedCategory
        ? products.filter(product => product.category_id === selectedCategory)
        : products;

    return (
        <div className="container">
            <div className="row">
                <div className="col-md-3">
                    <CategorySidebar categories={categories} setSelectedCategory={setSelectedCategory} />
                </div>
                <div className="col-md-9">
                    <h1>Products</h1>
                    <table className="table">
                        <thead>
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Name</th>
                                <th scope="col">Category</th>
                                <th scope="col">Price</th>
                                <th scope='col'>Currency</th>
                                <th scope="col">Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredProducts.map((product, index) => (
                                <tr key={index}>
                                    <td>{product.id}</td>
                                    <td>{product.name}</td>
                                    <td>{categories.find(cat => cat.id === product.category_id)?.name}</td>
                                    <td>{product.purchase_price}</td>
                                    <td>{product.currency}</td>
                                    <td>{product.quantity}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Products;