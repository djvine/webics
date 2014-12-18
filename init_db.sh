rm -Rf scans/migrations
./manage.py syncdb
./manage.py makemigrations scans
./manage.py migrate
