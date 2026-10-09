import client from './client';
import type { User } from '../types';

export const getUsers = (role?: string) =>
  client.get<User[]>('/users/', { params: role ? { role } : {} }).then((r) => r.data);

export const createUser = (data: {
  name: string;
  email: string;
  password: string;
  role: string;
  department_id?: number;
  linked_student_id?: number;
}) => client.post<User>('/users/', data).then((r) => r.data);

export const updateUser = (id: number, data: Partial<User>) =>
  client.patch<User>(`/users/${id}`, data).then((r) => r.data);
