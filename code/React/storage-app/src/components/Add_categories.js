// Add_Category.js
import React, { useState, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import Toast from 'react-bootstrap/Toast';

const Add_Category = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);

    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [parentName, setParentName] = useState(''); // New state variable for parent category

    const [showToast, setShowToast] = useState(false); 
    const [toastMessage, setToastMessage] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();

        const category = {
            name,
            description,
            parent_name: parentName // Include parent category in the category object
        };

        try {
            const response = await api.post('/create_category/', category);
            console.log(response.data);

            setToastMessage('Category: '+category.name+' created successfully!');
            setShowToast(true);
        } catch (error) {
            console.error('Failed to create category:', error);
            const errorMessage = error.response?.data?.detail || 'Failed to create category.';
            setToastMessage(errorMessage);
            setShowToast(true);
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
                    <div className="mb-3">
                        <label className="form-label">Parent Category</label>
                        <input type="text" className="form-control" value={parentName} onChange={e => setParentName(e.target.value)} /> {/* New input field for parent category */}
                    </div>
                    <button type="submit" className="btn btn-primary">Create Category</button>
                </form>
            </div>
            <div className="d-flex justify-content-center align-items-center mb-4" >
                    <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                        <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                    </Toast>
                </div>
        </div>
    );
};

export default Add_Category;