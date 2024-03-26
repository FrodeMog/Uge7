// Add_Category.js
import React, { useState } from 'react';
import api from '../api/api.js';

const Add_Category = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();

        const category = {
            name,
            description
        };

        try {
            const response = await api.post('/create_category/', category);
            console.log(response.data);
        } catch (error) {
            console.error('Failed to create category:', error);
        }
    };

    return (
        <div className="card container mt-5">
            <div className="card-body">
                <h5 className="card-title">Add Category</h5>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label">Name</label>
                        <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Description</label>
                        <input type="text" className="form-control" value={description} onChange={e => setDescription(e.target.value)} />
                    </div>
                    <button type="submit" className="btn btn-primary">Create Category</button>
                </form>
            </div>
        </div>
    );
};

export default Add_Category;