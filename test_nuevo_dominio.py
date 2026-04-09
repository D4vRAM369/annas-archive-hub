# test_nuevo_dominio.py
# Añade un dominio falso para probar que el sistema lo detecta

import json

# Leer domains.json actual
with open("domains.json", "r") as f:
    datos = json.load(f)

# Añadir un dominio de prueba
datos["active_auto"].append("https://annas-archive.prueba/")

# Guardar
with open("domains.json", "w") as f:
    json.dump(datos, f, indent=2)

print("✅ Dominio de prueba añadido")
