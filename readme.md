## Run project local without Docker
virtualenv venv
pip install -r local.txt
python main.py

# RUN Docker-compose local

docker-compose -f docker-compose.testing.yml build


## preconfigure.Dockerfile

- Este dockerfile se creo con el fin de que quede preconfigurado todas las librerias y todo lo necesario para el proyecto , por otra parte si se desea actualizar alguna libreria o crear añadir una nueva en su defecto , tocaria actualizar el ECR y ya.

Para ello se debe de configurar el profile de symptomps
aws ecr-public get-login-password --region us-east-1 --profile wts | docker login --username AWS --password-stdin public.ecr.aws

`docker build -t nombre_imagen .`
`docker build -t fastapi_image -f preconfigure.Dockerfile .`
`docker tag fastapi_image:latest public.ecr.aws/m7j0n8s6/testing`
`docker push public.ecr.aws/m7j0n8s6/testing`

