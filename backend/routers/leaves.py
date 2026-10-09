from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from models.course import Course
from models.leave_request import LeaveRequest, LeaveStatus
from models.user import User
from schemas.leave import LeaveRequestCreate, LeaveRequestRead, LeaveRequestReview
from services.leave_service import process_leave_approval, process_leave_rejection

router = APIRouter(prefix="/leaves", tags=["leaves"])


def _to_read(lr: LeaveRequest) -> LeaveRequestRead:
    return LeaveRequestRead(
        id=lr.id,
        student_id=lr.student_id,
        course_id=lr.course_id,
        from_date=lr.from_date,
        to_date=lr.to_date,
        reason=lr.reason,
        status=lr.status.value if hasattr(lr.status, "value") else lr.status,
        reviewed_by=lr.reviewed_by,
        reviewed_at=lr.reviewed_at,
        created_at=lr.created_at,
    )


@router.post("/", response_model=LeaveRequestRead, status_code=status.HTTP_201_CREATED)
def submit_leave(
    payload: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    lr = LeaveRequest(
        student_id=current_user.id,
        course_id=payload.course_id,
        from_date=payload.from_date,
        to_date=payload.to_date,
        reason=payload.reason,
        status=LeaveStatus.pending,
        created_at=datetime.now(timezone.utc),
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return _to_read(lr)


@router.get("/", response_model=list[LeaveRequestRead])
def list_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if role == "student":
        leaves = (
            db.query(LeaveRequest)
            .filter(LeaveRequest.student_id == current_user.id)
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )
    elif role == "teacher":
        # Teacher sees leaves for courses they teach
        course_ids = [c.id for c in db.query(Course).filter(Course.teacher_id == current_user.id).all()]
        leaves = (
            db.query(LeaveRequest)
            .filter(LeaveRequest.course_id.in_(course_ids))
            .order_by(LeaveRequest.created_at.desc())
            .all()
        )
    else:  # admin sees all
        leaves = db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()
    return [_to_read(lr) for lr in leaves]


@router.get("/{leave_id}", response_model=LeaveRequestRead)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if role == "student" and lr.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return _to_read(lr)


@router.patch("/{leave_id}/review", response_model=LeaveRequestRead)
def review_leave(
    leave_id: int,
    payload: LeaveRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.status != LeaveStatus.pending:
        raise HTTPException(status_code=400, detail="Leave request already reviewed")

    if payload.status == "approved":
        lr.status = LeaveStatus.approved
        process_leave_approval(db, lr, current_user.id)
    elif payload.status == "rejected":
        lr.status = LeaveStatus.rejected
        process_leave_rejection(db, lr)
    else:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    lr.reviewed_by = current_user.id
    lr.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lr)
    return _to_read(lr)
