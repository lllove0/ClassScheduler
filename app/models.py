from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    hours: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")

    rooms: Mapped[list["Room"]] = relationship(back_populates="store")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    facilities: Mapped[str | None] = mapped_column(String(200))

    store: Mapped[Store] = relationship(back_populates="rooms")
    courses: Mapped[list["Course"]] = relationship(back_populates="room")


class MemberType(Base):
    __tablename__ = "member_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    audience: Mapped[str] = mapped_column(String(20), nullable=False)
    pricing_type: Mapped[str] = mapped_column(String(30), nullable=False)
    total_uses: Mapped[int | None] = mapped_column(Integer)
    valid_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    cards: Mapped[list["StudentCard"]] = relationship(back_populates="member_type")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    student_type: Mapped[str] = mapped_column(String(20), nullable=False)
    guardian_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cards: Mapped[list["StudentCard"]] = relationship(back_populates="student")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="student")


class StudentCard(Base):
    __tablename__ = "student_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    member_type_id: Mapped[int] = mapped_column(ForeignKey("member_types.id"), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    remaining_uses: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    student: Mapped[Student] = relationship(back_populates="cards")
    member_type: Mapped[MemberType] = relationship(back_populates="cards")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="card")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    specialties: Mapped[str] = mapped_column(String(200), nullable=False)

    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")


class CourseType(Base):
    __tablename__ = "course_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    audience: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    default_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    courses: Mapped[list["Course"]] = relationship(back_populates="course_type")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False)
    course_type_id: Mapped[int] = mapped_column(ForeignKey("course_types.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    allow_booking: Mapped[bool] = mapped_column(Boolean, default=True)

    room: Mapped[Room] = relationship(back_populates="courses")
    teacher: Mapped[Teacher] = relationship(back_populates="courses")
    course_type: Mapped[CourseType] = relationship(back_populates="courses")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="course")
    cancellations: Mapped[list["CourseCancellation"]] = relationship(back_populates="course")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    card_id: Mapped[int] = mapped_column(ForeignKey("student_cards.id"), nullable=False)
    booked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="booked")

    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
    card: Mapped[StudentCard] = relationship(back_populates="bookings")
    attendance: Mapped["Attendance"] = relationship(back_populates="booking", uselist=False)


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="absent")
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime)

    booking: Mapped[Booking] = relationship(back_populates="attendance")


class CourseCancellation(Base):
    __tablename__ = "course_cancellations"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    course: Mapped[Course] = relationship(back_populates="cancellations")
