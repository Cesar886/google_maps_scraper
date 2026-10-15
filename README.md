# Google Maps Scraper y prospección por correo 🌎📊

Repositorio unificado para buscar negocios en Google Maps, localizar correos públicos en sus sitios web, clasificar prospectos por nicho y preparar campañas de correo mediante Brevo SMTP.

> Usa solamente datos públicos con una finalidad comercial legítima, respeta las solicitudes de baja y las leyes aplicables en el lugar donde operes.

This is script is a scraping script developed with Python and its automation library Selenium. **Consists of reading a list of keywords, searching them in the Google Maps search, and getting its data and cover image**.

The script goes one by one searching for the keyword, and storing the data in a list, to finally export it to an Excel file located in the folder specified by the user when running the script.

In the presentation video I show the script running without hiding the Chrome window, and it can be seen quite clear the process that the script follows.

However, although I have added [that version](build/maps_scraper_juaristech_windowed_demo.exe) in the build folder, the final version and the one it is in the source code, works without showing the Chrome window, because it works with 5 simultaneous threads to increase the speed and obtain the results faster.

For now the script works only for Spanish and English languages, however, I can add more languages in the future.

[![Google Maps Scraper](https://juaristech.com/wp-content/uploads/2021/11/google-maps-scraper-result.jpg)](https://juaristech.com/google-maps-scraper "JuarisTech")

## How to Run It

To execute this script you need to run it in the command prompt.

```bash
google_maps_scraper_juaristech.exe
```

Then, some questions will appear, which are necessary to run the script:

1. You will need to type "ES" for Spanish or "EN" for English.

    ```bash
    [1] Introduce the language, (ES o EN): 
    ```
2. You will need to specify the folder to save the output Excel and images. For example: *D:\Projects\Spain\Madrid\output\\*

    ```bash
    [2] Introduce the path to save the images:
    ```

3. To finish, you need to specify where is located the *.txt* file with the keywords to search. For example: *D:\Projects\Spain\Madrid\places.txt*

    ```bash
    [3] Introduce the path of the keywords txt file:
    ```

Then the script starts to work, and when it finished, the Excel file would appear in the output folder.

## How to run the script in Python

If you want to customize the script or just launch it with Python, you can follow this steps:

First create a virtual environment and activate it:

Windows:
```bash
virtualenv env
.\env\Scripts\activate
```

Ubuntu:
```bash
python3 -m venv env
source env/bin/activate
```

Then install the necessary requirements, which are are specified in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

And launch the main file:

```bash
python .\main_datos_maps.py
```

## Tutorial article and video

For any doubts about how to use the program, you can read the article of our web or see the demo video.

- Explanatory article: https://juaristech.com/google-maps-scraper
- Demo video: https://youtu.be/XX-u-eNkRFs

## Contact

- Website: [JuarisTech](https://juaristech.com/)
- Email: admin@juaristech.com



## Bulk searches on Linux

The Python version supports category and location queries such as `cafeterias en Monterrey`. It visits each result and searches the public business website for a contact email.

Run it with:

```bash
source .venv/bin/activate
python main_datos_maps.py
```

The script asks for the language, the TXT file containing one search per line, and the maximum number of results per search. It does not create Excel files or download images. New contacts are appended to `sendEmail.txt` in the format used by `send_email.py`:

```text
email|niche|business|contact name
```

Only businesses with a public email are added. Existing email addresses are preserved and not duplicated. Google Maps and business websites may omit contact details, and automated browsing may occasionally be rate-limited.


## Flujo completo desde una sola carpeta

1. Crea y activa el entorno virtual.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Crea un TXT con una búsqueda por línea, por ejemplo `dentistas en Monterrey`.
4. Ejecuta `python main_datos_maps.py --search-file busquedas.txt` para generar o actualizar `sendEmail.txt`.
5. Revisa manualmente la lista antes de iniciar cualquier campaña.
6. Define la variable de entorno `SMTP_PASSWORD` y ejecuta primero una prueba a tu propio correo.

Para ver los nichos disponibles sin enviar mensajes:

```bash
python send_email.py --list-niches
```

Para enviar una prueba individual:

```bash
SMTP_PASSWORD=tu-clave-smtp python send_email.py --to tu-correo@ejemplo.com --niche general --business "Negocio de prueba"
```

El envío a toda la lista se ejecuta con `python send_email.py --all`. Antes de hacerlo, revisa la lista y los límites de tu proveedor. Los archivos `sendEmail.txt`, `sent_emails.jsonl` y `.smtp_password` están excluidos por `.gitignore`; contienen datos privados y nunca deben subirse a GitHub.

La visión, el estado y los siguientes pasos comerciales están documentados en [`CONTEXTO_PROYECTO_VENTA_PAGINAS.md`](CONTEXTO_PROYECTO_VENTA_PAGINAS.md).
