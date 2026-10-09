from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from models.enrollment import Enrollment
from models.user import User
from services.analytics_service import (
    admin_summary,
    course_day_of_week,
    course_heatmap,
    course_student_ranking,
    course_weekly_trend,
    student_course_stats,
    teacher_summary,
)
from services.attendance_service import get_defaulters

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if role == "admin":
        return admin_summary(db)
    elif role == "teacher":
        return teacher_summary(db, current_user.id)
    elif role == "student":
        stats = student_course_stats(db, current_user.id)
        return {"courses": stats}
    elif role == "parent":
        if not current_user.linked_student_id:
            raise HTTPException(status_code=400, detail="No linked student")
        stats = student_course_stats(db, current_user.linked_student_id)
        return {"courses": stats}
    raise HTTPException(status_code=403, detail="Unknown role")


@router.get("/student/{student_id}/courses")
def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if role == "parent" and current_user.linked_student_id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return student_course_stats(db, student_id)


@router.get("/course/{course_id}/trend")
def get_trend(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return course_weekly_trend(db, course_id)


@router.get("/course/{course_id}/heatmap")
def get_heatmap(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return course_heatmap(db, course_id)


@router.get("/course/{course_id}/day-of-week")
def get_day_of_week(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return course_day_of_week(db, course_id)


@router.get("/defaulters")
def get_defaulters_endpoint(
    course_id: int,
    threshold: float = 75.0,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_defaulters(db, course_id, threshold)


@router.get("/course/{course_id}/students")
def get_course_students_ranked(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return course_student_ranking(db, course_id)
