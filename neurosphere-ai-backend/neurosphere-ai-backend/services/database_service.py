"""
Database Service - Database operations and queries
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import Task, ProcessedFile, User

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    @staticmethod
    def create_task(
        db: Session,
        user_id: int,
        task_type: str,
        input_data: str,
        output_data: Optional[str] = None,
        status: str = "completed",
        tokens_used: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task record"""
        try:
            task = Task(
                user_id=user_id,
                task_type=task_type,
                input_data=input_data,
                output_data=output_data,
                status=status,
                tokens_used=tokens_used,
                metadata=metadata or {}
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            logger.info(f"✅ Task created: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_tasks(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Task]:
        """Get user's tasks"""
        try:
            tasks = db.query(Task).filter(
                Task.user_id == user_id
            ).order_by(
                desc(Task.created_at)
            ).offset(skip).limit(limit).all()
            return tasks
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    @staticmethod
    def get_task_by_id(
        db: Session,
        task_id: int,
        user_id: int
    ) -> Optional[Task]:
        """Get specific task by ID"""
        try:
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            return task
        except Exception as e:
            logger.error(f"Error getting task: {str(e)}")
            return None
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[Task]:
        """Update task"""
        try:
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if not task:
                return None
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            db.commit()
            db.refresh(task)
            logger.info(f"✅ Task updated: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def delete_task(
        db: Session,
        task_id: int,
        user_id: int
    ) -> bool:
        """Delete task"""
        try:
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if not task:
                return False
            
            db.delete(task)
            db.commit()
            logger.info(f"✅ Task deleted: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def create_processed_file(
        db: Session,
        user_id: int,
        filename: str,
        file_type: str,
        process_type: str,
        result: str,
        file_size: int = 0
    ) -> ProcessedFile:
        """Create processed file record"""
        try:
            processed_file = ProcessedFile(
                user_id=user_id,
                filename=filename,
                file_type=file_type,
                process_type=process_type,
                result=result,
                file_size=file_size
            )
            db.add(processed_file)
            db.commit()
            db.refresh(processed_file)
            logger.info(f"✅ Processed file created: {processed_file.id}")
            return processed_file
        except Exception as e:
            logger.error(f"Error creating processed file: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_processed_files(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[ProcessedFile]:
        """Get user's processed files"""
        try:
            files = db.query(ProcessedFile).filter(
                ProcessedFile.user_id == user_id
            ).order_by(
                desc(ProcessedFile.created_at)
            ).offset(skip).limit(limit).all()
            return files
        except Exception as e:
            logger.error(f"Error getting processed files: {str(e)}")
            return []
    
    @staticmethod
    def delete_processed_file(
        db: Session,
        file_id: int,
        user_id: int
    ) -> bool:
        """Delete processed file"""
        try:
            file = db.query(ProcessedFile).filter(
                ProcessedFile.id == file_id,
                ProcessedFile.user_id == user_id
            ).first()
            
            if not file:
                return False
            
            db.delete(file)
            db.commit()
            logger.info(f"✅ Processed file deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting processed file: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_statistics(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
            total_files = db.query(ProcessedFile).filter(
                ProcessedFile.user_id == user_id
            ).count()
            
            # Task type breakdown
            task_types = {}
            for task in db.query(Task).filter(Task.user_id == user_id).all():
                task_types[task.task_type] = task_types.get(task.task_type, 0) + 1
            
            stats = {
                'total_tasks': total_tasks,
                'total_files': total_files,
                'task_types': task_types,
                'user_created': user.created_at.isoformat() if user.created_at else None,
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}
