import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import DeleteModal from './Delete.js';
import UpdateModal from './Update.js';


const Users = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [users, setUsers] = useState([]);
    const [sortColumn, setSortColumn] = useState(null);
    const [sortDirection, setSortDirection] = useState(true); // true for ascending, false for descending

    useEffect(() => {
        const fetchUsers = async () => {
            const response = await api.get('/get_users/');
            setUsers(response.data);
        };
        fetchUsers();
    }, []);

    const handleSort = (column) => {
        if (sortColumn === column) {
            setSortDirection(!sortDirection);
        } else {
            setSortColumn(column);
            setSortDirection(true);
        }
    };

    const sortedUsers = [...users].sort((a, b) => {
        if (a[sortColumn] < b[sortColumn]) {
            return sortDirection ? -1 : 1;
        }
        if (a[sortColumn] > b[sortColumn]) {
            return sortDirection ? 1 : -1;
        }
        return 0;
    });

    return (
        <div className="container">
            <h1>Users</h1>
            <table className="table table-sm table-bordered table-striped">
                <thead>
                    <tr>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('id')}>
                                ID {sortColumn === 'id' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('username')}>
                                Username {sortColumn === 'username' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('email')}>
                                Email {sortColumn === 'email' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('type')}>
                                Type {sortColumn === 'type' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        {isAdmin && (
                            <>
                                <th>Delete</th>
                                <th>Update</th>
                            </>
                        )}
                    </tr>
                </thead>
                <tbody>
                    {sortedUsers.map((user) => (
                        <tr key={user.id}>
                            <td>{user.id}</td>
                            <td>{user.username}</td>
                            <td>{user.email}</td>
                            <td>{user.type}</td>
                            {isAdmin && (
                                <>
                                    <td>
                                        <DeleteModal mode="user" id={user.id} />
                                    </td>
                                    <td>
                                        <UpdateModal mode="user" id={user.id} />
                                    </td>
                                </>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Users;