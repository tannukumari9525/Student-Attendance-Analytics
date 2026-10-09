from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from models.course import Course
from models.enrollment import Enrollment
from models.user import User
from schemas.course import CourseCreate, CourseRead, CourseUpdate
from schemas.user import UserRead

router = APIRouter(prefix="/courses", tags=["courses"])


def _get_course_or_404(course_id: int, db: Session) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if role == "teacher":
        return db.query(Course).filter(Course.teacher_id == current_user.id).all()
    return db.query(Course).all()


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    existing = db.query(Course).filter(Course.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _get_course_or_404(course_id, db)


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    course = _get_course_or_404(course_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    course = _get_course_or_404(course_id, db)
    db.delete(course)
    db.commit()


@router.get("/{course_id}/students", response_model=list[UserRead])
def list_enrolled_students(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _get_course_or_404(course_id, db)
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    students = []
    for e in enrollments:
        u = e.student
        role_val = u.role.value if hasattr(u.role, "value") else u.role
        students.append(
            UserRead(
                id=u.id,
                name=u.name,
                email=u.email,
                role=role_val,
                department_id=u.department_id,
                linked_student_id=u.linked_student_id,
                is_active=u.is_active,
            )
        )
    return students


@router.post("/{course_id}/enroll/{student_id}", status_code=status.HTTP_201_CREATED)
def enroll_student(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    _get_course_or_404(course_id, db)
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.student_id == student_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")
    enrollment = Enrollment(course_id=course_id, student_id=student_id)
    db.add(enrollment)
    db.commit()
    return {"message": "Student enrolled successfully"}


@router.delete("/{course_id}/enroll/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_student(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.student_id == student_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
