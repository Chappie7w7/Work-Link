import time
from selenium.webdriver.common.by import By


def ir_a_login(driver, base_url):
    driver.get(f"{base_url}/login")
    time.sleep(1)


def test_login_superadmin_exitoso(driver, base_url):
    ir_a_login(driver, base_url)

    # Seleccionar tipo de usuario
    tipo_select = driver.find_element(By.NAME, "tipo_usuario")
    # Selenium no tiene un wrapper Select aquí, usamos click+option
    tipo_select.click()
    # Seleccionar opción "Administrador" (value="superadmin")
    option_superadmin = driver.find_element(
        By.CSS_SELECTOR, "select[name='tipo_usuario'] option[value='superadmin']"
    )
    option_superadmin.click()

    # Correo y contraseña correctos
    email_input = driver.find_element(By.NAME, "correo")
    password_input = driver.find_element(By.NAME, "password")

    email_input.clear()
    email_input.send_keys("worklinkOco@gmail.com")
    password_input.clear()
    password_input.send_keys("admin123")

    # Enviar formulario (input type="submit")
    submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_btn.click()

    # Esperar redirección
    time.sleep(2)

    # Después de login superadmin debe ir a /admin/dashboard
    assert "/admin/dashboard" in driver.current_url


def test_login_credenciales_incorrectas(driver, base_url):
    ir_a_login(driver, base_url)

    tipo_select = driver.find_element(By.NAME, "tipo_usuario")
    tipo_select.click()
    option_superadmin = driver.find_element(
        By.CSS_SELECTOR, "select[name='tipo_usuario'] option[value='superadmin']"
    )
    option_superadmin.click()

    email_input = driver.find_element(By.NAME, "correo")
    password_input = driver.find_element(By.NAME, "password")

    email_input.clear()
    email_input.send_keys("correo_invalido@example.com")
    password_input.clear()
    password_input.send_keys("clave_incorrecta")

    submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_btn.click()

    time.sleep(2)

    # Debe seguir en /login (o regresar ahí) y mostrar mensaje de error
    assert "/login" in driver.current_url

    # Verificar que haya algún mensaje con estilo de error (rojo)
    mensajes = driver.find_elements(By.CSS_SELECTOR, ".mensajes p")
    assert any("error" in (m.get_attribute("style") or "").lower() or m.text for m in mensajes)