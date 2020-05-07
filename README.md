[![Build Status](https://travis-ci.com/sorrowless/twsyncer.svg?branch=master)](https://travis-ci.com/sorrowless/twsyncer)

# Taskwarrior Sync

Taskwarrior Sync is a small tool to sync local Taskwarrior database with some
remote issues tracker. Currently Github is a priority and it is only supported
issue tracker.


### How to run

Install requirements:

`pip install -r requirements.txt`

Export several environment variables:

`TW_DRY_RUN` should be set to `False` to really sync something

`TW_GITHUB_TOKEN` should be set to Github token with proper access permissions

`TW_GITHUB_ORG_LOGIN` is a login of organization in which project with cards
exists

`TW_GITHUB_PROJECT` is a name of the project

`TW_GITHUB_ISSUES_REPO` is a repo from which issues will be linked to project

`TW_FILTER_PROJECT` is a project name in local Taskwarrior to sync upon

After setting all of there ensure that tw_to_github_states mapped
properly.Keys of that mapping are states in TaskWarrior and values are
possible column names in project. In case there will be any inconsistence
between these, according Github issues will be moved across different columns.
Also all the issues in any of the 'completed' column will be closed
automatically.
