// API client for communicating with the FastAPI backend
const API_BASE_URL = '/api';

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

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new ApiError(response.status, errorData.detail || 'Request failed');
      }

      // For 204 No Content responses, return null
      if (response.status === 204) {
        return null as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, 'Network error');
    }
  }

  // Authentication endpoints
  async login(email: string): Promise<{ message: string; user_id: string; user_name: string }> {
    const formData = new FormData();
    formData.append('email', email);

    return this.request('/login', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  }

  async signup(userData: { name: string; email: string }): Promise<{ message: string; user_id: string; user_name: string }> {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
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
  async createGroup(groupData: { name: string }): Promise<Group> {
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

  // Expense endpoints
  async createExpense(
    groupId: string,
    expenseData: {
      description: string;
      amount: number;
      paid_by: string;
      split_type: 'EQUAL' | 'EXACT' | 'PERCENTAGE';
      split_among: string[];
      split_values?: number[];
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
  members: User[];
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
  split_values?: number[];
  installments_count: number;
  first_due_date?: string;
  created_at: string;
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;