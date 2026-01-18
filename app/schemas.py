from datetime import datetime

from pydantic import BaseModel


class StoreCreate(BaseModel):
    name: str
    address: str
    phone: str
    hours: str
    status: str = "open"


class StoreOut(StoreCreate):
    id: int

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    store_id: int
    name: str
    capacity: int
    facilities: str | None = None


class RoomOut(RoomCreate):
    id: int

    class Config:
        from_attributes = True


class MemberTypeCreate(BaseModel):
    name: str
    audience: str
    pricing_type: str
    total_uses: int | None = None
    valid_days: int
    price: int


class MemberTypeOut(MemberTypeCreate):
    id: int

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    name: str
    phone: str
    gender: str
    age: int
    student_type: str
    guardian_name: str | None = None


class StudentOut(StudentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StudentCardCreate(BaseModel):
    student_id: int
    member_type_id: int
    valid_until: datetime
    remaining_uses: int | None = None


class StudentCardOut(StudentCardCreate):
    id: int
    active: bool

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    name: str
    phone: str
    specialties: str


class TeacherOut(TeacherCreate):
    id: int

    class Config:
        from_attributes = True


class CourseTypeCreate(BaseModel):
    name: str
    audience: str
    duration_minutes: int
    description: str
    default_capacity: int


class CourseTypeOut(CourseTypeCreate):
    id: int

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    store_id: int
    room_id: int
    teacher_id: int
    course_type_id: int
    starts_at: datetime
    capacity: int
    allow_booking: bool = True


class CourseOut(CourseCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    student_id: int
    course_id: int
    card_id: int


class BookingOut(BookingCreate):
    id: int
    booked_at: datetime
    status: str

    class Config:
        from_attributes = True


class BookingCancel(BaseModel):
    reason: str


class AttendanceCreate(BaseModel):
    booking_id: int
    status: str
    checked_in_at: datetime | None = None


class AttendanceOut(AttendanceCreate):
    id: int

    class Config:
        from_attributes = True


class CourseCancellationCreate(BaseModel):
    course_id: int
    reason: str
    requested_by: str


class CourseCancellationOut(CourseCancellationCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
