/*
Component to show Users
*/
import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';

// import the AuthContext
import { AuthContext } from '../contexts/auth.js';



const Users = () => {
    // get user from context
    const { loggedInUser } = useContext(AuthContext);
    const [Users, setUsers] = useState([]);

    useEffect(() => {
        // get Users from the api
        const fetchUsers = async () => {
            const response = await api.get('/get_users/');
            setUsers(response.data);
        };
        fetchUsers();
    }, []);

    return (
        <div className="container">
            <h1>Users</h1>
            <table className="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    {Users.map((user) => (
                        <tr key={user.id}>
                            <td>{user.id}</td>
                            <td>{user.username}</td>
                            <td>{user.email}</td>
                            <td>{user.type}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Users;