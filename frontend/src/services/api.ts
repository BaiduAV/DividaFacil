// API client for communicating with the FastAPI backend
const API_BASE_URL = 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      credentials: 'include', // Include cookies for session management
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      console.log(`API ${config.method || 'GET'} ${url} -> ${response.status}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error(`API Error ${response.status}:`, errorData);
        throw new ApiError(response.status, errorData.detail || 'Request failed');
      }

      // For 204 No Content responses, return null
      if (response.status === 204) {
        return null as T;
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        console.error(`API Error:`, error);
        throw error;
      }
      console.error(`Network Error:`, error);
      throw new ApiError(0, 'Network error');
    }
  }

  // Authentication endpoints
  async login(email: string, password: string): Promise<{ message: string; user_id: string; user_name: string }> {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async signup(userData: { name: string; email: string; password: string }): Promise<{ message: string; user_id: string; user_name: string }> {
    return this.request('/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async forgotPassword(email: string): Promise<{ message: string; token?: string }> {
    return this.request('/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async resetPassword(token: string, password: string): Promise<{ message: string }> {
    return this.request('/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, password }),
    });
  }

  async logout(): Promise<{ message: string }> {
    return this.request('/logout', {
      method: 'POST',
    });
  }

  // User endpoints
  async createUser(userData: { name: string; email: string }): Promise<User> {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User[]> {
    return this.request('/users');
  }

  // Group endpoints
  async createGroup(groupData: { name: string; member_ids?: string[]; member_emails?: string[] }): Promise<Group> {
    return this.request('/groups', {
      method: 'POST',
      body: JSON.stringify(groupData),
    });
  }

  async getGroups(): Promise<Group[]> {
    return this.request('/groups');
  }

  async getGroup(groupId: string): Promise<Group> {
    return this.request(`/groups/${groupId}`);
  }

  async deleteGroup(groupId: string): Promise<void> {
    return this.request(`/groups/${groupId}`, {
      method: 'DELETE',
    });
  }

  // Expense endpoints
  async createExpense(
    groupId: string,
    expenseData: {
      description: string;
      amount: number;
      paid_by: string;
      split_type: 'EQUAL' | 'EXACT' | 'PERCENTAGE';
      split_among: string[];
      split_values?: Record<string, number>;
      installments_count?: number;
      first_due_date?: string;
    }
  ): Promise<Expense> {
    return this.request(`/groups/${groupId}/expenses`, {
      method: 'POST',
      body: JSON.stringify(expenseData),
    });
  }

  async getGroupExpenses(groupId: string): Promise<Expense[]> {
    const group = await this.getGroup(groupId);
    return group.expenses || [];
  }

  async getExpenses(): Promise<Expense[]> {
    const groups = await this.getGroups();
    const allExpenses: Expense[] = [];
    
    for (const group of groups) {
      if (group.expenses) {
        allExpenses.push(...group.expenses);
      }
    }
    
    return allExpenses;
  }
}

// Type definitions
export interface User {
  id: string;
  name: string;
  email: string;
  balance: number;
}

export interface Group {
  id: string;
  name: string;
  members: Record<string, User>; // Dictionary with user_id as key
  expenses: Expense[];
  balances: Record<string, number>;
}

export interface Expense {
  id: string;
  description: string;
  amount: number;
  paid_by: string;
  split_type: 'EQUAL' | 'EXACT' | 'PERCENTAGE';
  split_among: string[];
  split_values?: Record<string, number>;
  installments_count: number;
  first_due_date?: string;
  created_at: string;
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;