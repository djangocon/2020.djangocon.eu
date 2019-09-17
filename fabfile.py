import json
from datetime import datetime

from fabric.api import *
from fabric.operations import require
from fabric.context_managers import settings
from fabric.utils import fastprint

from fabvenv import virtualenv
from unipath import Path

SETTINGS_FILE_PATH = Path(__file__).ancestor(1).child('project_settings.json')

with open(SETTINGS_FILE_PATH, 'r') as f:
    # Load settings.
    project_settings = json.loads(f.read())

env.prompts = {
    'Type \'yes\' to continue, or \'no\' to cancel: ': 'yes'
}
env.use_ssh_config = True


def set_stage(stage_name='development'):
    stages = project_settings['stages'].keys()
    if stage_name not in stages:
        raise KeyError('Stage name "{0}" is not a valid stage ({1})'.format(
            stage_name,
            ','.join(stages))
        )
    env.stage = stage_name


@task
def stable():
    set_stage('stable')
    set_project_settings()


@task
def development():
    set_stage('development')
    set_project_settings()


def set_project_settings():
    stage_settings = project_settings['stages'][env.stage]
    if not all(project_settings.items()):
        raise KeyError('Missing values in project settings.')
    env.settings = stage_settings


@task
def deploy(debug='no'):
    """
    Deploys project to previously set stage.
    """
    require('stage', provided_by=(stable, development))
    require('settings', provided_by=(stable, development))
    # Set env.
    env.user = env.settings['user']
    env.host_string = env.settings['host']

    if debug == 'no':
        _hide = ('stderr', 'stdout', 'warnings', 'running')
    else:
        _hide = ()

    with hide(*_hide):
        with lcd(project_settings['local']['code_src_directory']):
            push_repository()
        with cd(env.settings['code_src_directory']):
            pull_repository()
        with virtualenv(env.settings['venv_directory']):
            with cd(env.settings['code_src_directory']):
                install_requirements()
                if project_settings.get('git_submodules', False):
                    pull_repository_submodules()
                migrate_models()
                if project_settings.get('scss', False):
                    compile_scss()
                collect_static()
        restart_application()


@task
def new_release(version, debug='no'):
    """
    GitFlow new release
    """
    require('stage', provided_by=(stable, development))
    require('settings', provided_by=(stable, development))
    # Set env.
    env.user = env.settings['user']
    env.host_string = env.settings['host']

    if debug == 'no':
        _hide = ('stderr', 'stdout', 'warnings', 'running')
    else:
        _hide = ()

    with hide(*_hide):
        local('git flow release start %s' % (version,), capture=True)
        local('git commit -am \'Bumped version to %s\'' % (version,))
        local('git flow release finish -m %s -p %s' % (version, version), capture=True)


def print_status(description):
    def print_status_decorator(fn):
        def print_status_wrapper():
            now = datetime.now().strftime('%H:%M:%S')
            fastprint('({time}) {description}{suffix}'.format(
                time=now,
                description=description.capitalize(),
                suffix='...\n')
            )
            fn()
            now = datetime.now().strftime('%H:%M:%S')
            fastprint('({time}) {description}{suffix}'.format(
                time=now,
                description='...finished ' + description,
                suffix='.\n')
            )

        return print_status_wrapper

    return print_status_decorator


@print_status('pulling repository')
def pull_repository():
    command = 'git pull origin {}'.format(
        env.settings.get('git_branch')
    )
    run(command)


@print_status('pulling submodules repository')
def pull_repository_submodules():
    command = 'git submodule update'
    run(command)


@print_status('pushing repository')
def push_repository():
    command = 'git push --all'
    local(command)
    command = 'git push --tags'
    local(command)


@print_status('collecting static files')
def collect_static():
    run('python manage.py collectstatic')


@print_status('compile scss files')
def compile_scss():
    run('python manage.py compilescss')


@print_status('installing requirements')
def install_requirements():
    with cd(env.settings['code_src_directory']):
        run('pip install -r {0}'.format(env.settings['requirements_file']))


@print_status('migrating models')
def migrate_models():
    run('python manage.py migrate')


@print_status('restarting application')
def restart_application():
    with settings(warn_only=True):
        restart_command = env.settings['restart_command']
        result = run(restart_command)
    if result.failed:
        abort('Could not restart application.')


# noinspection PyShadowingBuiltins
@task
def help():
    message = '''
    Remote updating application with fabric.

    Usage example:

    Deploy to development server:
    fab development deploy

    Deploy to development server with debug:
    fab stable deploy:debug=yes

    Deploy to production server:
    fab stable deploy
    '''
    fastprint(message)
