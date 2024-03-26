// Register.js
import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Toast from 'react-bootstrap/Toast';
import api from '../api/api.js';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [showToast, setShowToast] = useState(false); 
    const [toastMessage, setToastMessage] = useState('');

    const handleRegister = async (event) => {
        event.preventDefault();

        const user = {
            username,
            password,
            email
        };

        try {
            const response = await api.post('/create_user/', user);
            console.log(response.data);

            setToastMessage('User: '+user.username+' created successfully!');
            setShowToast(true);
            setTimeout(() => setShowModal(false), 2000);
        } catch (error) {
            console.error('Failed to create user:', error);
            // Extract the error message from the API response
            const errorMessage = error.response?.data?.detail || 'Failed to create user.';
            setToastMessage(errorMessage);
            setShowToast(true);
        }
    };

    return (
        <>
            <button type="button" className="btn btn-primary d-block mx-auto" onClick={() => setShowModal(true)}>
                Register
            </button>

            <Modal show={showModal} onHide={() => setShowModal(false)} aria-labelledby="registerModalLabel">
                <Modal.Header closeButton>
                    <Modal.Title id="registerModalLabel">Register</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <form onSubmit={handleRegister}>
                        <input className="form-control mb-4" type="text" placeholder="Username" aria-label="Username" onChange={e => setUsername(e.target.value)} />
                        <input className="form-control mb-4" type="password" placeholder="Password" aria-label="Password" onChange={e => setPassword(e.target.value)} />
                        <input className="form-control mb-4" type="email" placeholder="Email" aria-label="Email" onChange={e => setEmail(e.target.value)} />
                        <button type="submit" className="btn btn-primary d-block mx-auto">Register</button>
                    </form>
                </Modal.Body>
                <div className="d-flex justify-content-center align-items-center mb-4" >
                    <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                        <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                    </Toast>
                </div>
            </Modal>
        </>
    );
};

export default Register;