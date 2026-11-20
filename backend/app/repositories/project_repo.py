from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from uuid import UUID
from app.models.project import Project, ProjectFile

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Project]:
        stmt = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(desc(Project.updated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_project(
        self, 
        user_id: UUID, 
        name: str, 
        description: Optional[str] = None, 
        default_engine: str = "octave",
        experiment_id: Optional[UUID] = None
    ) -> Project:
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            default_engine=default_engine,
            experiment_id=experiment_id
        )
        self.db.add(project)
        await self.db.flush()

        # Create default entrypoint file
        ext = ".m" if default_engine == "octave" else ".py"
        entry_name = f"main{ext}"
        default_content = (
            "% ECE AI Studio - MATLAB/Octave Simulation\n"
            "clear all; close all; clc;\n\n"
            "t = 0:0.001:1;\n"
            "f = 5; % 5 Hz Sine Wave\n"
            "x = sin(2*pi*f*t);\n\n"
            "figure(1);\n"
            "plot(t, x, 'b-', 'LineWidth', 1.5);\n"
            "grid on;\n"
            "title('5 Hz Sine Wave Simulation');\n"
            "xlabel('Time (s)');\n"
            "ylabel('Amplitude');\n"
            "disp('Sine wave simulation completed successfully.');\n"
        ) if default_engine == "octave" else (
            "# ECE AI Studio - Scientific Python Simulation\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n\n"
            "t = np.linspace(0, 1, 1000)\n"
            "f = 5  # 5 Hz\n"
            "x = np.sin(2 * np.pi * f * t)\n\n"
            "plt.figure(figsize=(8, 4))\n"
            "plt.plot(t, x, 'b-', label='5 Hz Sine')\n"
            "plt.title('5 Hz Sine Wave Simulation')\n"
            "plt.xlabel('Time (s)')\n"
            "plt.ylabel('Amplitude')\n"
            "plt.grid(True)\n"
            "plt.legend()\n"
            "print('Simulation completed.')\n"
        )

        entry_file = ProjectFile(
            project_id=project.id,
            name=entry_name,
            path=f"/{entry_name}",
            content=default_content,
            is_entrypoint=True
        )
        self.db.add(entry_file)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_project(self, project: Project) -> Project:
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()
