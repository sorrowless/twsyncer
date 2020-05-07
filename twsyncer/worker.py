from github import ProjectCard
from github.Issue import Issue
from typing import List, Dict


class Worker(object):
    def __init__(self, gh_worker, tw_worker):
        self.gh = gh_worker
        self.tw = tw_worker
        self.columns_map = {}
        self.columns_data = {}

    def find_missing_tw_tasks(
            self, issues: List[Issue], tasks: Dict[str, dict]) -> List[Issue]:
        """Find issues in Github for which there are no tasks in TW

        There can be cases when someone created an Issue on Github and we need
        to ensure it in local TaskWarrior database. Get the list with issues
        and return list with those issues for which TaskWarrior tasks has to be
        created
        """
        tw_missing_tasks = []
        for issue in issues:
            if issue.title not in tasks:
                tw_missing_tasks.append(issue)
        # TODO(sbog): convert it to generator
        return tw_missing_tasks

    def find_missing_gh_issues(
            self, issues: List[Issue], tasks: Dict[str, dict]) -> List[dict]:
        """Find tasks in TW for which there are no issues in Github

        There are cases when one creates task in local TaskWarrior and we need
        to create according issue for it on Github.
        """
        gh_missing_issues = []
        # Rebuild issues list to faster search.
        issues = {issue.title: issue for issue in issues}
        for task_description in tasks:
            if task_description not in issues:
                gh_missing_issues.append(tasks[task_description])
        # TODO(sbog): convert it to generator
        return gh_missing_issues

    def find_pairs_to_check(
            self, issues: List[Issue], tasks: Dict[str, dict]) -> List[dict]:
        pairs_to_check = []
        for issue in issues:
            if issue.title in tasks:
                pairs_to_check.append({
                    'issue': issue,
                    'task': tasks[issue.title]
                })
                print(f'Found existing both in tw and in Github task: '
                      f'{issue.title}')
        # TODO(sbog): convert it to generator
        return pairs_to_check

    def resolve(self) -> None:
        """Resolve changes between Github and Taskwarrior

        Get Github and Taskwarrior instances and check for all the issues in
        Github which don't exists in Taskwarrior. Then check for all the tasks
        in Taskwarrior which don't exists in Github. Then create all missing
        tasks, all missing issues and fix states of those which are wrong for
        both sides.
        """
        # Create task list with all the tasks we have for given project
        tasks = {}
        for task_type in ['pending', 'completed', 'active']:
            task_dict = getattr(self.tw, f'tasks_{task_type}')
            tasks.update(task_dict)

        # Find all Github issues we do not have in Taskwarrior
        issues_to_create_tw = self.find_missing_tw_tasks(self.gh.issues, tasks)
        print(f'Found {len(issues_to_create_tw)} issues to create in '
              f'Taskwarrior overall')
        # Create all missing tasks
        for issue in issues_to_create_tw:
            self.tw_create_task_from_issue(issue)

        # Find all Github issues found in TaskWarrior - need to check statuses
        pairs_to_check = self.find_pairs_to_check(self.gh.issues, tasks)
        print(f'Found {len(pairs_to_check)} items with the same description '
              f'in TW and Github. Need to check their statuses')
        # Modify existing issues with wrong status
        self.github_modify_issues(pairs_to_check)

        # Find all TaskWarrior tasks we do not have in Github
        tasks_to_create_gh = self.find_missing_gh_issues(self.gh.issues, tasks)
        print(f"Found {len(tasks_to_create_gh)} issues to create in Github")
        # Create missing on Github issues
        self.github_create_issues(tasks_to_create_gh)

    def github_create_issues(self, tasks: List[dict]) -> None:
        for task in tasks:
            card_column = self.gh.tw_to_github_states[task['status']][0]
            print(f'  {self.gh.dry_run_prefix}Create new issue from task '
                  f'"{task["description"]}" in column {card_column}')
            if not self.gh.dry_run:
                new_issue = self.github_create_issue_from_task(
                    self.gh.issues_repo, task)
                self.github_create_card_from_issue(card_column, new_issue)

    def github_create_issue_from_task(self, repo, task):
        print(f'task is {task}')
        issue_title = task['description']
        issue = repo.create_issue(title=issue_title)
        return issue

    def github_create_card_from_issue(
            self, card_column_name: str, issue: Issue) -> ProjectCard:
        column = self.get_columns_map()[card_column_name]
        new_card = column.create_card(
            content_id=issue.id,
            content_type="Issue"
        )
        return new_card

    def tw_create_task_from_issue(self, issue: Issue) -> None:
        pass

    def get_columns_map(self) -> List[dict]:
        print(f"  Create columns mapping")
        if self.columns_map:
            return self.columns_map

        project_columns = self.gh.project.get_columns()
        for column in project_columns:
            self.columns_map[column.name] = column
        return self.columns_map

    def get_columns_data(self) -> List[dict]:
        if self.columns_data:
            return self.columns_data
        project_columns = self.get_columns_map()
        for column in project_columns.values():
            print(f"  Process column {column.name}")
            # Get real cards
            cards = column.get_cards(archived_state='all')
            print(f'    Processing {cards.totalCount} cards in column '
                  f'{column.name}')
            for index, card in enumerate(cards):
                if index > 9 and index % 10 == 0:
                    print(f'      Processed {index} cards')
                card_content = card.get_content()
                if type(card_content) != Issue:
                    print(f"    Looks that card '{card}' content is not an "
                          f"issue but {type(card_content)}, skip managing it")
                    continue
                issue_data = {}
                self.columns_data[card_content.title] = issue_data
                issue_data['card'] = card
                issue_data['issue'] = card_content
                issue_data['column'] = column
                issue_data['column_name'] = column.name
        return self.columns_data

    def github_modify_issues(self, datalist: List[dict]) -> None:
        print('Check if any issue should be moved to different column')
        self.get_columns_data()
        # Now we have all the columns data cached locally
        # Let's compare datalist issues with real ones
        for index, hsh in enumerate(datalist):
            if index % 10 == 0 and index > 9:
                print(f"  Processed {index} pairs 'task:issue'")
            issue = hsh['issue']
            task = hsh['task']
            task_status = task['status']
            issue_data = self.columns_data[issue.title]
            column_from_move_name = issue_data['column_name']
            # Move cards with issues to proper columns
            if issue_data['column_name'] not in \
                    self.gh.tw_to_github_states[task_status]:
                # We found an issue for which taskwarrior task was changed.
                # Let's move it to proper column - it's the first we found for
                # our state from the map
                column_to_move = self.columns_map[
                    self.gh.tw_to_github_states[task_status][0]]
                card_to_move = issue_data['card']
                print(f'  {self.gh.dry_run_prefix}Move issue "{issue}" from '
                      f'column "{column_from_move_name}" to column '
                      f'"{column_to_move.name}"')
                if not self.gh.dry_run:
                    card_to_move.move(position='top', column=column_to_move)
            # Close issues for tasks with 'completed' state
            if issue.state == 'open' and task_status == 'completed':
                print(f'  Move issue "{issue}" to "closed"')
                issue.edit(state='closed')
            elif issue.state == 'closed' and task_status != 'completed':
                print(f'  Move issue "{issue}" to "open"')
                issue.edit(state='open')
