import argparse
import importlib.util
import os
import shutil
import sys

import docker as docker_lib
import yaml

docker = docker_lib.from_env()

BASE_DIR = os.getcwd()

CONFIG_PY = os.path.join(BASE_DIR, '.dever/config.py')
CONFIG_YML = os.path.join(BASE_DIR, './dever/config.yml')


class DockerApp:

    def __init__(self, app):
        self.working_dir = app['working_dir'].replace('${BASE_DIR}', BASE_DIR)
        self.cleanup_dirs = [cleanup_dir.replace('${BASE_DIR}', BASE_DIR).replace('${WORKING_DIR}', self.working_dir)
                             for cleanup_dir in app['cleanup_dirs']]
        self.container_name = app['container_name']
        self.start_container_command = app['start_container_command']
        self.init_container_command = app['init_container_command']
        self.restart_container_command = app['restart_container_command']

    @staticmethod
    def print_stream(output):
        while True:
            try:
                # print(next(output).decode('utf-8'))
                stdout, stderr = next(output)
                if stdout:
                    sys.stdout.write(stdout.decode('utf-8'))
                elif stderr:
                    sys.stdout.write(stderr.decode('utf-8'))
            except StopIteration:
                break

    def init(self):
        os.chdir(self.working_dir)
        os.system(self.start_container_command)

        container = docker.containers.get(self.container_name)

        print(f'Container status: {container.status}')
        print('Running commands inside container...')
        commands_result = container.exec_run(cmd=self.init_container_command, stream=True, demux=True, tty=True)
        DockerApp.print_stream(commands_result.output)

    def remove(self):
        try:
            container = docker.containers.get(self.container_name)
            container.remove(force=True)

            for cleanup_dir in self.cleanup_dirs:
                shutil.rmtree(cleanup_dir)
        except:
            pass

        try:
            docker.containers.get(self.container_name)
        except:
            print('Container status: stopped')

    def stop(self):
        container = docker.containers.get(self.container_name)
        container.kill()

    def restart(self):
        container = docker.containers.get(self.container_name)
        container.restart()
        print('Restarting app inside container...')
        commands_result = container.exec_run(cmd=self.restart_container_command, stream=True, demux=True, tty=True)
        DockerApp.print_stream(commands_result.output)

    def start(self):
        is_running = False
        containers = docker.containers.list()
        for container in containers:
            if container.name == self.container_name:
                is_running = True
                break

        if is_running:
            self.stop()
            self.start()
        else:
            is_initiated = True
            try:
                docker.containers.get(self.container_name)
            except:
                is_initiated = False

            if is_initiated:
                self.restart()
            else:
                self.init()

    def inside(self):
        container = docker.containers.get(self.container_name)
        os.system(f'docker exec -it {container.id} bash')


class NormalApp:

    def __init__(self, app):
        self.working_dir = app['working_dir'].replace('${BASE_DIR}', BASE_DIR)
        self.cleanup_dirs = [cleanup_dir.replace('${BASE_DIR}', BASE_DIR).replace('${WORKING_DIR}', self.working_dir)
                             for cleanup_dir in app['cleanup_dirs']]
        self.init_command = app['init_command']
        self.start_command = app['start_command']

        os.chdir(self.working_dir)

    def init(self):
        os.system(self.init_command)
        os.system(self.start_command)

    def remove(self):
        try:
            for cleanup_dir in self.cleanup_dirs:
                shutil.rmtree(cleanup_dir)
        except Exception as e:
            print(e)

    def stop(self):
        print('empty function')

    def restart(self):
        os.system(self.start_command)

    def start(self):
        is_initiated = False
        for cleanup_dir in self.cleanup_dirs:
            if os.path.isdir(cleanup_dir):
                is_initiated = True

        if is_initiated:
            self.restart()
        else:
            self.init()

    def inside(self):
        print('empty function')


def parse_yml_config():
    '''
    parse dever_config.yml and return list of apps
    '''

    with open(CONFIG_YML, 'r') as ymlfile:
        return yaml.load(ymlfile)


def parse_py_config():
    '''
    parse dever_config.py and return list of apps
    '''
    spec = importlib.util.spec_from_file_location('', CONFIG_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.apps


def main():

    if os.path.isfile(CONFIG_PY):
        apps = parse_py_config()
    elif os.path.isfile(CONFIG_YML):
        apps = parse_yml_config()

    default_app = None
    for app in apps:
        if app.get('default', False) is True:
            default_app = app['name']
            break

    parser = argparse.ArgumentParser()

    if default_app:
        parser.add_argument('app', nargs='?', default=default_app)
    else:
        parser.add_argument('app')

    parser.add_argument('command', nargs='?', default='start')

    args = parser.parse_args()

    for current_app_data in apps:
        if current_app_data['name'] == args.app:
            app_data = current_app_data

    app_classes = {
        'docker': DockerApp,
        'normal': NormalApp
    }
    app_class = app_classes[app_data['type']]

    app = app_class(app_data)

    if args.command == 'start':
        print('Starting...')
        app.start()

    elif args.command == 'restart':
        print('Restarting...')
        app.restart()

    elif args.command == 'stop':
        print('Stopping...')
        app.stop()

    elif args.command == 'reset':
        print('Resetting...')
        app.remove()
        app.start()

    elif args.command == 'inside':
        print('Going inside container...')
        app.inside()

    elif args.command == 'init':
        print('Starting your server...')
        app.init()

    elif args.command == 'remove':
        print('Removing container...')
        app.remove()
