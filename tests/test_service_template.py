import service_template
import structures

def test_service_template():
    """
    it generates the correct service file
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

    namespace = {}
    exec(code, namespace)

    assert namespace['Pydock'].BUILD == {'context': '.','args': {'app_name': 'pydock' }}
    assert namespace['Pydock'].IMAGE == None
    assert namespace['Pydock'].VOLUMES == ['.:/pydock']
    assert namespace['Pydock'].DEPENDS_ON == ['redis']

    assert namespace['Redis'].BUILD == None
    assert namespace['Redis'].IMAGE == 'redis:alpine'
    assert namespace['Redis'].VOLUMES == None
    assert namespace['Redis'].DEPENDS_ON == []


