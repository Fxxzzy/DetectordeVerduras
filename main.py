import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from plyer import notification
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import webbrowser  # Importar para abrir URLs en el navegador

carpeta_lechuga = 'C:\\Users\\Darka\\OneDrive\\Escritorio\\Python\\ZITA\\Lechuga'
carpeta_tomate = 'C:\\Users\\Darka\\OneDrive\\Escritorio\\Python\\ZITA\\Tomate'
carpeta_tomateMalos = 'C:\\Users\\Darka\\OneDrive\\Escritorio\\Python\\ZITA\\Tomates echados a perder'
carpeta_lechugaMala = 'C:\\Users\\Darka\\OneDrive\\Escritorio\\Python\\ZITA\\Lechugas echadas a perder'


# Listas para almacenar los descriptores y las imágenes de referencia
descriptores_lechuga = []
imagenes_lechuga = []
nombres_imagenes_lechuga = []

descriptores_tomate = []
imagenes_tomate =  []
nombres_imagenes_tomate = []

descriptores_tomateMalos = []
imagenes_tomateMalos = []
nombres_imagenes_tomateMalos = []

descriptores_lechugaMala = []
imagenes_lechugaMala = []
nombres_imagenes_lechugaMala = []

# Detector de características (ORB)
orb = cv2.ORB_create()

def procesar_imagenes_de_referencia():
    global descriptores_lechuga, imagenes_lechuga, nombres_imagenes_lechuga
    global descriptores_tomate, imagenes_tomate, nombres_imagenes_tomate
    global descriptores_tomateMalos, imagenes_tomateMalos, nombres_imagenes_tomateMalos
    global descriptores_lechugaMala, imagenes_lechugaMala, nombres_imagenes_lechugaMala
    
    # Función interna para procesar imágenes
    def procesar_imagenes(carpeta, descriptores, imagenes, nombres_imagenes):
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".jpg") or archivo.endswith(".png"):
                ruta_imagen = os.path.join(carpeta, archivo)
                imagen = Image.open(ruta_imagen)
                imagen_cv = np.array(imagen)
                
                if imagen_cv.ndim == 3 and imagen_cv.shape[2] == 3:
                    gray = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
                else:
                    gray = imagen_cv
                
                kp, des = orb.detectAndCompute(gray, None)
                
                if des is not None:
                    descriptores.append(des)
                    imagenes.append(imagen)
                    nombres_imagenes.append(archivo)

    # Procesar todas las carpetas
    procesar_imagenes(carpeta_lechuga, descriptores_lechuga, imagenes_lechuga, nombres_imagenes_lechuga)
    procesar_imagenes(carpeta_tomate, descriptores_tomate, imagenes_tomate, nombres_imagenes_tomate)
    procesar_imagenes(carpeta_tomateMalos, descriptores_tomateMalos, imagenes_tomateMalos, nombres_imagenes_tomateMalos)
    procesar_imagenes(carpeta_lechugaMala, descriptores_lechugaMala, imagenes_lechugaMala, nombres_imagenes_lechugaMala)

def cargar_imagen():
    ruta_imagen = filedialog.askopenfilename(initialdir="/", title="Ingresar Imagen",
                                             filetypes=(("Archivos de Imagen", "*.jpg;*.png"), ("Todos los archivos", "*.*")))
    if ruta_imagen:
        imagen = Image.open(ruta_imagen)
        procesar_y_comparar_imagen(imagen)

