# Skip

Django REST API to Hop Alerts Database

## Topic Mapping

Skip assumes the following Hopskotch topic mapping:

- `gcn-circular`: All GCN Circulars
- `lvc.lvc-counterpart`: GCN/LVC Counterpart Notices
- `gcn`: All GCN Notices

## Local Development Quickstart

##### Using Django `runserver` (development only):
First, you'll need a PostGIS server listening at port 5432:

```bash
docker create --name skip-gis -e POSTGRES_DB=skip -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 mdillon/postgis
docker start skip-gis
```

Create a `local_settings.py` in the top level of your `skip` directory and add the following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'skip',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Set up the database tables:

```bash
 ./manage.py migrate
 ./manage.py createsuperuser
```

Choose a port (here we've choosen 8989) and run the server
```
./manage.py runserver 8989 &
```
`skip` is at http://localhost:8989


##### Using docker-compose

```
docker-compose build
docker-compose up &
```

Next, create a superuser:

```
docker exec -it skip /bin/bash
python manage.py createsuperuser
# Follow prompts to create user
```

Navigate to `localhost:8080` to view the API.

#### Populating with data

There are two ways to populate data.

##### Listening to the streams

There is a management command that can be run manually to ingest data by running `./manage.py ingestmessages`. In order to run this, you will need to properly configure your `HOPSKOTCH_CONSUMER_CONFIGURATION` in `settings.py`. Credentials can be generated at https://admin.dev.hop.scimma.org. In order to immediately ingest messages, set `'auto.offset.reset': 'latest'`, which will begin ingesting at the beginning of all available messages.

##### Getting Superevent data

In order to populate your database with Event data, you can run the following commands, one after another:

```python
./manage.py scrapegcncirculars
./manage.py scrapelvccounterparts
./manage.py scrapelvcnotices
./manage.py publishsupereventalerts
./manage.py ingestmessages
```

Each of the `scrape` management commands will pull alerts from the various sources for a Superevent and save them in your local database. The `publish` command will push those alerts to `hop` for ingestion.

###### Troubleshooting

If you're coming across connection errors, make sure you aren't inadvertently using bad values from your `local_settings.py`, and 
confirm that there are no conflicting docker containers exposing 5432 or 8080.

## AWS Deployment

### Updating terraform state

The deployment infrastructure is maintained via terraform in the [aws-dev repository](https://github.com/scimma/aws-dev/). The database is maintained in the [aws-dev/tf/skip-db/](https://github.com/scimma/aws-dev/tree/master/tf/skip-db) folder, the EC2 infrastructure is maintained in the [aws-dev/tf/skip/](https://github.com/scimma/aws-dev/tree/master/tf/skip) folder, and the Kubernetes infrastructure is maintained in the [aws-dev/tf/skip-eks/](https://github.com/scimma/aws-dev/tree/feature/skip-eks/tf/skip-eks) folder in the `feature/skip-eks` branch (Note: as of 8/23/21, this branch is two months out of date with `master`).

In order to make terraform changes, your system must be configured with the correct version of terraform, which is documented in the [top-level README](https://github.com/scimma/aws-dev#build-tools). The repository is well-documented, so this README will only document the few commands that are required to modify the terraform configuration, which are:

```bash
# From the top-level of aws-dev
cd tf/skip
make init
make plan
make apply
```

Please consult with the AWS lead on whether the `make` commands are still valid at the time of use, as this has been in some dispute.

### EC2 Deployment

Skip is currently deployed via `docker-compose` on an EC2 instance. The `terraform` can be found in [this repo](https://github.com/scimma/aws-dev/tree/master/tf). The database can be found in `skip-db`, and the web service in `skip`.

To deploy on the EC2 instance, you'll need AWS credentials from the SCIMMA security team. Ensure that your credentials are configured properly either via `aws configure` or by setting `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

Navigate to the AWS console by logging into Comanage at https://registry.scimma.org, and click on the "AWS Console" in the "Available Services" section. Then navigate to the EC2 service, and click on the "Instances" tab.

Click on the instance "hopDevel Skip in Region a", which should be running. Once selected, a button will appear at the top of the screen marked "Connect". Upon clicking that, a modal will provide the command to connect: `ssh -i "path/to/skip-web-deploy-2.pem" ec2-user@address.region.compute.amazonaws.com`.

Once you have accessed the EC2 instance via SSH, there are two potential paths to deployment. If the EC2 instance is newly created:

```bash
sudo yum install git
git clone https://github.com/scimma/skip.git
cd skip
# If migrations are needed, please see the note in the Troubleshooting section of this document
$(aws ecr get-login --no-include-email --region us-west-2)
docker-compose pull
docker-compose up &
```

If the EC2 instance has been deployed to previously:

```bash
cd skip
git fetch && git pull origin main  # This is necessary to ensure the docker compose file is up to date
docker-compose pull
docker-compose up &
```

If the EC2 instance has had multiple deployments, the disk space may be too low to pull down the latest docker image. In this case, you'll need to delete old docker images with a combination of `docker images` and `docker image rm <image tag>`.

#### A note about the private key

The private key is required for SSH access to the EC2 instance, must be created in the AWS console rather than in terraform, and is only accessible when created. A new private key also requires an update to the terraform configuration, as the key name is referred to [here](https://github.com/scimma/aws-dev/blob/0dbf906e398679cd925328381df112bdaadb3be1/tf/skip/skip.tf#L37).

To create a new key, navigate to the EC2 service in the AWS console as described above. Then, click on the "Key Pairs" link under the "Network & Security" section, followed by the "Create key pair" button.

### Kubernetes Deployment

Skip is not currently successfully deployed via Kubernetes, but is well on its way. The terraform configuration can be found in the `feature/skip-eks` [branch](https://github.com/scimma/aws-dev/tree/feature/skip-eks) in `aws-dev`, and the kubernetes dev deployment file can be found in this repository.

The deployment file requires a number of secrets that are configured via the terraform configuration. The secrets are database values that are provisioned in the `tf/skip-db/skip-db.tf` file, and loaded as environment variables in the kubernetes `deployment-dev.yaml` file.

Access to the SCIMMA kubernetes cluster is documented [here](https://github.com/scimma/aws-dev/blob/feature/skip-eks/doc/00README_FIRST.md)--however, this differs from the process that has been used by Skip developers previously. The method previously followed is significantly closer to the [AWS documentation](https://aws.amazon.com/premiumsupport/knowledge-center/amazon-eks-cluster-access/).

Access will require modification of the user's `~/.kube/config` file, and the writer of the document does not recall how to get the correct values for that. Any user intending to get access should contact the SCIMMA security team via Slack. Once the `config` file is up-to-date, the process is as follows:

```bash
export AWS_ACCESS_KEY_ID=<scimma_access_key> && export AWS_SECRET_ACCESS_KEY=<scimma_secret_key>
aws sts assume-role --role-arn arn:aws:iam::585193511743:role/scimma_power_user --role-session-name <your-session-name> --duration-seconds 43200  # This command will return values for AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN
export AWS_ACCESS_KEY_ID=<role_access_key> && export AWS_SECRET_ACCESS_KEY=<role_secret_key> && export AWS_SESSION_TOKEN=<role_session_token>
kubectx arn:aws:eks:us-west-2:585193511743:cluster/hopDevelEksCluster
kubectl get pods
kubectl apply -f ~/projects/skip/deployment-dev.yaml
```
