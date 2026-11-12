/**
 * Platform admin API (/api/v1/platform): the people who run the service log in
 * here and manage schools. Its token is separate from any school login.
 */
import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '../config/apiConfig';

const TOKEN_KEY = 'platformToken';
const ADMIN_KEY = 'platformAdmin';

export interface PlatformAdmin {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface School {
  id: number;
  code: string;
  name: string;
  short_name: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  logo_url: string | null;
  timezone: string;
  currency: string;
  academic_year_start_month: number;
  status: 'ACTIVE' | 'SUSPENDED';
  created_at: string | null;
  users: number;
  students: number;
  teachers: number;
}

// No X-School-Code here: platform routes belong to no school
const client = axios.create({
  baseURL: `${API_BASE_URL}/platform`,
  timeout: API_TIMEOUT,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const onLogin = error.config?.url?.includes('/auth/login');
    if (error.response?.status === 401 && !onLogin) {
      platformAuth.logout();
      window.location.assign('/platform/login');
    }
    return Promise.reject(error);
  }
);

export const platformAuth = {
  isLoggedIn: () => Boolean(localStorage.getItem(TOKEN_KEY)),
  admin: (): PlatformAdmin | null => {
    try {
      return JSON.parse(localStorage.getItem(ADMIN_KEY) || 'null');
    } catch {
      return null;
    }
  },
  login: async (email: string, password: string): Promise<PlatformAdmin> => {
    const { data } = await client.post('/auth/login', { email, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(ADMIN_KEY, JSON.stringify(data.user));
    return data.user;
  },
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ADMIN_KEY);
  },
};

export const platformAPI = {
  listSchools: (params: { search?: string; status?: string }) =>
    client
      .get('/schools', { params: Object.fromEntries(Object.entries(params).filter(([, value]) => value)) })
      .then((response) => response.data.schools as School[]),
  createSchool: (body: Record<string, any>) =>
    client.post('/schools', body, { timeout: 60000 }).then((response) => response.data),
  updateSchool: (id: number, body: Record<string, any>) =>
    client.patch(`/schools/${id}`, body).then((response) => response.data as School),
  suspend: (id: number) => client.post(`/schools/${id}/suspend`).then((response) => response.data as School),
  activate: (id: number) => client.post(`/schools/${id}/activate`).then((response) => response.data as School),
};
