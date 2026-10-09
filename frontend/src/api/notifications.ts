import client from './client';
import type { Notification } from '../types';

export const getNotifications = () =>
  client.get<Notification[]>('/notifications/').then((r) => r.data);

export const markRead = (id: number) =>
  client.patch<Notification>(`/notifications/${id}/read`).then((r) => r.data);

export const markAllRead = () =>
  client.patch('/notifications/read-all');
