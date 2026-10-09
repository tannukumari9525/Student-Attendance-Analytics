import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.attendance import AttendanceRecord, AttendanceStatus
from models.course import Course
from models.enrollment import Enrollment
from models.session import Session as SessionModel
from models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/export/csv")
def export_csv(
    course_id: int,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    query = (
        db.query(
            AttendanceRecord.id,
            AttendanceRecord.student_id,
            User.name.label("student_name"),
            SessionModel.date,
            AttendanceRecord.status,
            AttendanceRecord.notes,
        )
        .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
        .join(User, AttendanceRecord.student_id == User.id)
        .filter(SessionModel.course_id == course_id)
    )
    if from_date:
        query = query.filter(SessionModel.date >= from_date)
    if to_date:
        query = query.filter(SessionModel.date <= to_date)
    rows = query.order_by(SessionModel.date, User.name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["record_id", "student_id", "student_name", "date", "status", "notes"])
    for row in rows:
        status_val = row.status.value if hasattr(row.status, "value") else row.status
        writer.writerow([row.id, row.student_id, row.student_name, row.date, status_val, row.notes or ""])

    output.seek(0)
    filename = f"attendance_{course.code}_{date.today()}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf")
def export_pdf(
    course_id: int,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    query = (
        db.query(
            AttendanceRecord.id,
            AttendanceRecord.student_id,
            User.name.label("student_name"),
            SessionModel.date,
            AttendanceRecord.status,
        )
        .join(SessionModel, AttendanceRecord.session_id == SessionModel.id)
        .join(User, AttendanceRecord.student_id == User.id)
        .filter(SessionModel.course_id == course_id)
    )
    if student_id:
        query = query.filter(AttendanceRecord.student_id == student_id)
    rows = query.order_by(SessionModel.date, User.name).all()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Attendance Report — {course.name} ({course.code})", styles["Title"]))
    elements.append(Paragraph(f"Generated: {date.today()}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["#", "Student ID", "Student Name", "Date", "Status"]]
    for i, row in enumerate(rows, 1):
        status_val = row.status.value if hasattr(row.status, "value") else row.status
        table_data.append([i, row.student_id, row.student_name, str(row.date), status_val])

    if len(table_data) > 1:
        t = Table(table_data, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82d4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8fa")]),
                ]
            )
        )
        elements.append(t)
    else:
        elements.append(Paragraph("No attendance records found.", styles["Normal"]))

    doc.build(elements)
    buf.seek(0)
    filename = f"attendance_{course.code}_{date.today()}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
