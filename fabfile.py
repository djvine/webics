from __future__ import with_statement
from fabric.api import cd, run, lcd, local, env, hosts

prod = 'webics'
dev = '/home/david/web/dev/webics'
backend_webics = '/local/webics'
backend_python = '/local/webics/scans/backend/python'
backend_redis = '/local/webics/scans/backend/redis'
backend_nodejs = '/local/webics/scans/backend/nodejs'

#env.hosts = ['webics@joule', 'dvine@lemon']

@hosts('webics@joule')
def prepare_deployment():
	with lcd(dev):
	    local('python manage.py collectstatic --noinput')
    	    local('git commit -am "Prepare for deployment to apache server"')
    	    local('git push github master')

@hosts('webics@joule')
def deploy():
    with cd(prod):
        run('git pull origin master')
        run('service apache2 restart')

@hosts('dvine@lemon')
def backend():
    with cd(backend_webics):
        run('git pull origin master')
        run('/bin/bash -l -c "workon webics && python ./scans/backend/python/scan_engine.py"')
