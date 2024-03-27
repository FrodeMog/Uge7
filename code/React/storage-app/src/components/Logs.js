import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';

const Logs = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [logs, setLogs] = useState([]);
    const [sortColumn, setSortColumn] = useState('id'); // start sorted by id
    const [sortDirection, setSortDirection] = useState(false); // false for descending order

    useEffect(() => {
        const fetchLogs = async () => {
            const response = await api.get('/get_logs/');
            setLogs(response.data);
        };
        fetchLogs();
    }, []);

    const handleSort = (column) => {
        if (sortColumn === column) {
            setSortDirection(!sortDirection);
        } else {
            setSortColumn(column);
            setSortDirection(true);
        }
    };

    const sortedLogs = [...logs].sort((a, b) => {
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
            <h1>Logs</h1>
            <table className="table table-sm table-bordered table-striped">
                <thead>
                    <tr>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('id')}>
                                ID {sortColumn === 'id' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('date')}>
                                Date {sortColumn === 'date' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('func')}>
                                Function {sortColumn === 'func' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('kwargs')}>
                                Arguments {sortColumn === 'kwargs' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('status')}>
                                Status {sortColumn === 'status' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('message')}>
                                Message {sortColumn === 'message' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {sortedLogs.map((log) => (
                        <tr key={log.id}>
                            <td>{log.id}</td>
                            <td>{log.date}</td>
                            <td>{log.func}</td>
                            <td>{log.kwargs}</td>
                            <td>{log.status}</td>
                            <td>{log.message}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Logs;