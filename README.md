# Work-Link

Proyecto final de Tarea Integradora

---

## 🚀 Instalación del proyecto

### 1️⃣ Clonar el repositorio

```bash
git clone "https://github.com/Chappie7w7/Work-Link.git"
cd Work-Link
```

### 2️⃣ Crear entorno virtual

```bash
python -m venv .venv
```

### 3️⃣ Activar entorno virtual

```bash
# En Windows
.\.venv\Scripts\activate
# En Linux/Mac
source .venv/bin/activate
```

### 4️⃣ Actualizar pip e instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuración de variables de entorno

### 🔹 Configuración de Flask

* `FLASK_APP`: archivo principal de la aplicación.
* `FLASK_ENV`: entorno de ejecución (**production** o **development**).
* `FLASK_DEBUG`: activa el modo debug (0 o 1).

### 🔹 Llaves secretas

* `SECRET_KEY`: llave secreta de Flask.
* `JWT_SECRET_KEY`: llave para rutas protegidas por JWT.

### 🔹 Base de datos SQL

* `SQLALCHEMY_DATABASE_URI`: conexión, por ejemplo
  `mysql+pymysql://usuario:contraseña@host:puerto/base_datos`
* `SQLALCHEMY_TRACK_MODIFICATIONS`: booleano (True o False).

---

## ▶️ Ejecutar el proyecto

### Ejecución estándar (HTTP)

```bash
flask --app main.py run -h '0.0.0.0'
# o
flask run --debug -h '0.0.0.0'
```

### Ejecución directa (para usar debug=True)

```bash
python main.py
```

---

## 🗂️ Estructura del proyecto

* **app/** → código principal de la aplicación.
* **routes/** → rutas web del cliente.
* **db/** → conexión a la base de datos.
* **controller/** → controladores por módulo.
* **models/** → modelos SQLAlchemy.
* **static/** → archivos estáticos (CSS, JS, imágenes).
* **templates/** → plantillas Jinja2.
* **utils/** → utilidades (decoradores, seguridad, helpers).

---

## 🧩 Migraciones de base de datos

### Inicializar migraciones

```bash
flask db init
```

### Detectar cambios en modelos

```bash
flask db migrate -m "Descripción del cambio"
```

### Aplicar cambios a la BD

```bash
flask db upgrade
```

---

## 🔒 HTTPS local (opcional para desarrollo)

Si deseas ejecutar Flask con **HTTPS local**, sigue estos pasos:

1. Genera un certificado autofirmado:

   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

   Esto creará dos archivos:

   * `cert.pem`
   * `key.pem`

2. Modifica `main.py`:

   ```python
   from app import create_app
   app = create_app()

   if __name__ == '__main__':
       app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
   ```

3. Ejecuta con:

   ```bash
   python main.py
   ```

La app estará disponible en:
👉 [https://127.0.0.1:5000/](https://127.0.0.1:5000/)

---

📘 **Nota:**
El certificado es **temporal y solo para desarrollo**.
En producción se usará un certificado real (por ejemplo, con **NGINX + Let’s Encrypt**).
