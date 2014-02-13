from fabric.api import lcd, local

home = '/home/david'
prod = '/usr/local/www/webics.com'
dev = home+'/web/dev/webics'

def prepare_deployment():
	with lcd(dev):
		local('python manage.py collectstatic')
    	local('git add -p && git commit -a -m "Prepare for deployment to apache server"')

def deploy():
    with lcd(prod):

        local('git pull {:s}/web/dev/webics/'.format(home))
        local('sudo service apache2 restart')