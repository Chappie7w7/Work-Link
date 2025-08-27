# Work-Link
Proyecto final de tarea integradora

## Instalar proyecto

Clonar el repositorio

```sh
git clone "https://github.com/Chappie7w7/Work-Link.git"
```

Entrar a la carpeta

```sh
cd Work-Link
```

Crear el entorno virtual de python

```sh
python -m venv .venv
```

Instalar los requerimientos

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuración de las variables de entorno

A continuación un breve descripción para cada variable de entorno

**Variable para la configuración de flask**

- `FLASK_APP`: archivo de entrada de la aplicación para flask
- `FLASK_ENV`: modo de ejecución de la aplicación, esta variable acepta dos valores las cuales son **production**, **development**
- `FLASK_DEBUG`: se configura si el proyecto se ejecutara en modo debug o no, solo acepta dos valors 0 y 1

**Llaves secretas**

- `SECRET_KEY`: Llave secreta para la aplicación
- `JWT_SECRET_KEY`: Llave secreta para las rutas protegidas con JWT

**Configuración para la bd sql**

- `SQLALCHEMY_DATABASE_URI`: Url de conexión para la base de datos, en este proyecto la url debe tener la siguiente manera `mysql+pymysql://user:password@host:port/database`
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Boleando para activar o desactivar las notificaciones de SQLALCHEMY

## Ejecutar el proyecto

```sh
#Para activar el entorno virtual
.\.venv\Scripts\activate 
# o
source .venv/Scripts/Activate

#Para ejecutar el proyecto
flask --app main.py run -h '0.0.0.0'
# o
flask run --debug -h '0.0.0.0'
```

## Estructura del proyecto

- Carpeta `app`: Todo el código de la aplicación se encuentra aquí.

- Carpeta `apis`: Aquí se crearán todas las APIs necesarias para el funcionamiento de la aplicación.

- Carpeta `routes`: En esta carpeta se crearán todas las rutas web que utilizará el cliente desde un navegador.

- Carpeta `db`: En esta carpeta se encontrará la conexión a la base de datos

- Carpeta `controller`: En esta carpeta contendrá todos los archivos por cada modulo que controlara las acciones con la base de datos

- Carpeta `models`: Modelos de las tablas para la base de datos

- Carpeta `static`: archivos disponibles como recursos para las pagina web

- Carpeta `templates`: Contendrá los archivos jinja2 para las paginas web

- Carpeta `Utils`: Utilidades para la pagina web, las cuales son los decoradores las rutas protegidas

## Migraciones para la BD SQL

Cuando se inicie el proyecto por primera ves la bd se creara automáticamente, pero si surge una modificación no se puede actualizar, para eso se usa los siguientes comandos

Si aun no existe la carpeta migrations ejecutar el siguiente comando

```sh
flask db init
```

Si se aplico cambio en los modelos se ejecuta el siguiente comando para actualizar

```sh
flask db migrate -m "Mensaje del cambio aplicado"
```

Para aplicar los cambios y subirlos a la base de datos, ejecutar los siguiente comando

```sh
flask db upgrade
```

Todos los comandos deben de tener un resultado exitoso y ver los cambios en la bd