import React, { useState, useEffect, useContext } from 'react';
import { Modal, Button, Toast } from 'react-bootstrap';
import api from '../api/api.js';

// import the AuthContext
import { AuthContext } from '../contexts/auth.js';

function DeleteModal({ id, mode }) {
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    const [show, setShow] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const handleDelete = async () => {
        try {
            if(isAdmin){
                if(isAdmin){
                    if (mode === 'product') {
                        //await api.delete(`/delete_product/${id}/`);
                    } else if (mode === 'transaction') {
                        //await api.delete(`/delete_transaction/${id}/`);
                    } else if (mode === 'category') {
                        //await api.delete(`/delete_category/${id}/`);
                    } else if (mode === 'user') {
                        //await api.delete(`/delete_user/${id}/`);
                    }
                }
                //setToastMessage(`${mode.charAt(0).toUpperCase() + mode.slice(1)} deleted successfully`);
                setToastMessage(`Not implemented yet`);
            } else {
                setToastMessage('You are not authorized to delete');
            }
        } catch (error) {
            setToastMessage(`Failed to delete ${mode}: ${error}`);
        }
        setShowToast(true);
        handleClose();
    };

    return (
        <>
            <Button variant="danger" onClick={handleShow}>
                Delete
            </Button>

            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Confirm Delete</Modal.Title>
                </Modal.Header>
                <Modal.Body>Are you sure you want to delete this {mode}?</Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Cancel
                    </Button>
                    <Button variant="danger" onClick={handleDelete}>
                        Delete
                    </Button>
                </Modal.Footer>
            </Modal>
            <div className="d-flex justify-content-center align-items-center mb-4">
                    <Toast onClose={() => setShowToast(false)} show={showToast} delay={3000} autohide>
                        <Toast.Body className="text-center">{toastMessage}</Toast.Body>
                    </Toast>
                </div>
        </>
    );
}

export default DeleteModal;