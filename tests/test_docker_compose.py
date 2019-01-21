import inspect
import pytest

import docker_compose
import service_template
import structures
import exceptions

def test_load_and_exec():
    """
    it returns new namespace with service file exec result classes
    """
    services = [
    structures.ServiceDef(
        name='pydock',
        build={
            'context': '.',
            'args': {
                'app_name': 'pydock'
            }
        },
        volumes=['.:/pydock'],
        deps=['redis']
        ),
    structures.ServiceDef(
        name='redis',
        image='redis:alpine',
        )
    ]
    code = service_template.generate_service_file(services)
    ns = docker_compose._load_and_exec(code)

    assert inspect.isclass(ns['Pydock']) == True
    assert inspect.isclass(ns['Redis']) == True

def test_validate_dependencies_raises_on_missing_dependencies():
    """
    it detects missing dependencies and raises
    """
    services = [
    structures.ServiceDef(
        name='pydock',
        build={
            'context': '.',
            'args': {
                'app_name': 'pydock'
            }
        },
        volumes=['.:/pydock'],
        deps=['redis']
        ),
    ]

    source = service_template.generate_service_file(services)
    ns = docker_compose._load_and_exec(source)

    with pytest.raises(exceptions.PydockException) as execinfo:
        docker_compose._validate_dependencies(ns)

    assert str(execinfo.value) == "missing dependencies {'redis'} for service Pydock"

def test_generates_docker_compose():
    """
    given valid service definitions, it generates correct docker compose file
    """
    services = [
    structures.ServiceDef(
        name='pydock',
        build={
            'context': '.',
            'args': {
                'app_name': 'pydock'
            }
        },
        volumes=['.:/pydock'],
        deps=['redis']
        ),
    structures.ServiceDef(
        name='redis',
        image='redis:alpine',
        )
    ]
    code = service_template.generate_service_file(services)
    compose_yaml = docker_compose.generate_docker_compose(code)
    assert compose_yaml == {
        'version': '3',
        'services': {
            'pydock': {
                'build': {
                    'context': '.',
                    'args': {
                        'app_name': 'pydock'
                    }
                },
                'volumes': ['.:/pydock'],
                'depends_on': ['redis']
            },
            'redis': {
                'image': 'redis:alpine'
            }
        }
    }





