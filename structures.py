from collections import namedtuple

ServiceDef = namedtuple(
        'ServiceDef',
        ['name', 'build', 'image', 'volumes', 'deps'],
        defaults=(None, None,  None, None, None)
        )
