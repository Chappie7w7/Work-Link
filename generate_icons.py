from PIL import Image
import os

# Ruta del icono original
icon_path = 'app/static/icons/app.png'
output_dir = 'app/static/icons'

# Tamaños necesarios para PWA
sizes = [72, 96, 128, 144, 152, 192, 256, 384, 512]

try:
    # Abrir imagen original
    img = Image.open(icon_path)
    print(f"Imagen original: {img.size[0]}x{img.size[1]}")
    
    # Generar iconos en diferentes tamaños
    for size in sizes:
        # Redimensionar manteniendo la calidad
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Guardar con el nombre del tamaño
        output_path = os.path.join(output_dir, f'icon-{size}x{size}.png')
        resized.save(output_path, 'PNG', optimize=True)
        print(f"✓ Generado: icon-{size}x{size}.png")
    
    print("\n✅ Todos los iconos generados exitosamente!")
    
except Exception as e:
    print(f"❌ Error: {e}")
