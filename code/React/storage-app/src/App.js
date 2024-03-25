import React, {useState, useEffect} from 'react';
import api from './Api';

const App = () => {
  const [Users, setUsers] = useState([]);

  const fetchUsers = async () => {
    const response = await api.get('/get_users/');
    setUsers(response.data);
  }

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
      <h1>Users</h1>
      <ul className="list-unstyled">
        {Users.map((user) => (
          <li key={user.id} className="mb-3">
            <div className="card shadow">
              <div className="card-body">
                <h5 className="card-title">{user.username}</h5>
                <p className="card-text">{user.email}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );


}

export default App;
