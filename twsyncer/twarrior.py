from taskw import TaskWarrior

import sys


class TaskWarriorWorker(object):
    def __init__(self, **kwargs):
        self.w = TaskWarrior()
        self.tasks = self.w.load_tasks()
        self.filter_project = kwargs.get('filter_project', None)
        if not self.filter_project:
            print("Project to filter by in Taskwarrior not found, exiting.")
            sys.exit(1)
        self.tasks_pending = None
        self.tasks_completed = None
        self.tasks_active = None

    def initialize(self) -> None:
        tasks_pending = [
            t for t in self.tasks['pending'] if
            t.get('project', False) == self.filter_project]
        tasks_completed = [
            t for t in self.tasks['completed'] if
            t.get('project', False) == self.filter_project]
        print(f'Found {len(tasks_completed)} completed tasks for project '
              f'{self.filter_project} in Taskwarrior DB')
        completed_count = len(tasks_completed)
        tasks_active = [t for t in tasks_pending if t.get('start', False)]
        print(f'Found {len(tasks_active)} active tasks for project '
              f'{self.filter_project} in Taskwarrior DB')
        active_count = len(tasks_active)
        for task in tasks_active:
            tasks_pending.remove(task)  # Only not started now in pending tasks
        print(f'Found {len(tasks_pending)} pending and not active tasks for '
              f'project {self.filter_project} in Taskwarrior DB')
        pending_count = len(tasks_pending)
        # Convert tasks to easy search
        self.tasks_pending = {t['description']: t for t in tasks_pending}
        if len(self.tasks_pending) != pending_count:
            print('Seems you have duplicate descriptions in your pending '
                  'taskwarrior tasks')
        self.tasks_completed = {t['description']: t for t in tasks_completed}
        if len(self.tasks_completed) != completed_count:
            print('Seems you have duplicate descriptions in your completed '
                  'taskwarrior tasks')
        self.tasks_active = {t['description']: t for t in tasks_active}
        for task in self.tasks_active.values():
            task['status'] = 'active'
        if len(self.tasks_active) != active_count:
            print('Seems you have duplicate descriptions in your active '
                  'taskwarrior tasks')
