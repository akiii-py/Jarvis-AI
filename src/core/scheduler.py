"""
Scheduling System
Handles reminders and time-based automated tasks
"""

import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
import json
from pathlib import Path


class ScheduledTask:
    """Represents a scheduled task."""
    
    def __init__(self, task_id: str, task_type: str, description: str, 
                 action: str, params: Dict, trigger: str):
        self.task_id = task_id
        self.task_type = task_type  # "reminder", "recurring", "one_time"
        self.description = description
        self.action = action  # "notify", "open_app", "workflow", etc.
        self.params = params
        self.trigger = trigger  # "in 30 minutes", "daily at 9:00", etc.
        self.created_at = datetime.now()
        self.executed_count = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "action": self.action,
            "params": self.params,
            "trigger": self.trigger,
            "created_at": self.created_at.isoformat(),
            "executed_count": self.executed_count
        }


class Scheduler:
    """Manages scheduled tasks and reminders."""
    
    def __init__(self, agent, storage_path: Path):
        self.agent = agent
        self.storage_path = storage_path
        self.tasks: List[ScheduledTask] = []
        self.task_counter = 0
        self._load_tasks()
    
    def _load_tasks(self):
        """Load scheduled tasks from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Recreate tasks (but don't reschedule old one-time tasks)
                    for task_data in data:
                        if task_data["task_type"] == "recurring":
                            # Reschedule recurring tasks
                            task = ScheduledTask(**task_data)
                            self.tasks.append(task)
                            self._schedule_task(task)
            except Exception as e:
                print(f"Could not load scheduled tasks: {e}")
    
    def _save_tasks(self):
        """Save scheduled tasks to disk."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2)
        except Exception as e:
            print(f"Could not save scheduled tasks: {e}")
    
    def add_reminder(self, message: str, delay_minutes: int) -> str:
        """
        Add a one-time reminder.
        
        Args:
            message: Reminder message
            delay_minutes: Minutes until reminder
        
        Returns:
            Task ID
        """
        task_id = f"reminder_{self.task_counter}"
        self.task_counter += 1
        
        task = ScheduledTask(
            task_id=task_id,
            task_type="one_time",
            description=f"Remind: {message}",
            action="notify",
            params={"message": message},
            trigger=f"in {delay_minutes} minutes"
        )
        
        self.tasks.append(task)
        
        # Schedule the reminder
        def reminder_job():
            print(f"\n🔔 Reminder: {message}")
            task.executed_count += 1
            self.tasks.remove(task)
            self._save_tasks()
        
        schedule.every(delay_minutes).minutes.do(reminder_job).tag(task_id)
        self._save_tasks()
        
        return task_id
    
    def add_recurring_task(self, description: str, action: str, 
                          params: Dict, schedule_time: str, frequency: str) -> str:
        """
        Add a recurring task.
        
        Args:
            description: Task description
            action: Action to perform ("open_app", "workflow", etc.)
            params: Action parameters
            schedule_time: Time string (e.g., "09:00")
            frequency: "daily", "hourly", etc.
        
        Returns:
            Task ID
        """
        task_id = f"recurring_{self.task_counter}"
        self.task_counter += 1
        
        task = ScheduledTask(
            task_id=task_id,
            task_type="recurring",
            description=description,
            action=action,
            params=params,
            trigger=f"{frequency} at {schedule_time}"
        )
        
        self.tasks.append(task)
        self._schedule_task(task)
        self._save_tasks()
        
        return task_id
    
    def _schedule_task(self, task: ScheduledTask):
        """Schedule a task with the schedule library."""
        def task_job():
            self._execute_task(task)
            task.executed_count += 1
            self._save_tasks()
        
        # Parse trigger and schedule
        if "daily" in task.trigger.lower():
            # Extract time
            import re
            time_match = re.search(r'(\d{1,2}):(\d{2})', task.trigger)
            if time_match:
                hour, minute = time_match.groups()
                schedule.every().day.at(f"{hour}:{minute}").do(task_job).tag(task.task_id)
        elif "hourly" in task.trigger.lower():
            schedule.every().hour.do(task_job).tag(task.task_id)
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task."""
        try:
            if task.action == "notify":
                print(f"\n🔔 {task.params.get('message', 'Scheduled notification')}")
            
            elif task.action == "open_app":
                app = task.params.get("app")
                if app:
                    self.agent.mac_control.open_app(app)
                    print(f"\n🔔 Scheduled: Opened {app}")
            
            elif task.action == "workflow":
                workflow = task.params.get("workflow")
                if workflow:
                    self.agent.workflows.execute(workflow)
                    print(f"\n🔔 Scheduled: Executed {workflow} workflow")
        
        except Exception as e:
            print(f"Error executing scheduled task: {e}")
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            schedule.clear(task_id)
            self.tasks.remove(task)
            self._save_tasks()
            return True
        return False
    
    def list_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks."""
        return self.tasks
    
    def run_pending(self):
        """Run pending scheduled tasks. Call this in the main loop."""
        schedule.run_pending()
