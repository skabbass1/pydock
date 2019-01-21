import inspect

import yaml

import exceptions

def generate_docker_compose(code):
    ns = _load_and_exec(code)
    _validate_dependencies(ns)
    klasses = _get_classes(ns)
    return _docker_compose_yaml(klasses)



def _load_and_exec(code):
    ns = {}
    exec(code, ns)
    return ns

def _validate_dependencies(ns):
    _missing_dependencies(ns)
    # TODO: Check for circular and duplicate dependencies

def _missing_dependencies(ns):
    klasses = _get_classes(ns)
    keys = klasses.keys()
    for k, v in klasses.items():
        missing_deps = set(v.DEPENDS_ON) - set([k.lower() for k in klasses.keys()])
        if missing_deps:
            raise exceptions.PydockException(f'missing dependencies {missing_deps} for service {k}')

def _get_classes(ns):
    return {k:v for k,v in ns.items() if inspect.isclass(v)}

def _docker_compose_yaml(service_classes):
    attributes = ['BUILD', 'IMAGE', 'VOLUMES', 'DEPENDS_ON']
    services = {}
    for class_name, klass in service_classes.items():
        d = {}
        for attribute in attributes:
            attribute_value = getattr(klass, attribute)
            if attribute_value:
                d[attribute.lower()] = attribute_value
                services[class_name.lower()] = d

    return {
        'version': '3',
        'services': services
    }
