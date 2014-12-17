rm -Rf scans/migrations
./manage.py makemigrations scans
./manage.py migrate
./manage.py syncdb
