import React, {useState, useEffect} from 'react';
import api from './Api';

const App = () => {
  const [Users, setUsers] = useState([]);
  const [formdata, setFormdata] = useState({
    name: '',
    email: '',
    password: ''
  });

  const fetchUsers = async () => {
    const response = await api.get('/get_users/');
    setUsers(response.data);
  }

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleInputChange = (event) => {
    setFormdata({
      ...formdata,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.get('/get_users/', formdata);
    fetchUsers();
    setFormdata({
      name: '',
      email: '',
      password: ''
    });
  };

  //simple list of all users
  return (
    <div>
      <h1>Users</h1>
      <ul>
        {Users.map((user) => (
          <li key={user.id}>
            <p>{user.username}</p>
            <p>{user.email}</p>
          </li>
        ))}
      </ul>
    </div>
  );


}

export default App;
