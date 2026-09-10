import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const u = localStorage.getItem('user');
      if (u) setUser(JSON.parse(u));
    }
    setLoading(false);
  }, [token]);

  const login = async (username, password) => {
    const fd = new FormData();
    fd.append('username', username);
    fd.append('password', password);
    const res = await axios.post(`${process.env.REACT_APP_API_URL}/auth/login`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } });
    const { access_token, role, username: uname } = res.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify({ username: uname, role }));
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setToken(access_token);
    setUser({ username: uname, role });
    return res.data;
  };

  const logout = () => {
    localStorage.clear();
    delete axios.defaults.headers.common['Authorization'];
    setToken(null); setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
