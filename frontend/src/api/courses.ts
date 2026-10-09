import client from './client';
import type { Course } from '../types';

export const getCourses = () =>
  client.get<Course[]>('/courses').then((r) => r.data);

export const getCourse = (id: number) =>
  client.get<Course>(`/courses/${id}`).then((r) => r.data);

export const createCourse = (data: Omit<Course, 'id'>) =>
  client.post<Course>('/courses/', data).then((r) => r.data);

export const updateCourse = (id: number, data: Partial<Course>) =>
  client.patch<Course>(`/courses/${id}`, data).then((r) => r.data);

export const deleteCourse = (id: number) =>
  client.delete(`/courses/${id}`);

export const getCourseStudents = (courseId: number) =>
  client.get(`/courses/${courseId}/students`).then((r) => r.data);

export const enrollStudent = (courseId: number, studentId: number) =>
  client.post(`/courses/${courseId}/enroll/${studentId}`).then((r) => r.data);

export const getSessions = (courseId?: number) =>
  client.get('/sessions', { params: courseId ? { course_id: courseId } : {} }).then((r) => r.data);

export const createSession = (data: {
  course_id: number;
  date: string;
  start_time: string;
  end_time: string;
  session_type: string;
}) => client.post('/sessions/', data).then((r) => r.data);

export const getDepartments = () =>
  client.get('/departments').then((r) => r.data);

export const createDepartment = (data: { name: string; code: string }) =>
  client.post('/departments/', data).then((r) => r.data);

export const updateDepartment = (id: number, data: { name?: string; code?: string }) =>
  client.patch(`/departments/${id}`, data).then((r) => r.data);

export const deleteDepartment = (id: number) =>
  client.delete(`/departments/${id}`);
