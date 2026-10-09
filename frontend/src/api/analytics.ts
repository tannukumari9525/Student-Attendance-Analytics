import client from './client';

export const getSummary = () =>
  client.get('/analytics/summary').then((r) => r.data);

export const getStudentCourses = (studentId: number) =>
  client.get(`/analytics/student/${studentId}/courses`).then((r) => r.data);

export const getCourseTrend = (courseId: number) =>
  client.get(`/analytics/course/${courseId}/trend`).then((r) => r.data);

export const getCourseHeatmap = (courseId: number) =>
  client.get(`/analytics/course/${courseId}/heatmap`).then((r) => r.data);

export const getCourseDayOfWeek = (courseId: number) =>
  client.get(`/analytics/course/${courseId}/day-of-week`).then((r) => r.data);

export const getDefaulters = (courseId: number, threshold = 75) =>
  client.get('/analytics/defaulters', { params: { course_id: courseId, threshold } }).then((r) => r.data);

export const getCourseStudentsRanked = (courseId: number) =>
  client.get(`/analytics/course/${courseId}/students`).then((r) => r.data);
