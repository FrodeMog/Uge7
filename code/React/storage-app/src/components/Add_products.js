/*
Component to add products
*/
import React, { useState, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';

const Add_Products = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);

    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [categoryId, setCategoryId] = useState('');
    const [categoryName, setCategoryName] = useState('');
    const [purchasePrice, setPurchasePrice] = useState('');
    const [restockPrice, setRestockPrice] = useState('');
    const [currency, setCurrency] = useState('');
    const [quantity, setQuantity] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();

        const product = {
            name,
            description,
            category_id: categoryId,
            category_name: categoryName,
            purchase_price: purchasePrice,
            restock_price: restockPrice,
            currency,
            quantity
        };

        try {
            const response = await api.post('/create_product/', product);
            console.log(response.data);
        } catch (error) {
            console.error('Failed to create product:', error);
        }
    };

    return (
    <div className="card container mt-5">
        <div className="card-body">
            <h5 className="card-title">Add Product</h5>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Name</label>
                    <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Description</label>
                    <input type="text" className="form-control" value={description} onChange={e => setDescription(e.target.value)} />
                </div>
                <div className="mb-3">
                    <label className="form-label">Category ID</label>
                    <input type="text" className="form-control" value={categoryId} onChange={e => setCategoryId(e.target.value)} />
                </div>
                <div className="mb-3">
                    <label className="form-label">Category Name</label>
                    <input type="text" className="form-control" value={categoryName} onChange={e => setCategoryName(e.target.value)} />
                </div>
                <div className="mb-3">
                    <label className="form-label">Purchase Price</label>
                    <input type="number" className="form-control" value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Restock Price</label>
                    <input type="number" className="form-control" value={restockPrice} onChange={e => setRestockPrice(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Currency</label>
                    <input type="text" className="form-control" value={currency} onChange={e => setCurrency(e.target.value)} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Quantity</label>
                    <input type="number" className="form-control" value={quantity} onChange={e => setQuantity(e.target.value)} required />
                </div>
                <button type="submit" className="btn btn-primary">Create Product</button>
            </form>
        </div>
    </div>
    );
};

export default Add_Products;