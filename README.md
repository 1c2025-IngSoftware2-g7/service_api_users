# ClassConnect - API Users

## Contenidos
1. Introducción
2. 
3. Pre-requisitos
4. Tests
5. Comandos para construir la imagen de Docker
6. Comandos para correr la base de datos
7. Comandos para correr la imagen del servicio

## 1. Introducción

## 2. CI

### Test coverage

[![codecov](https://codecov.io/gh/1c2025-IngSoftware2-g7/service_api_users/branch/<RAMA>/graph/badge.svg)](https://codecov.io/gh/1c2025-IngSoftware2-g7/service_api_users)

## 3. Pre-requisitos
- Necesario para levantar el entorno de desarrollo:
    - [Docker](https://docs.docker.com/get-started/introduction/) (version 27.3.1) 
    - [Docker-compose](https://docs.docker.com/compose/install/) (version 2.30.3)

- Puertos utilizados: 
    - 5432: Utilizado por la base de datos PostgreSQL.
    - 8080: Utilizado por la API.

Adicionalmente, menciono a continuación lo utilizado dentro de los contenedores:

- Lenguaje:
    - Python 3.13 (Utilizado en la imagen del Dockerfile).

- Base de datos:
    - PostgreSQL 15 (imagen oficial).

- Gestión de paquetes:
    - pip (se usa dentro del contenedor para instalar dependencias).

## 4. Tests
Para la implementación de los test de integración, se utilizó la librería [pytest](https://www.psycopg.org/psycopg3/docs/basic/index.html).  
Estos se encuentran desarrollados en ```./src/test/api_test.py```.  


## 5. Comandos para construir la imagen de Docker
Al utilizar docker-compose, se puede construir todas las imágenes definidas en docker-compose.yml con el siguiente comando:
```bash
docker compose build
```

## 6. Comandos para correr la base de datos
Como ya se mencionó, se utilizó docker compose. Por lo que para levantar todas las imágenes del proyecto, se debe correr:
```bash
docker compose up
```

En ```docker-compose.yml```:
- db: Base de datos PostgreSQL. Se define la imagen oficial, los parámetros para la conexión, el puerto en el que escuchará (5432) y se carga el script que se debe correr para inicializar la base de datos, un tipo de usuario, sus permisos y se crea la tabla de cursos. Además, se define la red a la que va a pertenecer.  

> Para construir el docker de la base de datos y el script para levantar la base de datos y crear la tabla (cuando se corre por primera vez el proyecto), se utilizó [esta documentación](https://hub.docker.com/_/postgres).  
Se puede observar el script que se corre luego de levantarse la base de datos en: ```./initialize_users_db.sql```. Este fue incluido en el directorio ```/docker-entrypoint-initdb.d/``` dentro del contenedor, por lo que PostgreSQL lo ejecuta automáticamente cuando el contenedor se levanta por primera vez.

## 7. Comandos para correr la imagen del servicio
De igual forma que en el inciso anterior:
```bash
docker compose up
```

En ```docker-compose.yml```:
- app: API RESTful en Flask. Se utiliza como imagen la definida en Dockerfile. Se indica el puerto 8080 para comunicarse con este servicio y se incluye en la misma red que la base de datos, de esta forma se pueden comunicar. Además, se define que este servicio se va a correr cuando se termine de levantar la base de datos. Por último, se indica el comando que se va a correr.

## 8. Comandos para crear el primer administrador
Con el servicio levantado se debe correr desde root:
```bash
docker compose exec app python /create_first_admin.py
```

Se solicitara los datos del administrador y se creara el primer perfil con autorizaciones de "admin". Luego ya no se podrá volver a crear un administrador de esta forma. También se puede verificar que se creo el registro correctamente con:
```bash
docker compose exec db psql -U user_db -d classconnect_users -c "SELECT * FROM users WHERE role='admin';"
```
