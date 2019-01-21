import pathlib

import pytest
import yaml

import pydock
import structures
import docker_compose
import exceptions

def test_service_dependency_def():
    """
    it correctly generates service dependency definitions
    """
    service_defs = pydock._service_dependency_def(['redis', 'postgres:latest'])
    assert service_defs == [
        structures.ServiceDef(name='redis', build=None, image='redis', volumes=None, deps=None),
        structures.ServiceDef(name='postgres', build=None, image='postgres:latest', volumes=None, deps=None)
    ]

def test_app_service_def():
    """
    Given an app name, it generates the correct service definition
    """
    service_def = pydock._app_service_def(
        'pydock',
        pydock._service_dependency_def(['redis', 'postgres:latest'])
    )

    assert service_def == structures.ServiceDef(
        name='pydock',
        build={'context': '.', 'args': {'app_name': 'pydock'}},
        image=None,
        volumes=['.:/pydock'],
        deps=['redis', 'postgres']
    )

def test_generate_pydock_service_file(cleanup):
    """
    it generates the correct pydock service file
    """
    pydock._generate_pydock_service_file(app_name='pydock', depends_on=['redis', 'postgres'])
    with open('pydock_service_def.py', 'r') as f:
        contents = f.read()

    ns = docker_compose._load_and_exec(contents)

    assert ns['Pydock'].BUILD == {'context': '.', 'args': {'app_name': 'pydock'}}
    assert ns['Pydock'].IMAGE == None
    assert ns['Pydock'].VOLUMES == ['.:/pydock']
    assert ns['Pydock'].DEPENDS_ON == ['redis', 'postgres']

    assert ns['Redis'].BUILD == None
    assert ns['Redis'].IMAGE == 'redis'
    assert ns['Redis'].VOLUMES == None
    assert ns['Redis'].DEPENDS_ON == []

    assert ns['Postgres'].BUILD == None
    assert ns['Postgres'].IMAGE == 'postgres'
    assert ns['Postgres'].VOLUMES == None
    assert ns['Postgres'].DEPENDS_ON == []

def test_generate_docker_compose(cleanup):
    """
    it generates correct docker compose file from service definitions
    """
    pydock._generate_pydock_service_file(app_name='pydock', depends_on=['redis', 'postgres'])
    with open('pydock_service_def.py', 'r') as f:
        contents = f.read()
    pydock._generate_docker_compose(contents)

    with open('docker-compose.yaml', 'r') as f:
        contents = yaml.load(f)

    assert contents == {
        'services':
        {
            'postgres': {
                'image': 'postgres'
            },
            'pydock': {
                'build': {
                    'args': {
                        'app_name': 'pydock'
                    },
                    'context': '.'
                },
                'depends_on': ['redis', 'postgres'],
                'volumes': ['.:/pydock']
            },
            'redis': {
                'image': 'redis'
            }
        },
        'version': '3'
    }

def test_exec_raises():
    """
    it raises if no service definition file found
    """
    with pytest.raises(exceptions.PydockException) as expinfo:
        pydock._exec()

    assert str(expinfo.value) == 'unable to locate service definition file'


@pytest.fixture()
def cleanup():
    yield
    paths = [
        pathlib.Path('pydock_service_def.py'),
        pathlib.Path('docker-compose.yaml'),
    ]
    for p in paths:
        if p.exists():
            p.unlink()




