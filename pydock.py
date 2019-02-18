import pathlib
import os
import subprocess
import tempfile

import click
import yaml

import docker_compose
import structures
import service_template
import exceptions

@click.group()
def cli():
    pass

@cli.command()
@click.option('--depends-on','-d' , multiple=True)
@click.option('--requires-packages', '-r', multiple=True)
def init(depends_on, requires_packages):
    """
    sets up a base Dockerfile and service definition file
    """
    _generate_requirements_file(requires_packages)
    _generate_docker_file()
    _generate_pydock_service_file(
        app_name=_app_name(),
        depends_on=depends_on
    )

@cli.command()
def exec():
    """
    opens a terminal shell in the app container
    """
    _exec()

@cli.command()
def down():
    """
    stops and removes the running containers, networks and volumes
    """
    _down()

def _down():
    subprocess.run(['docker-compose', 'down'])

def _exec():
    contents = _service_def_file_contents()
    _generate_docker_compose(contents)
    _run_docker_compose()

def _app_name():
    return pathlib.Path('.').absolute().name

def _service_def_file_contents():
    path = pathlib.Path('pydock_service_def.py')
    if not path.exists():
        raise exceptions.PydockException('unable to locate service definition file')
    with path.open() as f:
        return f.read()

def _run_docker_compose():
    # set tag for the development docker container
    os.environ['TAG'] = 'latest'
    subprocess.run(
        ['docker-compose', 'run', _app_name(), 'bash'],
    )

def _generate_requirements_file(requires_packages):
    with open('requirements.txt', 'w') as f:
        for package in requires_packages:
            print(package, file=f)

def _generate_docker_file():
    with open('Dockerfile', 'w') as f:
        f.write(_docker_file_template())

def _generate_pydock_service_file(app_name, depends_on):
    dependencies = _service_dependency_def(depends_on)
    app = _app_service_def(
        app_name=app_name,
        service_dependencies=dependencies
    )
    code = service_template.generate_service_file([app] + dependencies)
    with open('pydock_service_def.py', 'w') as f:
        print(code, file=f)

def _generate_docker_compose(code):
    compose_yaml = docker_compose.generate_docker_compose(code)
    with open('docker-compose.yaml', 'w') as f:
        yaml.dump(compose_yaml, f, default_flow_style=False)

def _service_dependency_def(dependencies):
    services = []
    for d in dependencies:
        name = d.split(':')[0] if ':' in d else d
        services.append(
            structures.ServiceDef(
                name=name,
                image=d
            )
        )
    return services

def _app_service_def(app_name, service_dependencies):
    return structures.ServiceDef(
        name=app_name,
        image=f'{app_name}:${{TAG}}',
        build={
            'context': '.',
            'args': {
                'app_name': pathlib.Path('.').absolute().name
            }
        },
        volumes=[f'.:/{app_name}'],
        deps=[s.name for s in service_dependencies]
    )

def _base_image():
    return 'python:3.7-slim'

def _docker_file_template():
    template = '''
FROM python:3.7-slim

ARG app_name

ADD . /$app_name
WORKDIR /$app_name

RUN pip install -r requirements.txt
    '''
    return template

if __name__ == '__main__':
    cli()
