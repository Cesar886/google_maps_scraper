# Google Maps Scraper

Repositorio unificado para obtener correos públicos de negocios encontrados en Google Maps y, de forma opcional, preparar campañas mediante Brevo SMTP. El scraper no crea Excel, no descarga imágenes y nunca envía correos por sí mismo.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

Con varias búsquedas indicadas directamente:

```bash
python main_datos_maps.py \
  --search "dentistas en Monterrey" \
  --search "veterinarias en Monterrey"
```

O con un TXT que contenga una búsqueda por línea:

```bash
python main_datos_maps.py --search-file busquedas.txt
```

Valores predeterminados: 15 resultados por búsqueda, pausa aleatoria de 2 a 5 segundos entre negocios y de 30 a 90 segundos entre búsquedas. Todos son configurables:

```bash
python main_datos_maps.py \
  --search-file busquedas.txt \
  --max-results 20 \
  --max-searches 3 \
  --business-delay-min 2 \
  --business-delay-max 5 \
  --search-delay-min 30 \
  --search-delay-max 90
```

El rango recomendado de `--max-results` es 10 a 25. `--max-searches` limita cuántas búsquedas pendientes se procesan en esa ejecución.

## Guardado y reanudación

Cada correo nuevo se añade inmediatamente a `sendEmail.txt` con el formato:

```text
correo|nicho|negocio|contacto
```

El archivo se abre exclusivamente en modo append; cada línea se vacía y sincroniza a disco antes de continuar. Los correos que ya existen no se duplican.

El estado se guarda después de cada negocio en `progress.json`. Si existe progreso compatible, una ejecución interactiva pregunta si debe continuar; en automatizaciones se reanuda automáticamente. También se puede elegir de forma explícita:

```bash
python main_datos_maps.py --search-file busquedas.txt --resume
python main_datos_maps.py --search-file busquedas.txt --restart
```

`--restart` reinicia solamente el progreso: nunca borra ni sobrescribe `sendEmail.txt`.

## Bloqueos y registro

El proceso se detiene limpiamente si encuentra un captcha, un aviso de tráfico inusual, dos búsquedas vacías seguidas o tres timeouts seguidos. No intenta resolver ni evadir captchas. Ctrl+C sigue el mismo cierre: conserva el progreso y cierra Chrome/ChromeDriver.

Cada búsqueda imprime negocios revisados, correos nuevos, negocios sin correo, duplicados y tiempo. El historial también queda en `scraper.log`.

Consulta todas las opciones con:

```bash
python main_datos_maps.py --help
```

## Pruebas

La prueba automatizada cubre escritura incremental, bloqueo simulado, cierre del driver y reanudación exacta:

```bash
python -m unittest -v test_batch_scraper.py
```


## Envío opcional de propuestas

`send_email.py` procesa la lista generada por el scraper y selecciona una plantilla según el nicho. Revisa siempre los destinatarios antes de enviar y usa solamente datos públicos con una finalidad legítima, respetando las solicitudes de baja y las leyes aplicables.

Consulta los nichos sin enviar mensajes:

```bash
python send_email.py --list-niches
```

Haz primero una prueba dirigida a tu propio correo:

```bash
SMTP_PASSWORD=tu-clave-smtp python send_email.py \
  --to tu-correo@ejemplo.com \
  --niche general \
  --business "Negocio de prueba"
```

El envío de toda la lista se inicia explícitamente con `python send_email.py --all`. La contraseña también puede guardarse localmente en `.smtp_password`.

`sendEmail.txt`, `sent_emails.jsonl`, `.smtp_password`, `progress.json` y `scraper.log` están excluidos por `.gitignore` y nunca deben publicarse. La visión comercial y los siguientes pasos están en [`CONTEXTO_PROYECTO_VENTA_PAGINAS.md`](CONTEXTO_PROYECTO_VENTA_PAGINAS.md).