def tomar_foto():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se puede abrir la cámara")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se puede recibir el frame (final de la secuencia?). Saliendo ...")
            break

        cv2.imshow('Ingresa la verdura a analizar', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Capturar la última imagen
    ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()

    if ret:
        imagen = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        procesar_y_comparar_imagen(imagen)
    else:
        print("Error al capturar la imagen")

def procesar_y_comparar_imagen(imagen):
    # Convertir la imagen a formato numpy
    imagen_cv = np.array(imagen)
    
    # Convertir la imagen a escala de grises si es a color
    if imagen_cv.ndim == 3 and imagen_cv.shape[2] == 3:
        gray = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = imagen_cv
    
    # Mostrar la imagen en una ventana nueva
    cv2.imshow('Imagen Seleccionada', imagen_cv)
    
    # Seleccionar un área de interés para el análisis
    x, y, w, h = cv2.selectROI('Imagen Seleccionada', imagen_cv, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow('Imagen Seleccionada')
    
    # Recortar el área seleccionada
    area_seleccionada = gray[y:y+h, x:x+w]
    
    # Detectar keypoints y descriptores del área seleccionada
    kp_area, des_area = orb.detectAndCompute(area_seleccionada, None)
    
    if des_area is not None:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        mejor_coincidencia = None
        mejor_distancia = 100
        mejor_categoria = None
        mejor_tipo = None
        
        # Función para comparar con descriptores y encontrar la mejor coincidencia
        def comparar_imagenes(descriptores, imagenes, categoria, tipo):
            nonlocal mejor_coincidencia, mejor_distancia, mejor_categoria, mejor_tipo
            for i, descriptor in enumerate(descriptores):
                matches = bf.match(descriptor, des_area)
                if len(matches) == 0:
                    continue
                distancia = sum([match.distance for match in matches]) / len(matches)
                
                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_coincidencia = i
                    mejor_categoria = categoria
                    mejor_tipo = tipo
        
        # Comparar con las imágenes de lechuga
        comparar_imagenes(descriptores_lechuga, imagenes_lechuga, 'Lechuga', 'Saludable')
        comparar_imagenes(descriptores_lechugaMala, imagenes_lechugaMala, 'Lechuga', 'Enferma')
        
        # Comparar con las imágenes de tomate
        comparar_imagenes(descriptores_tomate, imagenes_tomate, 'Tomate', 'Saludable')
        comparar_imagenes(descriptores_tomateMalos, imagenes_tomateMalos, 'Tomate', 'Enfermo')
        
        # Mostrar resultado si la distancia es aceptable
        if mejor_coincidencia is not None and mejor_distancia < 50:
            imagen_match = None
            
            if mejor_categoria == 'Lechuga':
                if mejor_tipo == 'Sana':
                    imagen_match = np.array(imagenes_lechuga[mejor_coincidencia])
                else:
                    imagen_match = np.array(imagenes_lechugaMala[mejor_coincidencia])
            elif mejor_categoria == 'Tomate':
                if mejor_tipo == 'Sano':
                    imagen_match = np.array(imagenes_tomate[mejor_coincidencia])
                else:
                    imagen_match = np.array(imagenes_tomateMalos[mejor_coincidencia])
            
            cv2.imshow('Imagen Coincidente', imagen_match)
            
            # Mostrar notificación del sistema
            notification_title = f"¡Se encontró una {mejor_categoria.lower()} {mejor_tipo.lower()} similar!"
            notification_text = f"Categoría: {mejor_categoria} ({mejor_tipo})"
            notification.notify(
                title=notification_title,
                message=notification_text,
                app_icon=None,
                timeout=10  # La notificación desaparecerá después de 10 segundos
            )
            
            # Mostrar menú con Tkinter
            mostrar_menu(mejor_categoria.lower(), mejor_tipo.lower())
            
    # Esperar a que se presione una tecla para cerrar las ventanas de OpenCV
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def mostrar_menu(categoria, tipo):
    # Crear ventana de Tkinter
    root = tk.Tk()
    root.title(f"Coincidencia encontrada: {categoria.capitalize()} ({tipo.capitalize()})")
    root.configure(background='#0c4b43')  # Cambiar color de fondo
    root.geometry("300x300")
    root.resizable(0, 0)

    # Crear estilo para botones (debe estar antes de crear los botones)
    style = ttk.Style()
    style.configure('TButton', background='#4CAF50', foreground='black', font=('Helvetica', 12, 'bold'))

    # Funciones para los botones
    def mostrar_estado():
        messagebox.showinfo("Estado", f"Estado de la {categoria}: {tipo.capitalize()}")

    def mostrar_enfermedades():
        messagebox.showinfo("Enfermedades", f"Enfermedades de la {categoria}: puede que esté afectada por la descomposición avanzada que se produce al no tener el cuidado requerido")

    def salir():
        root.destroy()

    # Etiqueta con información de la imagen
    label_info = tk.Label(root, text=f"Categoría: {categoria.capitalize()} ({tipo.capitalize()})", background='#0c4b43', foreground='#FFFFFF', font=('Helvetica', 12, 'bold'))
    label_info.pack(pady=10)

    # Botones (creados después de configurar el estilo)
    btn_estado = ttk.Button(root, text="Estado", command=mostrar_estado, style='TButton')
    btn_estado.pack(pady=5)

    btn_enfermedades = ttk.Button(root, text="Enfermedades", command=mostrar_enfermedades, style='TButton')
    btn_enfermedades.pack(pady=5)

    btn_salir = ttk.Button(root, text="Salir", command=salir, style='TButton')
    btn_salir.pack(pady=10)

    # Ajustar la posición de la ventana en el centro de la pantalla
    wtotal = root.winfo_screenwidth()
    htotal = root.winfo_screenheight()
    wventana = 300
    hventana = 300
    pwidth = round(wtotal/2 - wventana/2)
    pheigth = round(htotal/2 - hventana/2)
    root.geometry(f"{wventana}x{hventana}+{pwidth}+{pheigth}")

    # Mostrar la ventana
    root.mainloop()

# Función para abrir el enlace del chatbot
def abrir_chatbot():
    webbrowser.open("https://landbot.site/v3/H-2523525-MTST5JGGRI7A7KMM/index.html")

# Llamar a las funciones para procesar las imágenes de referencia
procesar_imagenes_de_referencia()

# Crear una ventana principal de Tkinter
root = tk.Tk()
root.title("CultIvA")
root.configure(background='#0c4b43')  # Cambiar color de fondo
root.geometry("300x300")
root.resizable(0,0)

# Crear estilo para botones
style = ttk.Style()
style.configure('TButton', background='#4CAF50', foreground='black', font=('Helvetica', 12, 'bold'))

# Agregar logo
logo_path = r"C:\Users\Darka\OneDrive\Escritorio\Python\ZITA\logo_sin_fondo.png"  # Reemplazar con la ruta correcta del logo
logo = Image.open(logo_path)
logo = logo.resize((100, 100), Image.LANCZOS)  # Redimensionar el logo según sea necesario con LANCZOS
logo_tk = ImageTk.PhotoImage(logo)

# Establecer el icono de la aplicación
root.iconphoto(False, logo_tk)

# Colocar el logo en la ventana principal
logo_label = ttk.Label(root, image=logo_tk, background='#0c4b43')
logo_label.pack(pady=20)

# Botones para cargar imagen, tomar foto y abrir el chatbot
btn_cargar = ttk.Button(root, text="Cargar Imagen", command=cargar_imagen, style='TButton')
btn_cargar.pack(pady=10)

btn_tomar_foto = ttk.Button(root, text="Tomar Foto", command=tomar_foto, style='TButton')
btn_tomar_foto.pack(pady=10)

btn_chatbot = ttk.Button(root, text="Chatbot", command=abrir_chatbot, style='TButton')
btn_chatbot.pack(pady=10)

wtotal = root.winfo_screenwidth()
htotal = root.winfo_screenheight()
wventana = 300
hventana = 300
pwidth = round(wtotal/2 - wventana/2)
pheigth = round(htotal/2 - hventana/2)
root.geometry(str(wventana)+"x"+str(hventana)+"+"+str(pwidth)+"+"+str(pheigth))

# Mostrar la ventana principal
root.mainloop()
