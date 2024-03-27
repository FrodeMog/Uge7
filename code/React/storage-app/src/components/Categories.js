import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import DeleteModal from './Delete.js';
import UpdateModal from './Update.js';

const Categories = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [categories, setCategories] = useState([]);
    const [sortColumn, setSortColumn] = useState(null);
    const [sortDirection, setSortDirection] = useState(true); // true for ascending, false for descending

    useEffect(() => {
        const fetchCategories = async () => {
            const response = await api.get('/get_categories/');
            setCategories(response.data);
        };
        fetchCategories();
    }, []);

    const handleSort = (column) => {
        if (sortColumn === column) {
            setSortDirection(!sortDirection);
        } else {
            setSortColumn(column);
            setSortDirection(true);
        }
    };

    const sortedCategories = [...categories].sort((a, b) => {
        if (a[sortColumn] < b[sortColumn]) {
            return sortDirection ? -1 : 1;
        }
        if (a[sortColumn] > b[sortColumn]) {
            return sortDirection ? 1 : -1;
        }
        return 0;
    });

    const getParentName = (id) => {
        const parentCategory = categories.find(category => category.id === id);
        return parentCategory ? parentCategory.name : '';
    };

    return (
        <div className="container">
            <h1>Categories</h1>
            <table className="table table-sm table-bordered table-striped">
                <thead>
                    <tr>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('id')}>
                                ID {sortColumn === 'id' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('parent_id')}>
                                Parent ID {sortColumn === 'parent_name' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('parent_id')}>
                                Parent Name {sortColumn === 'parent_name' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('name')}>
                                Name {sortColumn === 'name' && (sortDirection ? '↓' : '↑')}
                            </button>
                        </th>
                        <th>
                            <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('description')}>
                                Description {sortColumn === 'description' && (sortDirection ? '↓' : '↑')}
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
                    {sortedCategories.map((category) => (
                        <tr key={category.id}>
                            <td>{category.id}</td>
                            <td>{category.parent_id}</td>
                            <td>{getParentName(category.parent_id)}</td>
                            <td>{category.name}</td>
                            <td>{category.description}</td>
                            {isAdmin && (
                                <>
                                    <td>
                                        <DeleteModal mode="category" id={category.id} />
                                    </td>
                                    <td>
                                        <UpdateModal mode="category" id={category.id} />
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

export default Categories;