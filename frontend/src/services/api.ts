// API client for communicating with the FastAPI backend
// Base URL can be overridden via Vite env var: VITE_API_BASE_URL
// Fallback to same-origin '/api' so that reverse proxies work in production.
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api';
const CSRF_HEADER = 'X-CSRF-Token';
const CSRF_STORAGE_KEY = 'csrf_token';
const USER_STORAGE_KEY = 'session_user';

// Throttle unauthorized dispatch to at most one every 2 seconds
let lastUnauthorizedDispatch = 0;
function dispatchUnauthorizedThrottled() {
  const now = Date.now();
  if (now - lastUnauthorizedDispatch > 2000) {
    window.dispatchEvent(new CustomEvent('api:unauthorized'));
    lastUnauthorizedDispatch = now;
  }
}

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

    // Attach CSRF token for state-changing methods if present
    const method = (options.method || 'GET').toUpperCase();
    const isMutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
    const csrfToken = (isMutating && typeof window !== 'undefined') ? sessionStorage.getItem(CSRF_STORAGE_KEY) : null;

    const config: RequestInit = {
      credentials: 'include', // Include cookies for session management
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken ? { [CSRF_HEADER]: csrfToken } : {}),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      console.log(`API ${config.method || 'GET'} ${url} -> ${response.status}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        if (response.status === 401) {
          dispatchUnauthorizedThrottled();
        }
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
  const res = await this.request<{ message: string; user_id: string; user_name: string }>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    await this.refreshCsrfToken();
    return res;
  }

  async signup(userData: { name: string; email: string; password: string }): Promise<{ message: string; user_id: string; user_name: string }> {
  const res = await this.request<{ message: string; user_id: string; user_name: string }>('/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    await this.refreshCsrfToken();
    return res;
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
  const res = await this.request<{ message: string }>('/logout', {
      method: 'POST',
    });
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(CSRF_STORAGE_KEY);
      sessionStorage.removeItem(USER_STORAGE_KEY);
    }
    return res;
  }

  // User endpoints
  async createUser(userData: { name: string; email: string }): Promise<User> {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  /**
   * Get current session status. Returns authenticated flag and optional user.
   * Prefer this over getCurrentUser() which required auth and returned an array.
   */
  async getSession(): Promise<SessionResponse> {
    const session = await this.request<SessionResponse>('/session');
    if (typeof window !== 'undefined') {
      if (session.authenticated && session.user) {
        sessionStorage.setItem(USER_STORAGE_KEY, JSON.stringify(session.user));
      } else {
        sessionStorage.removeItem(USER_STORAGE_KEY);
      }
    }
    return session;
  }

  // Backwards compatibility (deprecated): returns an array for legacy code paths.
  async getCurrentUser(): Promise<User[]> {
    const session = await this.getSession();
    if (session.authenticated && session.user) {
      return [{ ...session.user, balance: session.user.balance || {} } as User];
    }
    return [];
  }

  private async refreshCsrfToken(): Promise<void> {
    try {
      const data = await this.request<{ csrf_token: string; header: string }>('/csrf-token');
      if (data?.csrf_token && typeof window !== 'undefined') {
        sessionStorage.setItem(CSRF_STORAGE_KEY, data.csrf_token);
      }
    } catch (e) {
      // Non-fatal; log quietly.
      console.warn('Failed to refresh CSRF token', e);
    }
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
  // Balance is a mapping of other_user_id -> net amount (positive means this user owes that user, negative means is owed)
  balance: Record<string, number>;
}

export interface SessionResponse {
  authenticated: boolean;
  user?: User;
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
  category?: string;
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