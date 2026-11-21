import asyncio
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserProfile
from app.models.report import Subscription
from app.models.experiment import ExperimentCategory, Experiment
from app.core.seed_data import EXPERIMENT_CATEGORIES, EXPERIMENTS
from datetime import datetime, timezone, timedelta

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        def add_cols_if_missing(connection):
            try:
                cursor = connection.connection.cursor()
                cursor.execute("PRAGMA table_info(experiments)")
                existing = [row[1] for row in cursor.fetchall()]
                if "matlab_code" not in existing:
                    cursor.execute("ALTER TABLE experiments ADD COLUMN matlab_code TEXT")
                if "python_code" not in existing:
                    cursor.execute("ALTER TABLE experiments ADD COLUMN python_code TEXT")
                if "viva_questions_json" not in existing:
                    cursor.execute("ALTER TABLE experiments ADD COLUMN viva_questions_json JSON DEFAULT '[]'")
                cursor.execute("PRAGMA table_info(ai_messages)")
                ai_existing = [row[1] for row in cursor.fetchall()]
                if "suggested_code" not in ai_existing:
                    cursor.execute("ALTER TABLE ai_messages ADD COLUMN suggested_code TEXT")
                # MATLAB-Only migration: ensure all existing projects and executions point to octave
                cursor.execute("UPDATE projects SET default_engine = 'octave' WHERE default_engine != 'octave'")
                cursor.execute("UPDATE executions SET engine = 'octave' WHERE engine != 'octave'")
                cursor.execute("UPDATE project_files SET name = 'main.m', path = '/main.m' WHERE name = 'main.py'")
                cursor.execute("DELETE FROM project_files WHERE name = 'main_python.py'")
            except Exception:
                pass
        try:
            await conn.run_sync(add_cols_if_missing)
        except Exception:
            pass

    async with AsyncSessionLocal() as session:
        # 1. Seed Default Admin
        admin_res = await session.execute(select(User).where(User.email == "admin@ece.edu"))
        if not admin_res.scalar_one_or_none():
            admin = User(
                email="admin@ece.edu",
                hashed_password=get_password_hash("AdminPass123!"),
                role="admin",
                is_verified=True,
                is_active=True
            )
            session.add(admin)
            await session.flush()
            profile = UserProfile(
                user_id=admin.id,
                full_name="Dr. System Administrator",
                college_name="National Institute of Technology",
                branch="ECE",
                academic_year=4
            )
            session.add(profile)
            sub = Subscription(
                user_id=admin.id,
                tier="premium",
                monthly_execution_quota=10000,
                monthly_ai_token_quota=1000000,
                quota_reset_at=datetime.now(timezone.utc) + timedelta(days=365)
            )
            session.add(sub)

        # 2. Seed Default Student
        student_res = await session.execute(select(User).where(User.email == "student@ece.edu"))
        if not student_res.scalar_one_or_none():
            student = User(
                email="student@ece.edu",
                hashed_password=get_password_hash("StudentPass123!"),
                role="student",
                is_verified=True,
                is_active=True
            )
            session.add(student)
            await session.flush()
            profile = UserProfile(
                user_id=student.id,
                full_name="Aarav Sharma",
                college_name="IIT Delhi",
                branch="ECE",
                academic_year=3
            )
            session.add(profile)
            sub = Subscription(
                user_id=student.id,
                tier="free",
                monthly_execution_quota=100,
                monthly_ai_token_quota=50000,
                quota_reset_at=datetime.now(timezone.utc) + timedelta(days=30)
            )
            session.add(sub)

        # 3. Seed Experiment Categories
        category_map = {}
        for cat_data in EXPERIMENT_CATEGORIES:
            res = await session.execute(select(ExperimentCategory).where(ExperimentCategory.code == cat_data["code"]))
            cat = res.scalar_one_or_none()
            if not cat:
                cat = ExperimentCategory(
                    name=cat_data["name"],
                    code=cat_data["code"],
                    description=cat_data["description"],
                    display_order=cat_data["display_order"]
                )
                session.add(cat)
                await session.flush()
            category_map[cat_data["code"]] = cat.id

        # 4. Seed / Update Experiments
        for exp_data in EXPERIMENTS:
            res = await session.execute(select(Experiment).where(Experiment.slug == exp_data["slug"]))
            existing_exp = res.scalar_one_or_none()
            cat_id = category_map[exp_data["category_code"]]
            if existing_exp:
                existing_exp.title = exp_data["title"]
                existing_exp.objective = exp_data["objective"]
                existing_exp.theory = exp_data["theory"]
                existing_exp.equations_json = exp_data["equations_json"]
                existing_exp.procedure_json = exp_data["procedure_json"]
                existing_exp.default_code = exp_data["default_code"]
                existing_exp.engine = exp_data["engine"]
                existing_exp.expected_output = exp_data["expected_output"]
                existing_exp.matlab_code = exp_data.get("matlab_code")
                existing_exp.python_code = exp_data.get("python_code")
                existing_exp.viva_questions_json = exp_data.get("viva_questions_json", [])
            else:
                exp = Experiment(
                    category_id=cat_id,
                    title=exp_data["title"],
                    slug=exp_data["slug"],
                    objective=exp_data["objective"],
                    theory=exp_data["theory"],
                    equations_json=exp_data["equations_json"],
                    procedure_json=exp_data["procedure_json"],
                    default_code=exp_data["default_code"],
                    engine=exp_data["engine"],
                    expected_output=exp_data["expected_output"],
                    matlab_code=exp_data.get("matlab_code"),
                    python_code=exp_data.get("python_code"),
                    viva_questions_json=exp_data.get("viva_questions_json", [])
                )
                session.add(exp)

        await session.commit()
        print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    asyncio.run(init_database())
