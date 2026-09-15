from config_nube import supabase

print("Conectando con Supabase...")

# Intentamos insertar una finca de prueba para verificar permisos y conexión
try:
    data, count = supabase.table("fincas").insert({
        "id": "finca_prueba_01",
        "nombre_finca": "Finca Las Margaritas",
        "ubicacion": "Facatativá, Cundinamarca"
    }).execute()
    
    print("¡Finca insertada con éxito en la nube! Datos:", data)
except Exception as e:
    print("Nota sobre la inserción (puede que ya exista):", e)

# Intentamos leer las fincas registradas
response = supabase.table("fincas").select("*").execute()
print("\n--- Fincas actualmente en la nube ---")
print(response.data)