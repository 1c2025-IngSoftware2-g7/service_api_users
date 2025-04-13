# ClassConnect - API Users

## Contenidos
1. Introducción
2. Pre-requisitos
3. CI-CD
4. Tests
5. Comandos para construir la imagen de Docker
6. Comandos para correr la base de datos
7. Comandos para correr la imagen del servicio

## 1. Introducción

Microservicio para la gestión de Usuarios en ClassConnect.
Permite:
    - Creación de usuarios nuevos.
    - Login de usuarios a través de email y contraseña.
    - Login de administradores de la plataforma.
    - Registro de usuarios (creación) a través de Google.
    - Login a través de Google.
    - Integración entre una cuenta creada de forma tradicional y el ingreso a través de Google.
    - Sesiones con tiempo de expiración.

## 2. Pre-requisitos
- Necesario para levantar el entorno de desarrollo de forma local:
    - [Docker](https://docs.docker.com/get-started/introduction/) (version 27.3.1) 
    - [Docker-compose](https://docs.docker.com/compose/install/) (version 2.30.3)

- Puertos utilizados: 
    - 5432: Utilizado por la base de datos PostgreSQL.
    - 8080: Utilizado por la API.

Adicionalmente, se menciona a continuación lo utilizado dentro de los contenedores:

- Lenguaje:
    - Python 3.13 (Utilizado en la imagen del Dockerfile).

- Base de datos:
    - PostgreSQL 15 (imagen oficial).

- Gestión de paquetes:
    - pip (se usa dentro del contenedor para instalar dependencias).


## 3. CI-CD

Se realizó un [repositorio template de los workflows](https://github.com/1c2025-IngSoftware2-g7/ci_templates/tree/main) de test y deploy en Render, el cual se reutiliza en todos los repos del backend realizados en python.
Se corre, en los tests:
    - Set up Python
    - Install dependencies
    - Lint with flake8
    - Run tests in Docker
    - Upload to Codecov

En el deploy: 
    - Checkout code (clone del repositorio).
    - Set up Python
    - Install dependencies
    - Trigger deploy in Render

### Test coverage

[![codecov](https://codecov.io/gh/1c2025-IngSoftware2-g7/service_api_users/branch/<RAMA>/graph/badge.svg)](https://codecov.io/gh/1c2025-IngSoftware2-g7/service_api_users)


## 4. Tests
Para la implementación de los test de integración, se utilizó la librería [pytest](https://www.psycopg.org/psycopg3/docs/basic/index.html).  
Estos se encuentran desarrollados en ```./tests/api_test.py```.  


## 5. Comandos para construir la imagen de Docker
Al utilizar docker-compose, se puede construir todas las imágenes definidas en docker-compose.yml con el siguiente comando:
```bash
docker compose build
```

## 6. Comandos para correr la base de datos
Como ya se mencionó, se utilizó docker compose para correr el servicio de forma local. Por lo que para levantar todas las imágenes del proyecto, se debe correr:
```bash
docker compose up
```

En ```docker-compose.yml```:
- db local: Base de datos PostgreSQL. Se define la imagen oficial, los parámetros para la conexión, el puerto en el que escuchará (5432) y se carga el script que se debe correr para inicializar la base de datos, un tipo de usuario, sus permisos y se crea la tabla de cursos. Además, se define la red a la que va a pertenecer.  

> Para construir el docker de la base de datos y el script para levantar la base de datos y crear la tabla (cuando se corre por primera vez el proyecto), se utilizó [esta documentación](https://hub.docker.com/_/postgres).  
Se puede observar el script que se corre luego de levantarse la base de datos en: ```./initialize_users_db.sql```. Este fue incluido en el directorio ```/docker-entrypoint-initdb.d/``` dentro del contenedor, por lo que PostgreSQL lo ejecuta automáticamente cuando el contenedor se levanta por primera vez.

> En Render se corrieron los comandos sobre la base de datos, directamente sobre la base levantada en Render.

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

Se solicitará los datos del administrador y se creará el primer perfil con autorizaciones de "admin". Luego ya no se podrá volver a crear un administrador de esta forma. También se puede verificar que se creó el registro correctamente con:
```bash
docker compose exec db psql -U user_db -d classconnect_users -c "SELECT * FROM users WHERE role='admin';"
```

# 9. Despliegue en la Nube 

Se encuentra desplegada en Render. 
Se puede ingresar a través del siguiente link: https://service-api-users.onrender.com/users

Se levantó el servicio que escucha las request sobre la API de Usuarios. Para esto se construye la imagen en Render a partir del Dockerfile y se corre con el comando descrito en este archivo.
Además, se deployó de forma separada la base de datos en PostgreSQL. Con la cual se comunica el backend de Usuarios a través de los datos de conexión de esta base indicados en el Environments de nuestro servicio.

