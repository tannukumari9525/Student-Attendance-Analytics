import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from models.attendance import AttendanceRecord, AttendanceStatus
from models.enrollment import Enrollment
from models.session import Session as SessionModel
from models.user import User
from schemas.attendance import (
    AttendanceBulkCreate,
    AttendanceRecordCreate,
    AttendanceRecordRead,
    AttendanceRecordUpdate,
)
from services.attendance_service import get_attendance_percentage
from services.notification_service import check_and_notify_threshold

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _to_read(r: AttendanceRecord) -> AttendanceRecordRead:
    return AttendanceRecordRead(
        id=r.id,
        session_id=r.session_id,
        student_id=r.student_id,
        status=r.status.value if hasattr(r.status, "value") else r.status,
        marked_by=r.marked_by,
        marked_at=r.marked_at,
        notes=r.notes,
    )


def _parse_status(s: str) -> AttendanceStatus:
    try:
        return AttendanceStatus[s.lower()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {s}")


@router.post("/", response_model=AttendanceRecordRead, status_code=status.HTTP_201_CREATED)
def mark_single(
    payload: AttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    record = AttendanceRecord(
        session_id=payload.session_id,
        student_id=payload.student_id,
        status=_parse_status(payload.status),
        marked_by=current_user.id,
        marked_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.flush()
    # get course_id for threshold check
    session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
    if session:
        check_and_notify_threshold(db, payload.student_id, session.course_id)
    db.commit()
    db.refresh(record)
    return _to_read(record)


@router.post("/bulk", response_model=list[AttendanceRecordRead], status_code=status.HTTP_201_CREATED)
def mark_bulk(
    payload: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    created = []
    for item in payload.records:
        # Upsert: update existing if already marked
        existing = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id == payload.session_id,
                AttendanceRecord.student_id == item.student_id,
            )
            .first()
        )
        if existing:
            existing.status = _parse_status(item.status)
            existing.marked_by = current_user.id
            existing.marked_at = datetime.now(timezone.utc)
            db.flush()
            created.append(existing)
        else:
            record = AttendanceRecord(
                session_id=payload.session_id,
                student_id=item.student_id,
                status=_parse_status(item.status),
                marked_by=current_user.id,
                marked_at=datetime.now(timezone.utc),
            )
            db.add(record)
            db.flush()
            created.append(record)

    # Threshold notifications for all affected students
    student_ids = {item.student_id for item in payload.records}
    for student_id in student_ids:
        check_and_notify_threshold(db, student_id, session.course_id)

    db.commit()
    for r in created:
        db.refresh(r)
    return [_to_read(r) for r in created]


@router.post("/upload-csv", response_model=list[AttendanceRecordRead], status_code=status.HTTP_201_CREATED)
async def upload_csv(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """
    CSV columns: student_id, status
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    created = []
    for row in reader:
        student_id = int(row["student_id"])
        status_str = row["status"].strip().lower()
        existing = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id,
            )
            .first()
        )
        if existing:
            existing.status = _parse_status(status_str)
            existing.marked_by = current_user.id
            existing.marked_at = datetime.now(timezone.utc)
            db.flush()
            created.append(existing)
        else:
            record = AttendanceRecord(
                session_id=session_id,
                student_id=student_id,
                status=_parse_status(status_str),
                marked_by=current_user.id,
                marked_at=datetime.now(timezone.utc),
            )
            db.add(record)
            db.flush()
            created.append(record)

    student_ids = {r.student_id for r in created}
    for student_id in student_ids:
        check_and_notify_threshold(db, student_id, session.course_id)

    db.commit()
    for r in created:
        db.refresh(r)
    return [_to_read(r) for r in created]


@router.get("/session/{session_id}", response_model=list[AttendanceRecordRead])
def get_session_records(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()
    return [_to_read(r) for r in records]


@router.get("/student/{student_id}", response_model=list[AttendanceRecordRead])
def get_student_records(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    # Access control
    if role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if role == "parent":
        if current_user.linked_student_id != student_id:
            raise HTTPException(status_code=403, detail="Access denied")
    records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).all()
    return [_to_read(r) for r in records]


@router.patch("/{record_id}", response_model=AttendanceRecordRead)
def update_record(
    record_id: int,
    payload: AttendanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if payload.status is not None:
        record.status = _parse_status(payload.status)
    if payload.notes is not None:
        record.notes = payload.notes
    record.marked_by = current_user.id
    record.marked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return _to_read(record)
