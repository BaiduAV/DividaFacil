import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Database URL - default to SQLite local file, overridable via env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dividafacil.db")

# Normalize postgres URLs (Render often provides postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+" not in DATABASE_URL:
    # Ensure psycopg2 driver explicit for reliability
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Engine setup depending on backend
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # check_same_thread only valid for SQLite
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Pre-ping helps long-lived connections on hosted DBs
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for group members (many-to-many)
group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", String, ForeignKey("groups.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
)

# Association table for expense split_among (many-to-many)
expense_split_among = Table(
    "expense_split_among",
    Base.metadata,
    Column("expense_id", String, ForeignKey("expenses.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)  # Index for login lookups
    password_hash = Column(
        String, nullable=True
    )  # For authentication, nullable for backward compatibility
    reset_token = Column(String, nullable=True)  # For password reset
    reset_token_expiry = Column(DateTime, nullable=True)  # Reset token expiration
    balance = Column(JSON, default=dict)  # Store as JSON: {"user_id": amount}
    notification_preferences = Column(
        JSON,
        default=lambda: {"email_overdue": True, "email_upcoming": True, "days_ahead_reminder": 3},
    )  # Store notification settings as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships - specify foreign_keys to avoid ambiguity
    groups = relationship("GroupDB", secondary=group_members, back_populates="members")
    paid_expenses = relationship(
        "ExpenseDB", foreign_keys="ExpenseDB.paid_by", back_populates="payer"
    )
    created_expenses = relationship("ExpenseDB", foreign_keys="ExpenseDB.created_by")


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("UserDB", secondary=group_members, back_populates="groups")
    expenses = relationship("ExpenseDB", back_populates="group", cascade="all, delete-orphan")


class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by = Column(
        String, ForeignKey("users.id"), nullable=False, index=True
    )  # Index for user expense queries
    created_by = Column(
        String, ForeignKey("users.id"), nullable=True, index=True
    )  # Index for creator queries
    group_id = Column(
        String, ForeignKey("groups.id"), nullable=False, index=True
    )  # Index for group expense queries
    category = Column(String, nullable=True)  # expense category
    split_type = Column(String, nullable=False)  # EQUAL, EXACT, PERCENTAGE
    split_values = Column(JSON, default=dict)  # Store as JSON: {"user_id": value}
    created_at = Column(
        DateTime, default=datetime.utcnow, index=True
    )  # Index for date-based queries
    installments_count = Column(Integer, default=1)
    first_due_date = Column(DateTime)

    # Relationships
    payer = relationship("UserDB", foreign_keys=[paid_by], back_populates="paid_expenses")
    creator = relationship("UserDB", foreign_keys=[created_by], overlaps="created_expenses")
    group = relationship("GroupDB", back_populates="expenses")
    split_among_users = relationship("UserDB", secondary=expense_split_among)
    installments = relationship(
        "InstallmentDB", back_populates="expense", cascade="all, delete-orphan"
    )


class InstallmentDB(Base):
    __tablename__ = "installments"

    id = Column(String, primary_key=True)
    expense_id = Column(
        String, ForeignKey("expenses.id"), nullable=False, index=True
    )  # Index for expense installment queries
    number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(
        DateTime, nullable=False, index=True
    )  # Index for due date queries (notifications)
    paid = Column(Boolean, default=False, index=True)  # Index for payment status queries
    paid_at = Column(DateTime)

    # Relationships
    expense = relationship("ExpenseDB", back_populates="installments")


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
