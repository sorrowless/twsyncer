from .config import load_config
from .ghub import GithubWorker
from .twarrior import TaskWarriorWorker
from .worker import Worker

import os


def main():
    config = load_config()
    if not config:
        dry_run = os.environ.get('TW_DRY_RUN', True)
        # Actually you getting str from env, let's roughly convert it
        dry_run = False if dry_run == 'False' else True
        token = os.environ.get('TW_GITHUB_TOKEN', False)

        org_login = os.environ.get('TW_GITHUB_ORG_LOGIN', "")
        project_name = os.environ.get('TW_GITHUB_PROJECT', "")
        issues_repo_name = os.environ.get('TW_GITHUB_ISSUES_REPO', "")
        tw_filter_project = os.environ.get('TW_FILTER_PROJECT', "")
    else:
        dry_run = config.get('dry_run', True)
        dry_run = False if dry_run == 'False' else True
        token = config.get('token', False)
        org_login = config.get('org_login', False)
        project_name = config.get('project_name', False)
        issues_repo_name = config.get('issues_repo', False)
        tw_filter_project = config.get('tw_filter_project', False)
    # We somehow should map Github project columns to states in Taskwarrior. We
    # could use UDA but actually it is way easier to use some mapping to the
    # existing in Taskwarrior states
    tw_to_github_states = {
        'pending': ['Backlog', 'To do'],
        'active': ['In progress'],
        'completed': ['Done', 'Cancelled', 'Feedback Needed']
    }

    gh_worker = GithubWorker(
        dry_run=dry_run,
        token=token,
        org_login=org_login,
        project_name=project_name,
        issues_repo_name=issues_repo_name
    )
    gh_worker.initialize()
    gh_worker.get_issues()
    gh_worker.set_states_mapping(tw_to_github_states)

    # Now start working with taskwarrior
    tw_worker = TaskWarriorWorker(
        filter_project=tw_filter_project
    )
    tw_worker.initialize()

    worker = Worker(gh_worker, tw_worker)
    worker.resolve()


if __name__ == "__main__":
    main()
