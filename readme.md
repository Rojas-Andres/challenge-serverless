## Anotaciones
1. Roles
    - Super admin (encargado de crear, eliminar , actualizar usuarios admin)
        - Lo pense principalmente para que los administradores no se puedan eliminar entre si y que solo lo haga un super admin.
    - Admin (encargado de crear o actualizar productos)
        - El admin solo puede eliminar o actualizar productos, no va a tener permisos ni de editarse a si mismo , ni de eliminarse y mucho menos de eliminar otros usuarios
    - Usuario (Usuario de la plataforma)
        - El usuario por ahora solo podra ver los productos
    - Usuario anonimo ( usuario que no esta registrado en la plataforma)

## Run project local without Docker
virtualenv venv
pip install -r local.txt
python main.py
# RUN migrations alembic

alembic revision --autogenerate -m "generate new models"
alembic upgrade heads
# RUN Docker-compose local

docker-compose -f docker-compose.testing.yml build
docker-compose -f docker-compose.testing.yml up --force-recreate --build

## preconfigure.Dockerfile

- Este dockerfile se creo con el fin de que quede preconfigurado todas las librerias y todo lo necesario para el proyecto , por otra parte si se desea actualizar alguna libreria o crear añadir una nueva en su defecto , tocaria actualizar el ECR y ya.

Para ello se debe de configurar el profile de symptomps
aws ecr-public get-login-password --region us-east-1 --profile wts | docker login --username AWS --password-stdin public.ecr.aws

`docker build -t nombre_imagen .`
`docker build -t fastapi_image -f preconfigure.Dockerfile .`
`docker tag fastapi_image:latest public.ecr.aws/m7j0n8s6/testing`
`docker push public.ecr.aws/m7j0n8s6/testing`

## Documentacion para generar los roles y credenciales para configurar el cicd
https://aws.amazon.com/es/blogs/compute/introducing-aws-sam-pipelines-automatically-generate-deployment-pipelines-for-serverless-applications/