from __future__ import with_statement
from fabric.api import lcd, local, env

home = '/home/david'
prod = 'webics'
dev = home+'/web/dev/webics'

env.hosts = ['webics@joule']

def prepare_deployment():
	with lcd(dev):
	    local('python manage.py collectstatic')
    	    local('git add -p && git commit -am "Prepare for deployment to apache server"')
    	    local('git push github master')

def deploy():
    prepare_deployment()
    with cd(prod):
        run('git pull origin master')
        run('service apache2 restart')
