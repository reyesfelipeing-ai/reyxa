import urllib.request

try:
    urllib.request.urlopen("https://www.google.com", timeout=5)
    print("¡Google responde perfectamente! El problema es específico del dominio de Supabase.")
except Exception as e:
    print("Google también falló. El Firewall de Windows está bloqueando a Python:", e)