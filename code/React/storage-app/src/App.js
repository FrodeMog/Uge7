import React, {useState, useEffect} from 'react';
import api from './Api';
import './App.css';

const App = () => {
  const [Users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchUsers = async () => {
    const response = await api.get('/get_users/');
    setUsers(response.data);
  }

  const handleUserClick = (user) => {
    setSelectedUser(selectedUser === user ? null : user);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div>
      <nav className="navbar navbar-dark bg-primary">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            Storage App
          </a>
        </div>
      </nav>
      <h1 className="text-center">Users</h1>
      <ul className="list-unstyled">
      {Users.map((user) => (
        <li key={user.id} className="mb-3">
          <div className="card shadow p-3 m-3" onClick={() => handleUserClick(user)}>
            <div className={`card-body ${selectedUser === user ? 'open' : ''}`}>
              <h5 className="card-title">{user.username}</h5>
              {selectedUser === user && (
                <>
                  <p className="card-text">{user.email}</p>
                  <p className="card-text">ID: {user.id}</p>
                  <p className="card-text">Type: {user.type}</p>
                </>
              )}
            </div>
          </div>
        </li>
      ))}
      </ul>
    </div>
  );
}

export default App;