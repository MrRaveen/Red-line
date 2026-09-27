const API_URL = 'http://127.0.0.1:5000/api/auth';

export const authService = {
  async register(username, email, password) {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    return response.json();
  },

  async login(email, password) {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (response.ok && data.data?.access_token) {
      localStorage.setItem('access_token', data.data.access_token);
      localStorage.setItem('refresh_token', data.data.refresh_token);
    }
    return { ok: response.ok, data };
  },

  async refresh() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return null;

    const response = await fetch(`${API_URL}/refresh`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${refreshToken}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.data.access_token);
      return data.data.access_token;
    } else {
      this.logoutLocal();
      return null;
    }
  },

  async getProtected() {
    let token = localStorage.getItem('access_token');
    let response = await fetch(`${API_URL}/protected`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    // Handle token expiry
    if (response.status === 401) {
      token = await this.refresh();
      if (token) {
        response = await fetch(`${API_URL}/protected`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }
    }
    return response.json();
  },

  async logout() {
    const token = localStorage.getItem('access_token');
    if (token) {
      await fetch(`${API_URL}/logout`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      }).catch(console.error);
    }
    this.logoutLocal();
  },

  logoutLocal() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};
