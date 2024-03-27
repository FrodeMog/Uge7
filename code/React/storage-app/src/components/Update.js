import React, { useState, useContext, useEffect } from 'react';
import { Modal, Button, Toast } from 'react-bootstrap';
import api from '../api/api.js';

// import the AuthContext
import { AuthContext } from '../contexts/auth.js';

function UpdateModal({ id, mode }) {
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    const [show, setShow] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    // Product state
    const [product, setProduct] = useState(null);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [purchasePrice, setPurchasePrice] = useState('');
    const [restockPrice, setRestockPrice] = useState('');
    const [currency, setCurrency] = useState('');
    const [quantity, setQuantity] = useState('');

    // category state
    const [category, setCategory] = useState(null);
    const [categoryName, setCategoryName] = useState('');
    const [categoryDescription, setCategoryDescription] = useState('');
    const [parentCategory, setParentCategory] = useState('');


    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const handleUpdate = async (event) => {
        event.preventDefault();

        const updatedProduct = {
            name: name,
            description: description || null,
            purchase_price: purchasePrice,
            restock_price: restockPrice,
            currency: currency || null,
            quantity: quantity || null
        };

        const updatedCategory = {
            name: categoryName,
            parent_id: parentCategory || null,
            description: categoryDescription || null
        };

        try {
            if(isAdmin){
                if (mode === 'product') {
                    await api.put(`/update_product/${id}/`, updatedProduct);
                } else if (mode === 'category') {
                    await api.put(`/update_category/${id}/`, updatedCategory);
                }
                setToastMessage(`${mode.charAt(0).toUpperCase() + mode.slice(1)} updated successfully`);
            } else {
                setToastMessage('You are not authorized to update');
            }
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Failed to update';
            setToastMessage(errorMessage);
        }
        setShowToast(true);
        handleClose();
    };

    return (
        <>
            <Button variant="warning" onClick={handleShow}>
                Update
            </Button>

            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Confirm Update</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    Are you sure you want to update this {mode}?
                    {mode === 'product' && (
                    <form onSubmit={handleUpdate}>
                        <div className="mb-3">
                            <label className="form-label">Name</label>
                            <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Description</label>
                            <input type="text" className="form-control" value={description} onChange={e => setDescription(e.target.value)} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Purchase Price</label>
                            <input type="text" className="form-control" value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Restock Price</label>
                            <input type="text" className="form-control" value={restockPrice} onChange={e => setRestockPrice(e.target.value)} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Currency</label>
                            <input type="text" className="form-control" value={currency} onChange={e => setCurrency(e.target.value)} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">Quantity</label>
                            <input type="text" className="form-control" value={quantity} onChange={e => setQuantity(e.target.value)} />
                        </div>
                            <Modal.Footer>
                                <Button variant="secondary" onClick={handleClose}>
                                    Cancel
                                </Button>
                                <Button variant="warning" type="submit">
                                    Update
                                </Button>
                            </Modal.Footer>
                    </form>
                    )}
                    {mode === 'category' && (
                        <form onSubmit={handleUpdate}>
                            <div className="mb-3">
                                <label className="form-label">Category Name</label>
                                <input type="text" className="form-control" value={categoryName} onChange={e => setCategoryName(e.target.value)} required />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Description</label>
                                <input type="text" className="form-control" value={categoryDescription} onChange={e => setCategoryDescription(e.target.value)} />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Parent Category ID</label>
                                <input type="text" className="form-control" value={parentCategory} onChange={e => setParentCategory(e.target.value)} />
                            </div>
                            <Modal.Footer>
                                <Button variant="secondary" onClick={handleClose}>
                                    Cancel
                                </Button>
                                <Button variant="warning" type="submit">
                                    Update
                                </Button>
                            </Modal.Footer>
                        </form>
                    )}
                </Modal.Body>
            </Modal>
            <div className="d-flex justify-content-center align-items-center mb-4">
                <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                    <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                </Toast>
            </div>
        </>
    );
}

export default UpdateModal;

