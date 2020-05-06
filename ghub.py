from github import Github
from github.Issue import Issue
from typing import List

import sys


class GithubWorker(object):
    def __init__(self, **kwargs):
        self.dry_run = kwargs.get('dry_run', True)
        self.dry_run_prefix = "DRY RUN: " if self.dry_run else ""
        dry_run = 'enabled' if self.dry_run else 'disabled'
        print(f'Dry run is {dry_run}')
        self.token = kwargs.get('token', False)
        self.org_login = kwargs.get('org_login', False)
        self.project_name = kwargs.get('project_name', False)
        self.issues_repo_name = kwargs.get('issues_repo_name', False)
        # Real objects from initialize
        self.g = None
        self.org = None
        self.issues_repo = None
        self.project = None
        self.issues = None
        self.tw_to_github_states = None

    def initialize(self) -> None:
        if not self.token:
            print("Cannot found a Github token, exiting.")
            sys.exit(1)
        if not self.org_login:
            print("Cannot found a Github organization name, exiting.")
            sys.exit(1)
        print(f'Github organization to work with is {self.org_login}')
        if not self.project_name:
            print("Cannot found a Github project name, exiting.")
            sys.exit(1)
        print(f'Github project name to link issues is {self.project_name}')
        if not self.issues_repo_name:
            print("Cannot found a Github repo name for creating issues, "
                  "exiting.")
            sys.exit(1)
        print(f'Github repository to work with issues is '
              f'{self.issues_repo_name}')
        # Start initializing
        self.g = Github(self.token)
        self.org = self.g.get_organization(self.org_login)
        if not self.org:
            print("Organization not found on Github, exiting")
            sys.exit(1)
        print(f"Organization found: {self.org}")
        self.issues_repo = self.org.get_repo(self.issues_repo_name)
        if not self.issues_repo:
            print("Repository for issues not found on Github, exiting")
            sys.exit(1)
        print(f"Issues repo found: {self.issues_repo}")
        # Check if we have 'in_sync' label in that repo
        labels = self.issues_repo.get_labels()
        in_sync_label = None
        for label in labels:
            if label.name == 'in_sync':
                in_sync_label = label
                print(f'Found sync label: {label}')
                break
        if not in_sync_label:
            self.issues_repo.create_label(
                    name='in_sync', color='2c82c9',
                    description='Label to sync with local taskwarrior instance'
                    )
        projects = self.org.get_projects()
        for p in projects:
            if p.name == self.project_name:
                self.project = p
                print(f'Github project found: {self.project}')

        if not self.project:
            print("Project not found, exiting")
            sys.exit(1)

    def get_issues(self, state: str = 'all') -> List[Issue]:
        print(f'Get list of issues in {self.issues_repo}')
        self.issues = self.issues_repo.get_issues(state=state)
        return self.issues

    def set_states_mapping(self, mapping: dict) -> None:
        self.tw_to_github_states = mapping
