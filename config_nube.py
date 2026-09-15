import os
from supabase import create_client, Client

# Tus credenciales maestras de Supabase
SUPABASE_URL = "https://runoqujcdjywxasfhdkl.supabase.co"
SUPABASE_KEY = "sb_publishable_hWnWSVgB__vI56X0X4-UwA_KNOhBEMT"

# Inicializar el cliente de la nube
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)