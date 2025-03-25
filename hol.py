import os

ruta_archivo = r"C:\Users\LENOVO\Desktop\UNT\qda\reniec.txt"


if os.path.exists(ruta_archivo):
    print("✅ El archivo existe.")
else:
    print("❌ El archivo NO existe. Verifica la ruta.")
