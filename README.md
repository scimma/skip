# Skip

Django REST API to Hop Alerts Database

## Local Development Quickstart

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


##### Using docker-compose

```
docker-compose build
docker-compose up
```

Next, create a superuser:

```
docker exec -it skip /bin/bash
python manage.py createsuperuser
# Follow prompts to create user
```

Navigate to `localhost:8080` to view the API.

###### Troubleshooting

If you're coming across connection errors, make sure you aren't inadvertently using bad values from your `local_settings.py`, and 
confirm that there are no conflicting docker containers exposing 5432 or 8080.

## AWS Deployment
For the time being, on the terraformed EC2 instance:
```bash
sudo yum install git
git clone https://github.com/scimma/skip.git || git pull origin master
cd skip
$(aws ecr get-login --no-include-email --region us-west-2)
docker-compose up &
```
