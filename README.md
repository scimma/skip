# hop-alert-api-app

Django REST api to Hop Alerts Database

### Quickstart

##### Using Django `runserver` (development only):
First, you'll need a PostGIS server listening at port 5432:
```bash
docker create --name skip-gis -e POSTGRES_DB=skip -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 mdillon/postgis
docker start skip-gis
```
Second, set up the database tables:
```bash
 ./manage.py migrate
```
Third, choose a port (here we've choosen 8989) and run the server
```
./manage.py runserver 8989 &
```
`skip` is at http://localhost:8989