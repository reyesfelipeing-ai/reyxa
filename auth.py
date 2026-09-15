from config_nube import supabase

def iniciar_sesion(email, password):
    email_clean = email.strip().lower()
    
    # 1. Consulta directa a Supabase (Fuente de verdad)
    try:
        res = supabase.table("usuarios").select("*").eq("email", email_clean).execute()
        if res.data and len(res.data) > 0:
            usr = res.data[0]
            pass_db = usr.get("password_hash") or usr.get("password")
            
            if pass_db == password:
                tipo_cli = usr.get("tipo_cliente") or "PRIVADO_B2B"
                return {
                    "id": usr.get("id"),
                    "email": usr.get("email"),
                    "nombre_completo": usr.get("nombre_completo", "Usuario REYXA"),
                    "rol": usr.get("rol", "OPERADOR"),
                    "tipo_cliente": tipo_cli,
                    "finca_id": usr.get("finca_id", "FINCA_DEFAULT"),
                    "nombre_organizacion": (
                        "Reservorio Comunitario - Facatativá" 
                        if tipo_cli == "GOBERNACION_B2G" 
                        else "Finca Comercial San José"
                    )
                }
    except Exception as e:
        print(f"Error consultando Supabase: {e}")
        
    # 2. Respaldos locales para desarrollo (Fallback maestro)
    if email_clean == "admin@reyxacol.com" and password == "reyxa2026":
        return {
            "id": 1,
            "email": "admin@reyxacol.com",
            "nombre_completo": "Wilmar Reyes",
            "rol": "ADMINISTRADOR",
            "tipo_cliente": "PRIVADO_B2B",
            "finca_id": "1",
            "nombre_organizacion": "Finca Comercial San José"
        }
        
    if email_clean == "lider.vereda@jac.gov.co" and password == "reyxa2026":
        return {
            "id": 2,
            "email": "lider.vereda@jac.gov.co",
            "nombre_completo": "Carlos Mendoza (Líder Veredal)",
            "rol": "OPERADOR_COMUNITARIO",
            "tipo_cliente": "GOBERNACION_B2G",
            "finca_id": "RESERVORIO_FACATATIVA",
            "nombre_organizacion": "Reservorio Comunitario - Facatativá"
        }
    
    return None