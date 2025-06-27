# ClassConnect - API Users

## Contenidos
1. Introducción
2. Arquitectura de componentes, Pre-requisitos, CI-CD, Test, Comandos, Despliegue en la nube
3. Test coverage
4. Base de datos
5. Funcionalidades

## 1. Introducción

Microservicio para la gestión de Usuarios en ClassConnect.
Se utilizó por una [arquitectura en capas](https://dzone.com/articles/layered-architecture-is-good).

El servicio permite:

- Creación de usuarios nuevos y validación por PIN.
- Login de usuarios a través de email y contraseña.
- Login de administradores de la plataforma.
- Registro de usuarios (creación) a través de Google.
- Login a través de Google.
- Integración entre una cuenta creada de forma tradicional y el ingreso a través de Google.
- Recupero de contraseña.

# 2. Arquitectura de componentes, Pre-requisitos, CI-CD, Test, Comandos, Despliegue en la nube

[Explicados en API Gateway](https://github.com/1c2025-IngSoftware2-g7/api_gateway)

# 3. Test coverage

[Coverage User Service (codecov)](https://codecov.io/gh/1c2025-IngSoftware2-g7/service_api_users)

# 4. Base de datos

## PostgreSQL

La base de datos está diseñada para almacenar, consultar y mantener la información crítica relacionada con los usuarios del sistema, incluyendo credenciales, tokens, preferencias y roles.    

# 5. Funcionalidades

1. Registro de Usuarios

    Se almacenan los datos del nuevo usuario, incluyendo email, nombre, contraseña hasheada y metadatos asociados.

    Se genera un código PIN o token para validar el proceso de registro.

2. Login de Usuarios con Email y Contraseña

    Autenticación de credenciales mediante comparación del hash almacenado en base de datos.

3. Login con Proveedores de Identidad Federada (Google)

    Almacena y asocia los identificadores únicos externos al usuario en el sistema.

    Permite el login sin contraseña interna si la identidad federada es válida.

4. Registro y Login de Administradores

    La base diferencia tipos de usuario mediante roles (role).

    Los administradores tienen privilegios elevados y autenticación separada.

5. Recupero de Contraseña

    Se almacenan tokens temporales de recuperación y su expiración.

    Se registra el evento y se limita el número de intentos.

7. Notificación de PIN en Proceso de Registro

    El PIN generado es almacenado temporalmente en la base junto con el email o teléfono del usuario.

    Se utiliza para validar la identidad del usuario durante el registro vía email.
