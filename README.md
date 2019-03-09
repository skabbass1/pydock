Pydock is a utility built on top of docker-compose to enable docker based development from the get go. It enables one to do app development and testing from within a docker container from the very beginning of the app development cycle.

# Usage
From within the application directory, run `pydock init` to setup a basic docker based development environment. For example, if you are building an app called `my_app`  which depends on `redis`, `postgres` and requires the `pyredis`, `pyscoppg2` and `pytest` python packages, you can execute
```
pydock init -d  redis -d postgres  -r pyredis -r pyscoppg2 -r pytest
```
This will create the necessary setup files required to instantiate a python docker container with dependencies on redis and postgres.

Once the `init` command has been run - the next step is to run the `exec` command from within the application folder
```
pydock exec
```
The `exec` command pulls  down the necessary containers (in this case, a base python container, a redis container and a postgres container), sets up the necessary network connections between these containers,  installs the required pyhton packages in a python development container and gives you a command prompt within this container. Your application directory is also mounted onto this development container. From here on, you can use this terminal to run and test your code just as you would in a normal terminal

Note that if you need to develop with specific versions of python, redis or postgres, you can specify these versions as part of the `init` command above
```
pydock init -d  redis:5.0.3  -d postgres:latest  -r pyredis -r pyscoppg2 -r pytest --base-pyhton-image python:3.6
```
Since `pydock` pulls containers from docker hub, the version specifiers should match the available image `tags` on [DockerHub](https://hub.docker.com/)

Finally, `pydock` also  provides a `build` command which builds an application container with a given tag. You might use this command once you are finished developing and are ready to ship your application container


# TODO
* More robust image cleanup handling
* Provide a `push` command to to publish a built container to a remote repository
* Ability to handle languages other than python
