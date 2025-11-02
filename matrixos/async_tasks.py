"""
Async Task System for MatrixOS

Provides threading-based background task execution so apps can perform
long-running operations (network requests, file I/O) without blocking
the main 60fps event loop.

Apps can schedule tasks that run in worker threads and receive results
via callbacks on the main thread.
"""

import threading
import queue
import time
from typing import Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class TaskResult:
    """Result from a completed background task."""
    task_id: int
    success: bool
    result: Any = None
    error: Exception = None


class BackgroundTask:
    """Represents a background task to be executed."""
    
    _next_id = 1
    _id_lock = threading.Lock()
    
    def __init__(self, func: Callable, callback: Optional[Callable] = None, 
                 app_name: str = "Unknown"):
        """Create a background task.
        
        Args:
            func: Function to execute in background (should be self-contained)
            callback: Function to call on main thread with TaskResult
            app_name: Name of app scheduling this task (for debugging)
        """
        with BackgroundTask._id_lock:
            self.id = BackgroundTask._next_id
            BackgroundTask._next_id += 1
        
        self.func = func
        self.callback = callback
        self.app_name = app_name
        self.result = None
        self.error = None
        self.completed = False
        self.success = False
    
    def execute(self):
        """Execute the task (called by worker thread)."""
        try:
            self.result = self.func()
            self.success = True
        except Exception as e:
            self.error = e
            self.success = False
        finally:
            self.completed = True
    
    def get_result(self) -> TaskResult:
        """Get the task result."""
        return TaskResult(
            task_id=self.id,
            success=self.success,
            result=self.result,
            error=self.error
        )


class AsyncTaskManager:
    """Manages background task execution with thread pool."""
    
    def __init__(self, num_workers: int = 2):
        """Initialize task manager.
        
        Args:
            num_workers: Number of worker threads (default 2 for MatrixOS)
        """
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.running = False
        self.tasks = {}  # task_id -> BackgroundTask
    
    def start(self):
        """Start the worker threads."""
        if self.running:
            return
        
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"MatrixOS-Worker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop all worker threads."""
        self.running = False
        # Add sentinel values to unblock workers
        for _ in range(self.num_workers):
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=2.0)
        
        self.workers.clear()
    
    def _worker_loop(self):
        """Worker thread main loop."""
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.5)
                
                if task is None:  # Sentinel value to exit
                    break
                
                # Execute the task
                task.execute()
                
                # Put result in result queue for main thread
                self.result_queue.put(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def schedule_task(self, func: Callable, callback: Optional[Callable] = None,
                     app_name: str = "Unknown") -> int:
        """Schedule a task to run in background.
        
        Args:
            func: Function to execute (should be self-contained, no shared state)
            callback: Optional callback for when task completes
            app_name: Name of app scheduling task
        
        Returns:
            Task ID for tracking
        
        Example:
            def fetch_data():
                import urllib.request
                response = urllib.request.urlopen('https://api.example.com/data')
                return response.read()
            
            def on_complete(result):
                if result.success:
                    self.data = result.result
                else:
                    print(f"Error: {result.error}")
            
            task_id = task_manager.schedule_task(fetch_data, on_complete, "MyApp")
        """
        task = BackgroundTask(func, callback, app_name)
        self.tasks[task.id] = task
        self.task_queue.put(task)
        return task.id
    
    def process_completed_tasks(self):
        """Process completed tasks and invoke callbacks.
        
        This MUST be called from the main thread, typically in the OS event loop.
        """
        processed = 0
        
        # Process all completed tasks in result queue
        while not self.result_queue.empty():
            try:
                task = self.result_queue.get_nowait()
                
                # Invoke callback on main thread if provided
                if task.callback:
                    try:
                        task.callback(task.get_result())
                    except Exception as e:
                        print(f"Callback error for task {task.id}: {e}")
                
                # Clean up task
                if task.id in self.tasks:
                    del self.tasks[task.id]
                
                processed += 1
                
            except queue.Empty:
                break
        
        return processed
    
    def get_task_count(self) -> dict:
        """Get task queue statistics."""
        return {
            'queued': self.task_queue.qsize(),
            'pending': len(self.tasks),
            'workers': len(self.workers),
            'running': self.running
        }
    
    def cancel_task(self, task_id: int) -> bool:
        """Attempt to cancel a task (only works if not started yet).
        
        Args:
            task_id: ID of task to cancel
        
        Returns:
            True if cancelled, False if already running/completed
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if not task.completed:
                # Can't actually stop a running thread, but we can
                # prevent callback from being invoked
                task.callback = None
                del self.tasks[task_id]
                return True
        return False


# Global task manager instance (initialized by OS)
_task_manager: Optional[AsyncTaskManager] = None


def get_task_manager() -> AsyncTaskManager:
    """Get the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager(num_workers=2)
        _task_manager.start()
    return _task_manager


def schedule_task(func: Callable, callback: Optional[Callable] = None,
                 app_name: str = "Unknown") -> int:
    """Convenience function to schedule a background task.
    
    Args:
        func: Function to run in background
        callback: Callback for when task completes (receives TaskResult)
        app_name: Name of calling app
    
    Returns:
        Task ID
    """
    return get_task_manager().schedule_task(func, callback, app_name)


def process_completed_tasks():
    """Convenience function to process completed tasks.
    
    Should be called from OS event loop every frame.
    """
    return get_task_manager().process_completed_tasks()


# Example usage for apps:
"""
from matrixos.async_tasks import schedule_task, TaskResult

class MyApp(App):
    def fetch_weather(self):
        '''Example: Fetch weather in background'''
        
        def fetch():
            import urllib.request
            import json
            response = urllib.request.urlopen(
                'https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY',
                timeout=5
            )
            return json.loads(response.read())
        
        def on_complete(result: TaskResult):
            if result.success:
                self.weather_data = result.result
                print("Weather updated!")
            else:
                print(f"Fetch failed: {result.error}")
        
        schedule_task(fetch, on_complete, self.name)
    
    def on_activate(self):
        '''Start fetching when app becomes active'''
        self.fetch_weather()
    
    def on_background_tick(self):
        '''Refresh periodically when in background'''
        self.fetch_weather()  # Non-blocking!
"""
