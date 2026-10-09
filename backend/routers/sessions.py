from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from database import get_db
from models.session import Session as SessionModel, SessionType
from models.user import User
from schemas.session import SessionCreate, SessionRead, SessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _to_read(s: SessionModel) -> SessionRead:
    return SessionRead(
        id=s.id,
        course_id=s.course_id,
        date=s.date,
        start_time=s.start_time,
        end_time=s.end_time,
        session_type=s.session_type.value if hasattr(s.session_type, "value") else s.session_type,
        conducted_by=s.conducted_by,
    )


@router.get("/", response_model=list[SessionRead])
def list_sessions(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(SessionModel)
    if course_id:
        query = query.filter(SessionModel.course_id == course_id)
    return [_to_read(s) for s in query.order_by(SessionModel.date.desc()).all()]


@router.post("/", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    try:
        session_type_enum = SessionType[payload.session_type]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid session_type: {payload.session_type}")
    session = SessionModel(
        course_id=payload.course_id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        session_type=session_type_enum,
        conducted_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _to_read(session)


@router.get("/{session_id}", response_model=SessionRead)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return _to_read(s)


@router.patch("/{session_id}", response_model=SessionRead)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "session_type" and value is not None:
            try:
                value = SessionType[value]
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid session_type: {value}")
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return _to_read(s)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(s)
    db.commit()
