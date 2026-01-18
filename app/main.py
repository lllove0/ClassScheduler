from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import (
    Attendance,
    Booking,
    Course,
    CourseCancellation,
    CourseType,
    MemberType,
    Room,
    Store,
    Student,
    StudentCard,
    Teacher,
)
from app.schemas import (
    AttendanceCreate,
    AttendanceOut,
    BookingCancel,
    BookingCreate,
    BookingOut,
    CourseCancellationCreate,
    CourseCancellationOut,
    CourseCreate,
    CourseOut,
    CourseTypeCreate,
    CourseTypeOut,
    MemberTypeCreate,
    MemberTypeOut,
    RoomCreate,
    RoomOut,
    StoreCreate,
    StoreOut,
    StudentCardCreate,
    StudentCardOut,
    StudentCreate,
    StudentOut,
    TeacherCreate,
    TeacherOut,
)
from app.settings import settings

app = FastAPI(title="Dance Studio Booking API")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stores", response_model=StoreOut)
def create_store(payload: StoreCreate, db: Session = Depends(get_db)) -> Store:
    store = Store(**payload.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@app.get("/stores", response_model=list[StoreOut])
def list_stores(db: Session = Depends(get_db)) -> list[Store]:
    return list(db.scalars(select(Store)).all())


@app.post("/rooms", response_model=RoomOut)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)) -> Room:
    if not db.get(Store, payload.store_id):
        raise HTTPException(status_code=404, detail="Store not found")
    room = Room(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@app.get("/rooms", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)) -> list[Room]:
    return list(db.scalars(select(Room)).all())


@app.post("/member-types", response_model=MemberTypeOut)
def create_member_type(payload: MemberTypeCreate, db: Session = Depends(get_db)) -> MemberType:
    member_type = MemberType(**payload.model_dump())
    db.add(member_type)
    db.commit()
    db.refresh(member_type)
    return member_type


@app.get("/member-types", response_model=list[MemberTypeOut])
def list_member_types(db: Session = Depends(get_db)) -> list[MemberType]:
    return list(db.scalars(select(MemberType)).all())


@app.post("/students", response_model=StudentOut)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> Student:
    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.get("/students", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)) -> list[Student]:
    return list(db.scalars(select(Student)).all())


@app.post("/student-cards", response_model=StudentCardOut)
def create_student_card(payload: StudentCardCreate, db: Session = Depends(get_db)) -> StudentCard:
    if not db.get(Student, payload.student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    if not db.get(MemberType, payload.member_type_id):
        raise HTTPException(status_code=404, detail="Member type not found")
    card = StudentCard(**payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@app.get("/student-cards", response_model=list[StudentCardOut])
def list_student_cards(db: Session = Depends(get_db)) -> list[StudentCard]:
    return list(db.scalars(select(StudentCard)).all())


@app.post("/teachers", response_model=TeacherOut)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db)) -> Teacher:
    teacher = Teacher(**payload.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@app.get("/teachers", response_model=list[TeacherOut])
def list_teachers(db: Session = Depends(get_db)) -> list[Teacher]:
    return list(db.scalars(select(Teacher)).all())


@app.post("/course-types", response_model=CourseTypeOut)
def create_course_type(payload: CourseTypeCreate, db: Session = Depends(get_db)) -> CourseType:
    course_type = CourseType(**payload.model_dump())
    db.add(course_type)
    db.commit()
    db.refresh(course_type)
    return course_type


@app.get("/course-types", response_model=list[CourseTypeOut])
def list_course_types(db: Session = Depends(get_db)) -> list[CourseType]:
    return list(db.scalars(select(CourseType)).all())


@app.post("/courses", response_model=CourseOut)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)) -> Course:
    for model, identifier, label in [
        (Store, payload.store_id, "Store"),
        (Room, payload.room_id, "Room"),
        (Teacher, payload.teacher_id, "Teacher"),
        (CourseType, payload.course_type_id, "Course type"),
    ]:
        if not db.get(model, identifier):
            raise HTTPException(status_code=404, detail=f"{label} not found")
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@app.get("/courses", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course)).all())


