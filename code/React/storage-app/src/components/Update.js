import React, { useState, useContext } from 'react';
import { Modal, Button, Toast } from 'react-bootstrap';
import api from '../api/api.js';

// import the AuthContext
import { AuthContext } from '../contexts/auth.js';

function UpdateModal({ id, mode }) {
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    const [show, setShow] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const handleUpdate = async () => {
        try {
            if(isAdmin){
                if(isAdmin){
                    if (mode === 'product') {
                        //await api.update_(`/update_product/${id}/`);
                    } else if (mode === 'transaction') {
                        //await api.update_(`/update_transaction/${id}/`);
                    } else if (mode === 'category') {
                        //await api.update_(`/update_category/${id}/`);
                    } else if (mode === 'user') {
                        //await api.update_(`/update_user/${id}/`);
                    }
                }
                //setToastMessage(`${mode.charAt(0).toUpperCase() + mode.slice(1)} updated successfully`);
                setToastMessage(`Not implemented yet`);
            } else {
                setToastMessage('You are not authorized to update');
            }
        } catch (error) {
            setToastMessage(`Failed to update ${mode}: ${error}`);
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
                <Modal.Body>Are you sure you want to update this {mode}?</Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Cancel
                    </Button>
                    <Button variant="warning" onClick={handleUpdate}>
                        Update
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

export default UpdateModal;