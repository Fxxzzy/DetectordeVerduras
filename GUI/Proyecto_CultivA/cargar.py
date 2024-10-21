import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from plyer import notification
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import webbrowser

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

# Contadores para métricas
TP = 0
FP = 0
TN = 0
FN = 0

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
    global TP, FP, TN, FN
    
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
                if mejor_tipo == 'Saludable':
                    imagen_match = np.array(imagenes_lechuga[mejor_coincidencia])
                else:
                    imagen_match = np.array(imagenes_lechugaMala[mejor_coincidencia])
            elif mejor_categoria == 'Tomate':
                if mejor_tipo == 'Saludable':
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
                timeout=10
            )
            
            # Actualizar contadores para métricas
            if mejor_tipo == 'Saludable' and mejor_categoria == 'Lechuga':
                TP += 1
            elif mejor_tipo == 'Enferma' and mejor_categoria == 'Lechuga':
                FN += 1
            elif mejor_tipo == 'Saludable' and mejor_categoria == 'Tomate':
                TN += 1
            elif mejor_tipo == 'Enfermo' and mejor_categoria == 'Tomate':
                FP += 1
            
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            messagebox.showinfo("Sin coincidencias", "No se encontraron coincidencias significativas.")
            FP += 1
    else:
        messagebox.showinfo("Error", "No se detectaron características en el área seleccionada.")
        FP += 1
    
    # Calcular y mostrar las métricas
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    sensibilidad = TP / (TP + FN) if (TP + FN) > 0 else 0
    especificidad = TN / (TN + FP) if (TN + FP) > 0 else 0
    
    print(f"Precisión: {precision:.2f}")
    print(f"Sensibilidad: {sensibilidad:.2f}")
    print(f"Especificidad: {especificidad:.2f}")

def salir():
    ventana.destroy()

def visitar_pagina():
    url = "https://github.com/Darkacee"
    webbrowser.open(url)

ventana = tk.Tk()
ventana.title("ZITA")
ventana.geometry("400x200")
ventana.configure(bg="white")

boton_cargar_imagen = tk.Button(ventana, text="Cargar Imagen", command=cargar_imagen, width=20)
boton_tomar_foto = tk.Button(ventana, text="Tomar Foto", command=tomar_foto, width=20)
boton_salir = tk.Button(ventana, text="Salir", command=salir, width=20)

boton_cargar_imagen.pack(pady=10)
boton_tomar_foto.pack(pady=10)
boton_salir.pack(pady=10)

# Procesar imágenes de referencia al iniciar la aplicación
procesar_imagenes_de_referencia()

ventana.mainloop()
