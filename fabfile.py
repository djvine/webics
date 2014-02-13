from fabric.api import lcd, local

home = '/home/david'

def prepare_deployment():
    local('python manage.py test webics')
    local('git add -p && git commit')

def deploy():
    with lcd('{:s}/web/prod/webics'.format(home)):

        local('git pull {:s}/web/dev/webics/'.format(home))

        local('python manage.py migrate scans')
        local('python manage.py test scans')
        local('sudo service apache2 restart')