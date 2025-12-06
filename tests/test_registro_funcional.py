import time
from selenium.webdriver.common.by import By


def ir_a_form_registro(driver, base_url):
    # La forma más realista: desde /login, hacer clic en "Registrarse -> Soy usuario"
    driver.get(f"{base_url}/login")
    time.sleep(1)

    # Abrir dropdown
    btn_registro = driver.find_element(By.ID, "sign-up")
    btn_registro.click()
    time.sleep(0.5)

    # Click en "Soy usuario" (href a LoginRoute.form_usuario => /form-registro-empleado)
    link_usuario = driver.find_element(By.ID, "usuario")
    link_usuario.click()

    time.sleep(2)
    # Ahora deberíamos estar en la página /form-registro-empleado que muestra registro.jinja2
    assert "/form-registro-empleado" in driver.current_url


def test_registro_usuario_exitoso(driver, base_url):
    ir_a_form_registro(driver, base_url)

    # Llenar formulario de registro
    nombre_input = driver.find_element(By.NAME, "nombre")
    correo_input = driver.find_element(By.NAME, "correo")
    password_input = driver.find_element(By.NAME, "password")
    confirmar_input = driver.find_element(By.NAME, "confirmar")
    privacy_check = driver.find_element(By.ID, "privacyCheck")

    nombre_input.clear()
    nombre_input.send_keys("Ángela")

    # Cambia el correo si ya existe en tu BD
    correo_input.clear()
    correo_input.send_keys("angela@gmail.com")

    password_input.clear()
    password_input.send_keys("qwerty123")

    confirmar_input.clear()
    confirmar_input.send_keys("qwerty123")

    # Aceptar aviso de privacidad
    if not privacy_check.is_selected():
        privacy_check.click()

    # Enviar formulario (input submit)
    submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_btn.click()

    time.sleep(2)

    # Tras registro redirige a LoginRoute.login_form (login.jinja2)
    assert "/login" in driver.current_url

    # Verificar mensaje de éxito
    mensajes = driver.find_elements(By.CSS_SELECTOR, ".mensajes p")
    textos = [m.text for m in mensajes]
    assert any("Cuenta creada con éxito" in t for t in textos)