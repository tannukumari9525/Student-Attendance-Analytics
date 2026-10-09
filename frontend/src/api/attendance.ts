import client from './client';
import type { AttendanceRecord } from '../types';

export const getSessionRecords = (sessionId: number) =>
  client.get<AttendanceRecord[]>(`/attendance/session/${sessionId}`).then((r) => r.data);

export const getStudentRecords = (studentId: number) =>
  client.get<AttendanceRecord[]>(`/attendance/student/${studentId}`).then((r) => r.data);

export const markSingle = (data: { session_id: number; student_id: number; status: string }) =>
  client.post<AttendanceRecord>('/attendance/', data).then((r) => r.data);

export const markBulk = (data: { session_id: number; records: { student_id: number; status: string }[] }) =>
  client.post<AttendanceRecord[]>('/attendance/bulk', data).then((r) => r.data);

export const updateRecord = (id: number, data: { status?: string; notes?: string }) =>
  client.patch<AttendanceRecord>(`/attendance/${id}`, data).then((r) => r.data);
