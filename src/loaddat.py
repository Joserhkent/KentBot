import os
from datetime import datetime
from dotenv import load_dotenv
from bot import get_connection

def extract_first_lines(input_file_path, output_file='PARTE.TXT', num_lines=200):
    try:
        # Leer las primeras líneas del archivo de entrada
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            lines = []
            for i, line in enumerate(input_file):
                if i >= num_lines:
                    break
                lines.append(line)
        
        # Guardar las líneas en el archivo de salida
        with open(output_file, 'w', encoding='utf-8') as output_file:
            output_file.writelines(lines)
            
        print(f"Se han guardado {len(lines)} líneas en {output_file}")  
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def cargar_datos_reniec(archivo_path, linea_omitir=129):
    """
    Carga datos desde un archivo TXT a PostgreSQL usando la conexión existente
    Omite una línea específica durante la carga
    """
    connection = get_connection()
    if not connection:
        print("❌ No se pudo establecer conexión a la base de datos")
        return
    
    try:
        with connection.cursor() as cursor:
            # Leer archivo y procesar líneas
            with open(archivo_path, 'r', encoding='utf-8') as file:
                lineas_procesadas = 0
                lineas_ignoradas = 0
                
                # Saltar la primera línea (encabezados)
                next(file)
                
                for num_linea, linea in enumerate(file, 2):  # Empezamos en 2 porque ya saltamos la primera línea
                    # Omitir la línea específica
                    if num_linea == linea_omitir:
                        print(f"ℹ️ Omitiendo línea {linea_omitir}")
                        continue
                        
                    try:
                        # Ignorar líneas vacías
                        linea = linea.strip()
                        if not linea:
                            continue
                            
                        # Dividir la línea por el separador |
                        campos = linea.split('|')
                        
                        if len(campos) != 16:
                            lineas_ignoradas += 1
                            continue
                        
                        # Validar que no sean campos vacíos
                        if not all(campos[:8]):  # Verificar campos obligatorios
                            lineas_ignoradas += 1
                            continue
                            
                        try:
                            # Convertir fechas
                            fecha_nac = datetime.strptime(campos[4], '%d/%m/%Y').date()
                            fch_inscripcion = datetime.strptime(campos[5], '%d/%m/%Y').date()
                            fch_emision = datetime.strptime(campos[6], '%d/%m/%Y').date()
                            fch_caducidad = datetime.strptime(campos[7], '%d/%m/%Y').date()
                        except ValueError:
                            print(f"⚠ Error en fechas de la línea {num_linea}: {linea}")
                            lineas_ignoradas += 1
                            continue
                        
                        # Insertar datos
                        cursor.execute("""
                            INSERT INTO usuarios VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (dni) DO NOTHING
                        """, (
                            campos[0].strip(), campos[1].strip(), campos[2].strip(), campos[3].strip(),
                            fecha_nac, fch_inscripcion, fch_emision, fch_caducidad,
                            campos[8].strip(), campos[9].strip(), campos[10].strip(), campos[11].strip(),
                            campos[12].strip(), campos[13].strip(), campos[14].strip(), campos[15].strip()
                        ))
                        
                        lineas_procesadas += 1
                        
                    except (ValueError, IndexError) as e:
                        print(f"⚠ Error en línea {num_linea}: {e}")
                        lineas_ignoradas += 1
                        continue
            
            connection.commit()
            print(f"✅ Proceso completado:")
            print(f"📊 Líneas procesadas: {lineas_procesadas}")
            print(f"⚠ Líneas ignoradas: {lineas_ignoradas}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        connection.close()

if __name__ == "__main__":
    # Ejemplo de uso
    archivo_path = r"C:\Users\LENOVO\Desktop\UNT\qda\reniec.txt"
    cargar_datos_reniec(archivo_path)

# Para usar la función, llámala con la ruta de tu archivo:
extract_first_lines(r"C:\Users\LENOVO\Desktop\UNT\qda\reniec.txt")