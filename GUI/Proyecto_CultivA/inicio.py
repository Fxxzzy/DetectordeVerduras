import flet as ft

def main(page: ft.Page):
    # Crear el título
    title = ft.Text(
        "CultivA",
        size=30,
        weight=ft.FontWeight.BOLD,
        color="white",
        text_align=ft.TextAlign.CENTER,
    )

    # Crear la imagen
    image = ft.Image(
        src="img/planta.png",
        width=150,
        height=80,
        fit=ft.ImageFit.CONTAIN
    )

    # Crear los botones con imagen y color personalizado
    button1 = ft.ElevatedButton(
        text="Cargar Imagen",
        icon=ft.icons.UPLOAD_FILE,
        bgcolor="#69bf58",
        color="white",
        on_click=lambda _: open_upload_dialog(page)
    )
    button2 = ft.ElevatedButton(
        text="Tomar Foto",
        icon=ft.icons.CAMERA_ALT,
        bgcolor="#69bf58",
        color="white",
        on_click=lambda _: open_camera_dialog(page)
    )
    button3 = ft.ElevatedButton(
        text="Chatbot",
        icon=ft.icons.CHAT,
        bgcolor="#69bf58",
        color="white"
    )

    navigation_container = ft.Container(
        col=3,
        bgcolor="#69bf58",
        border_radius=ft.border_radius.all(10),
        padding=ft.padding.all(10),  # Ajusta el padding entre botones
        content=ft.Column(
            controls=[
                ft.Container(
                    content=title,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=image,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=button1,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=button2,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=button3,
                    alignment=ft.alignment.center
                ),
            ],
            alignment=ft.MainAxisAlignment.START,  # Alinea el contenido a la izquierda
            expand=True
        )
    )

    # Contenedor principal
    main_container = ft.Container(
        content=ft.Row(
            controls=[navigation_container],
            alignment=ft.MainAxisAlignment.START,  # Alinea el contenedor al inicio (izquierda)
        ),
        expand=True
    )

    page.window.width = 800
    page.window.height = 600
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_center = True
    page.bgcolor = "#e6ffd2"

    page.add(main_container)

def open_upload_dialog(page: ft.Page):
    # Crear el cuadro de diálogo de carga de imagen
    file_picker = ft.FilePicker(on_result=lambda e: load_image(page, e.files[0]) if e.files else None)
    page.overlay.append(file_picker)

    dialog = ft.AlertDialog(
        title=ft.Text(
            "Cargar Imagen",
            size=20,
            weight=ft.FontWeight.BOLD,
            color="#277e1b"
        ),
        content=ft.Column(
            controls=[
                ft.Text("Selecciona una imagen para cargar:", color="#277e1b"),
                file_picker
            ],
            spacing=10,
        ),
        actions=[
            ft.TextButton(
                "Abrir Explorador",
                on_click=lambda _: file_picker.pick_files(allow_multiple=False),
                style=ft.ButtonStyle(
                    color="#e6ffd2",
                    bgcolor="#277e1b",
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            ),
            ft.TextButton(
                "Cerrar",
                on_click=lambda _: close_dialog(page),
                style=ft.ButtonStyle(
                    color="#e6ffd2",
                    bgcolor="#277e1b",
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            )
        ],
        bgcolor="#e6ffd2",
        shape=ft.RoundedRectangleBorder(radius=12),
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

def close_dialog(page: ft.Page):
    page.dialog.open = False
    page.update()

def load_image(page: ft.Page, file):
    # Función para cargar la imagen seleccionada
    image_container = ft.Container(
        content=ft.Image(
            src=file.path,
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN
        )
    )
    page.controls[0].content.controls.append(image_container)
    page.update()

def open_camera_dialog(page: ft.Page):
    import cv2
    from PIL import Image
    from io import BytesIO
    import base64

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se puede abrir la cámara")
        return

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("No se puede capturar la imagen")
        return

    # Convertir la imagen a base64 para mostrarla en Flet
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    image_container = ft.Container(
        content=ft.Image(
            src=f"data:image/png;base64,{img_str}",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN
        )
    )
    page.controls[0].content.controls.append(image_container)
    page.update()

ft.app(target=main)
