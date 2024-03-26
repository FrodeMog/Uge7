import React, {useState, useEffect} from 'react';
import api from './Api';
import './App.css';
//npm start

const App = () => {
  const [Users, setUsers] = useState([]);
  const [Products, setProducts] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loggedInUser, setLoggedInUser] = useState(null);


  const fetchUsers = async () => {
    const response = await api.get('/get_users/');
    setUsers(response.data);
  }

  const fetchProducts = async () => {
    const response = await api.get('/get_products/');
    setProducts(response.data);
  }

  const handleUserClick = (user) => {
    setSelectedUser(selectedUser === user ? null : user);
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    try {
      const response = await api.post('/login_user/', { username, password });
      const logged_in_user = response.data;
      console.log(logged_in_user);
      setLoggedInUser(logged_in_user); // Set the logged-in user
    } catch (error) {
      
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="App">
      <nav className="navbar navbar-dark bg-primary">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            Storage App
          </a>
          {loggedInUser ? (
            <span className="navbar-text">
              Logged in as: {loggedInUser.username}
            </span>
          ) : (
            <form className="d-flex" onSubmit={handleLogin}>
              <input className="form-control me-2" type="text" placeholder="Username" aria-label="Username" onChange={e => setUsername(e.target.value)} />
              <input className="form-control me-2" type="password" placeholder="Password" aria-label="Password" onChange={e => setPassword(e.target.value)} />
              <button className="btn btn-primary" type="submit">Login</button>
            </form>
          )}
        </div>
      </nav>
      <h1 className="text-center">Products</h1>
      <ul className="list-unstyled">
      {loggedInUser ? (
        Products.map((product) => (
          <li key={product.id} className="mb-3">
            <div className="card shadow p-3 m-3">
              <div className="card-body">
                <h5 className="card-title">{product.name}</h5>
                <p className="card-text">{product.description}</p>
                <p className="card-text">ID: {product.id}</p>
                <p className="card-text">Price: {product.purchase_price}</p>
                <p className="card-text">Stock: {product.quantity}</p>
                <p className="card-text">Currenct: {product.currency}</p>
              </div>
            </div>
          </li>
        ))
      ) : (
        <div>Please log in to view products</div>
      )}
      </ul>
    </div>
  );
}

export default App;