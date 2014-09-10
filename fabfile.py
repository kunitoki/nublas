# -*- coding: utf-8 -*-

from fabric.api import env, task, cd, lcd, run, local, settings

from nublas import __version__

env.hosts = ['localhost']

#==============================================================================
@task
def execute_tests():
    with lcd("."):
        local("python manage.py test nublas")


#==============================================================================
@task
def demo_server():
    with lcd("example"):
        local("python manage.py runserver")


@task
def demo_shell():
    with lcd("example"):
        local("python manage.py shell")


#==============================================================================
@task
def update_docs():
    with lcd("docs"):
        local("make html")


#==============================================================================
@task
def pypi_register(where="pypitest"):
    with lcd("."):
        local("python setup.py register -r %s" % where)


@task
def pypi_upload(where="pypitest"):
    with lcd("."):
        local("python setup.py sdist upload -r %s" % where)


#==============================================================================
@task
def create_release(version=None):
    with lcd("."):
        version_todo = __version__

        # update version file if present
        if version is not None:
            version_todo = version
            local("sed -ie 's/[0-9]*\.[0-9]*/%s/' custard/__init__.py" % version_todo)
            local("git commit -a -m 'Bump release %s'" % version_todo)
            local("git push")

        # remove tag if present
        with settings(warn_only=True):
            local("git tag -d %s && git push origin :refs/tags/%s" % (version_todo, version_todo))

        # create tag
        local("git tag %s" % version_todo)
        local("git push --tags")

        # register with pypi and upload
        local("python setup.py register -r pypi")
        local("python setup.py sdist upload -r pypi")
