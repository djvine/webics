from fabric.api import lcd, local

home = '/home/david'
prod = '/usr/local/www/webics.com'

def prepare_deployment():

    local('python manage.py collectstatic')
    local('git add -p && git commit -m "Prepared for deployment to apache server"')

def deploy():
    with lcd(prod):

        local('git pull {:s}/web/dev/webics/'.format(home))
        local('sudo service apache2 restart')