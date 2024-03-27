import React, { useState, useEffect, useContext } from 'react';
import { Modal, Button, Form, Toast } from 'react-bootstrap';
import api from '../api/api';
import { AuthContext } from '../contexts/auth.js';

// import the AuthContext

const RestockModal = ({ product, onQuantityChange }) => {
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    const [show, setShow] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [transaction, setTransaction] = useState({
        product_id: '',
        user_id: '',
        currency: '',
        quantity: '',
        transaction_type: ''
    });

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const handleChange = (e) => {
        const value = e.target.name === 'quantity' ? parseInt(e.target.value, 10) : e.target.value;
        setTransaction({ ...transaction, [e.target.name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if(isAdmin){
            const response = await api.post('/create_transaction/', transaction);
            setToastMessage('Restock successful');
            setShowToast(true);
            onQuantityChange(product.id, transaction.quantity); // Update the quantity
            } else {
                setToastMessage('You are not authorized to restock');
                setShowToast(true);
            }
        } catch (error) {
            console.error('Failed to restock', error);
            const errorMessage = error.response?.data?.detail || 'Failed to restock.';
            setToastMessage(errorMessage);
            setShowToast(true);
        }
    };

    useEffect(() => {
        setTransaction({
            product_id: product.id,
            user_id: loggedInUser.id, // Set the user_id based on your application's state
            currency: product.currency,
            quantity: 1, // Set the initial quantity to 1
            transaction_type: 'restock' // Set the transaction_type to 'restock'
        });
    }, [product]);

    return (
        <>
            <Button variant="primary" onClick={handleShow}>
                Restock
            </Button>

            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Restock</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form onSubmit={handleSubmit}>
                        <Form.Text className="mb-3">
                            You are about to restock: <strong>{product.name}</strong>
                        </Form.Text>
                        <Form.Group controlId="formQuantity">
                            <Form.Label>Restock Quantity</Form.Label>
                            <Form.Control
                                type="number"
                                name="quantity"
                                value={transaction.quantity}
                                onChange={handleChange}
                                min="1"
                                required
                            />
                        </Form.Group>
                        <Form.Group controlId="formCurrency">
                            <Form.Label>Currency</Form.Label>
                            <Form.Control
                                type="text"
                                name="currency"
                                value={transaction.currency}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="d-block mx-auto mt-3">
                            Submit
                        </Button>
                    </Form>
                </Modal.Body>
                <div className="d-flex justify-content-center align-items-center mb-4">
                    <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                        <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                    </Toast>
                </div>
            </Modal>
        </>
    );
};

export default RestockModal;