@app.post("/bookings", response_model=BookingOut)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)) -> Booking:
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.status != "scheduled" or not course.allow_booking:
        raise HTTPException(status_code=400, detail="Course is not open for booking")
    card = db.get(StudentCard, payload.card_id)
    if not card or not card.active:
        raise HTTPException(status_code=404, detail="Student card not found")
    if card.student_id != payload.student_id:
        raise HTTPException(status_code=400, detail="Student card does not belong to student")
    if card.valid_until < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Student card is expired")
    if card.remaining_uses is not None and card.remaining_uses <= 0:
        raise HTTPException(status_code=400, detail="No remaining uses")

    existing = db.execute(
        select(Booking).where(
            Booking.student_id == payload.student_id,
            Booking.course_id == payload.course_id,
            Booking.status == "booked",
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Already booked")

    booked_count = db.execute(
        select(Booking).where(Booking.course_id == payload.course_id, Booking.status == "booked")
    ).scalars().all()
    if len(booked_count) >= course.capacity:
        raise HTTPException(status_code=400, detail="Course is full")

    booking = Booking(**payload.model_dump())
    if card.remaining_uses is not None:
        card.remaining_uses -= 1
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.post("/bookings/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    payload: BookingCancel,
    db: Session = Depends(get_db),
) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != "booked":
        raise HTTPException(status_code=400, detail="Booking cannot be cancelled")
    course = booking.course
    now = datetime.now(timezone.utc)
    if course.starts_at.replace(tzinfo=timezone.utc) - now < timedelta(minutes=settings.cancel_limit_minutes):
        raise HTTPException(status_code=400, detail="Cancellation window has passed")
    booking.status = "cancelled"
    if booking.card.remaining_uses is not None:
        booking.card.remaining_uses += 1
    db.commit()
    db.refresh(booking)
    return booking


@app.post("/attendances", response_model=AttendanceOut)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)) -> Attendance:
    booking = db.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != "booked":
        raise HTTPException(status_code=400, detail="Booking not active")
    attendance = Attendance(**payload.model_dump())
    booking.status = "attended"
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@app.post("/course-cancellations", response_model=CourseCancellationOut)
def create_course_cancellation(
    payload: CourseCancellationCreate,
    db: Session = Depends(get_db),
) -> CourseCancellation:
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    status_value = "pending"
    if payload.requested_by == "admin":
        status_value = "approved"
    cancellation = CourseCancellation(
        course_id=payload.course_id,
        reason=payload.reason,
        requested_by=payload.requested_by,
        status=status_value,
    )
    db.add(cancellation)
    if status_value == "approved":
        _apply_course_cancellation(course, db)
    db.commit()
    db.refresh(cancellation)
    return cancellation


@app.post("/course-cancellations/{cancellation_id}/approve", response_model=CourseCancellationOut)
def approve_course_cancellation(
    cancellation_id: int,
    db: Session = Depends(get_db),
) -> CourseCancellation:
    cancellation = db.get(CourseCancellation, cancellation_id)
    if not cancellation:
        raise HTTPException(status_code=404, detail="Cancellation request not found")
    if cancellation.status != "pending":
        raise HTTPException(status_code=400, detail="Cancellation already processed")
    course = cancellation.course
    cancellation.status = "approved"
    _apply_course_cancellation(course, db)
    db.commit()
    db.refresh(cancellation)
    return cancellation


def _apply_course_cancellation(course: Course, db: Session) -> None:
    course.status = "cancelled"
    bookings = db.execute(
        select(Booking).where(Booking.course_id == course.id, Booking.status == "booked")
    ).scalars()
    for booking in bookings:
        booking.status = "cancelled"
        if booking.card.remaining_uses is not None:
            booking.card.remaining_uses += 1


@app.get("/course-cancellations", response_model=list[CourseCancellationOut])
def list_course_cancellations(db: Session = Depends(get_db)) -> list[CourseCancellation]:
    return list(db.scalars(select(CourseCancellation)).all())
