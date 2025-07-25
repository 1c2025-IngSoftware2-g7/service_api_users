from werkzeug.security import generate_password_hash
import sys

from src.infrastructure.config.db_config import DatabaseConfig
import psycopg
import uuid
import getpass

def create_admin():
    print("=== Creación del Primer Administrador ===")

    # Obtener datos por consola
    print("\nPor favor ingrese los datos del administrador:")
    name = input("Nombre: ").strip()
    surname = input("Apellido: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Contraseña: ").strip()
    confirm_password = getpass.getpass("Confirmar Contraseña: ").strip()

    if password != confirm_password:
        print("\nError: Las contraseñas no coinciden", file=sys.stderr)
        sys.exit(1)

    # Validación básica
    if not all([name, surname, email, password]):
        print("\nError: Todos los campos son obligatorios", file=sys.stderr)
        sys.exit(1)

    # Base de datos
    try:
        conn_str = DatabaseConfig().connection_strings
        conn = psycopg.connect(conn_str)
        cursor = conn.cursor()

        # Verificar si ya existe un admin
        cursor.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1")
        if cursor.fetchone():
            print("\nError: Ya existe un administrador en el sistema", file=sys.stderr)
            sys.exit(1)

        password_hashed = generate_password_hash(password)

        # Insertar
        admin_data = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "surname": surname,
            "password": password_hashed,
            "email": email,
            "status": "active",
            "role": "admin"
        }

        cursor.execute(
            """
            INSERT INTO users (uuid, name, surname, password, email, status, role)
            VALUES (%(uuid)s, %(name)s, %(surname)s, %(password)s, %(email)s, %(status)s, %(role)s)
            """,
            admin_data
        )
        conn.commit()

        print(f"\nÉxito: Administrador {email} creado correctamente")

    except psycopg.Error as e:
        print(f"\nError de base de datos: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    create_admin()
