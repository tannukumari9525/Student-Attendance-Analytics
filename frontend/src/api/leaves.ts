import client from './client';
import type { LeaveRequest } from '../types';

export const submitLeave = (data: {
  course_id: number;
  from_date: string;
  to_date: string;
  reason: string;
}) => client.post<LeaveRequest>('/leaves/', data).then((r) => r.data);

export const getLeaves = () =>
  client.get<LeaveRequest[]>('/leaves/').then((r) => r.data);

export const reviewLeave = (id: number, status: 'approved' | 'rejected') =>
  client.patch<LeaveRequest>(`/leaves/${id}/review`, { status }).then((r) => r.data);
