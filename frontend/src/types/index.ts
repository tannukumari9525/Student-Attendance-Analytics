export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'teacher' | 'student' | 'parent';
  department_id: number | null;
  linked_student_id: number | null;
  is_active: boolean;
}

export interface Department {
  id: number;
  name: string;
  code: string;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  department_id: number;
  teacher_id: number;
  credits: number;
  semester: string;
  academic_year: string;
  attendance_threshold: number;
}

export interface Session {
  id: number;
  course_id: number;
  date: string;
  start_time: string;
  end_time: string;
  session_type: string;
  conducted_by: number;
}

export interface AttendanceRecord {
  id: number;
  session_id: number;
  student_id: number;
  status: 'present' | 'absent' | 'late' | 'excused';
  marked_by: number;
  marked_at: string;
  notes: string | null;
}

export interface LeaveRequest {
  id: number;
  student_id: number;
  course_id: number;
  from_date: string;
  to_date: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  reviewed_by: number | null;
  reviewed_at: string | null;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
  notification_type: 'threshold_alert' | 'leave_update' | 'general';
}

export interface CourseAttendanceStat {
  course_id: number;
  course_name: string;
  course_code: string;
  total_sessions: number;
  attendance_percentage: number;
  threshold: number;
}

export interface AnalyticsSummary {
  // admin
  total_students?: number;
  total_teachers?: number;
  total_courses?: number;
  sessions_today?: number;
  defaulter_count?: number;
  // teacher
  courses?: CourseAttendanceStat[] | TeacherCourseStat[];
  total_defaulters?: number;
}

export interface TeacherCourseStat {
  course_id: number;
  course_name: string;
  course_code: string;
  student_count: number;
  total_sessions: number;
  defaulter_count: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
