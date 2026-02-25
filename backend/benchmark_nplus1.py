import sys
import os
import time
import uuid
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Add backend directory to path to allow imports from src
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.database import SessionLocal, Base, engine, UserDB, GroupDB, ExpenseDB, InstallmentDB
from src.repositories.group_repository import GroupRepository

# Counter for queries
query_count = 0

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1

def setup_benchmark_data(db, num_expenses=50):
    # Create a test user
    user_id = str(uuid.uuid4())
    user = UserDB(id=user_id, name="Test User", email=f"test_{user_id}@example.com")
    db.add(user)

    # Create a group
    group_id = str(uuid.uuid4())
    group = GroupDB(id=group_id, name="Benchmark Group")
    group.members.append(user)
    db.add(group)

    db.flush() # Ensure group and user are in DB

    # Add expenses
    for i in range(num_expenses):
        expense_id = str(uuid.uuid4())
        expense = ExpenseDB(
            id=expense_id,
            description=f"Expense {i}",
            amount=100.0,
            paid_by=user_id,
            group_id=group_id,
            split_type="EQUAL",
            created_at=time.strftime('%Y-%m-%d %H:%M:%S') # use a string for sqlite if needed, but datetime.utcnow is default
        )
        db.add(expense)
        expense.split_among_users.append(user)

        # Add an installment
        installment = InstallmentDB(
            id=str(uuid.uuid4()),
            expense_id=expense_id,
            number=1,
            amount=100.0,
            due_date=time.strftime('%Y-%m-%d %H:%M:%S'),
            paid=False
        )
        db.add(installment)

    db.commit()
    return group_id

def run_benchmark(num_expenses=50):
    global query_count
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        group_id = setup_benchmark_data(db, num_expenses)

        # Start a new session to ensure nothing is cached
        db.close()
        db = SessionLocal()

        # Reset query count
        query_count = 0
        start_time = time.time()

        # Act
        repo = GroupRepository(db)
        group = repo.get_by_id(group_id)

        # Also test get_all which might be used
        # repo.get_all()

        end_time = time.time()

        print(f"Loaded group with {len(group.expenses)} expenses")
        print(f"Time taken: {end_time - start_time:.4f} seconds")
        print(f"Number of queries: {query_count}")

        return query_count, end_time - start_time
    finally:
        db.close()

if __name__ == "__main__":
    num_exp = 100
    if len(sys.argv) > 1:
        num_exp = int(sys.argv[1])
    run_benchmark(num_exp)
