import client from './client';
import type { TokenResponse } from '../types';

export const login = (email: string, password: string) =>
  client.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data);

export const getMe = () =>
  client.get('/auth/me').then((r) => r.data);
