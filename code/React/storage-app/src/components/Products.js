import React, { useState, useEffect, useContext } from 'react';
import api from '../api/api.js';
import { AuthContext } from '../contexts/auth.js';
import CategorySidebar from './Category_sidebar.js';
import PurchaseModal from './Purchase.js';
import RestockModal from './Restock.js';
import DeleteModal from './Delete.js';
import UpdateModal from './Update.js';

const Products = () => {
    const { loggedInUser, isAdmin } = useContext(AuthContext);
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [sortColumn, setSortColumn] = useState(null);
    const [sortDirection, setSortDirection] = useState(true); // true for ascending, false for descending

    useEffect(() => {
        const fetchProducts = async () => {
            const response = await api.get('/get_products/');
            setProducts(response.data);
        };
        fetchProducts();
    }, []);

    useEffect(() => {
        const fetchCategories = async () => {
            const response = await api.get('/get_categories/');
            setCategories(response.data);
        };
        fetchCategories();
    }, []);

    const [selectedCategory, setSelectedCategory] = useState(null);

    const filteredProducts = selectedCategory
        ? products.filter(product => product.category_id === selectedCategory)
        : products;

    const handlePurchaseQuantityChange = (productId, quantity) => {
        setProducts(prevProducts => prevProducts.map(product =>
            product.id === productId ? { ...product, quantity: product.quantity - quantity } : product
        ));
    };

    const handleRestockQuantityChange = (productId, quantity) => {
        setProducts(prevProducts => prevProducts.map(product =>
            product.id === productId ? { ...product, quantity: product.quantity + quantity } : product
        ));
    };

    const handleSort = (column) => {
        if (sortColumn === column) {
            setSortDirection(!sortDirection);
        } else {
            setSortColumn(column);
            setSortDirection(true);
        }
    };

    const sortedProducts = [...filteredProducts].sort((a, b) => {
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
            <div className="row">
                <div className="col-md-3">
                    <CategorySidebar categories={categories} setSelectedCategory={setSelectedCategory} />
                </div>
                <div className="col-md-9">
                    <h1>Products</h1>
                    <h4>Category: {selectedCategory ? categories.find(cat => cat.id === selectedCategory)?.name : 'All'}</h4>
                    <table className="table table-sm table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('id')}>
                                        ID {sortColumn === 'id' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('name')}>
                                        Name {sortColumn === 'name' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('category_id')}>
                                        Category {sortColumn === 'category_id' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('purchase_price')}>
                                        Price {sortColumn === 'purchase_price' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                {isAdmin && (
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('restock_price')}>
                                        Restock Price {sortColumn === 'restock_price' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                )}
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('currency')}>
                                        Currency {sortColumn === 'currency' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                <th>
                                    <button className="btn btn-outline-primary text-left text-nowrap" onClick={() => handleSort('quantity')}>
                                        Quantity {sortColumn === 'quantity' && (sortDirection ? '↓' : '↑')}
                                    </button>
                                </th>
                                <th>Purchase</th>
                                {isAdmin && (
                                    <>
                                        <th>Restock</th>
                                        <th>Delete</th>
                                        <th>Update</th>
                                    </>
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedProducts.map((product, index) => (
                                <tr key={index}>
                                    <td>{product.id}</td>
                                    <td>{product.name}</td>
                                    <td>{categories.find(cat => cat.id === product.category_id)?.name}</td>
                                    <td>{product.purchase_price}</td>
                                    {isAdmin && (
                                    <td>{product.restock_price}</td>
                                    )}
                                    <td>{product.currency}</td>
                                    <td>{product.quantity}</td>
                                    <td>
                                        <PurchaseModal product={product} onQuantityChange={handlePurchaseQuantityChange} />
                                    </td>
                                    {isAdmin && (
                                        <>
                                            <td>
                                                <RestockModal product={product} onQuantityChange={handleRestockQuantityChange} />
                                            </td>
                                            <td>
                                                <DeleteModal mode="product" id={product.id} />
                                            </td>
                                            <td>
                                                <UpdateModal mode="product" id={product.id} />
                                            </td>
                                        </>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Products;