from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    name: str
    code: str
    department_id: int
    teacher_id: int
    credits: int
    semester: str
    academic_year: str
    attendance_threshold: float = 75.0


class CourseUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    department_id: int | None = None
    teacher_id: int | None = None
    credits: int | None = None
    semester: str | None = None
    academic_year: str | None = None
    attendance_threshold: float | None = None


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    department_id: int
    teacher_id: int
    credits: int
    semester: str
    academic_year: str
    attendance_threshold: float
