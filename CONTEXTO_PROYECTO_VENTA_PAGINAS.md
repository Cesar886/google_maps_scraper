# Contexto del proyecto: venta de páginas web

**Última actualización:** 15 de octubre de 2026  
**Responsable:** Daniel Rodríguez  
**Nombre actual de la operación:** Website Developer / Web Development & Digital Solutions  
**Portafolio:** https://dev.danielrdz.site/

## 1. Propósito del proyecto

Construir un sistema repetible para encontrar negocios que necesitan una mejor presencia digital, contactarlos con una propuesta personalizada por sector y convertir esos prospectos en clientes de páginas web.

No se busca solamente enviar correos. La meta completa es crear un proceso comercial medible:

1. Encontrar negocios adecuados.
2. Obtener datos públicos de contacto.
3. Clasificar cada prospecto por giro.
4. Enviar una propuesta relevante y profesional.
5. Dar seguimiento a quienes respondan.
6. Diagnosticar su necesidad y cotizar una solución concreta.
7. Cerrar la venta, construir la página y solicitar testimonio o recomendación.

## 2. Propuesta de valor actual

Ofrecemos páginas web profesionales para negocios locales y prestadores de servicios. La propuesta enfatiza:

- Diseño rápido, moderno y adaptable a celular.
- Presentación clara de servicios, productos, ubicación y horarios.
- Contacto directo mediante WhatsApp, formularios y correo.
- Integración con Google Maps y redes sociales.
- SEO técnico y local para mejorar la visibilidad en Google.
- Funciones adaptadas al giro: citas, reservaciones, catálogos, galerías, cotizaciones, inscripciones o pagos.
- Una propuesta inicial sin compromiso, con alcance, precio y plazo.

## 3. Lo que ya está construido

### 3.1 Sistema de prospección desde Google Maps

En `google_maps_scraper/` existe una adaptación funcional en Python y Selenium que:

- Ejecuta Chrome en modo headless.
- Acepta búsquedas por categoría y ubicación, por ejemplo `dentistas en Monterrey`.
- Recorre varios resultados por cada búsqueda.
- Trabaja hasta con cuatro hilos en paralelo.
- Extrae nombre, categoría, dirección, teléfono, sitio web, horario, calificación y reseñas.
- Visita el sitio público del negocio para buscar un correo de contacto.
- También revisa páginas internas como contacto, nosotros o about.
- Descarta correos técnicos o falsos comunes.
- Evita duplicar direcciones ya guardadas.
- Clasifica automáticamente el negocio por nicho.
- Agrega los prospectos encontrados a `sendEmail.txt`.

El formato de cada registro es:

```text
correo|nicho|negocio|nombre del contacto
```

### 3.2 Clasificación por nichos

El sistema reconoce 20 categorías contando la categoría general:

- General
- Restaurantes y cafeterías
- Consultorios médicos
- Clínicas dentales
- Abogados
- Contadores
- Inmobiliarias
- Gimnasios
- Belleza y estética
- Barberías
- Veterinarias
- Talleres automotrices
- Construcción y arquitectura
- Hoteles
- Tiendas y comercio electrónico
- Escuelas y cursos
- Salones y servicios para eventos
- Psicología
- Fotografía
- Seguros

Hay reglas de alias para convertir términos parecidos al nicho correcto, por ejemplo `café` a restaurante, `dentista` a dental y `gym` a gimnasio.

### 3.3 Sistema de correos comerciales

En `send_email.py` existe un sistema de envío mediante Brevo SMTP que:

- Envía con conexión TLS.
- Permite contactar una dirección manualmente o procesar toda la lista.
- Personaliza asunto, negocio, saludo y contenido según el nicho.
- Inserta funcionalidades recomendadas específicas para cada sector.
- Incluye el portafolio profesional.
- Detecta duplicados dentro del mismo lote.
- Evita reenviar a destinatarios ya registrados, salvo que se use la opción explícita de reenvío.
- Registra cada envío exitoso con fecha, estado, nicho, negocio y contacto.
- Continúa con el siguiente destinatario si falla un envío individual.

### 3.4 Campaña realizada

Al 14 de octubre de 2026, los archivos locales muestran:

- **309 prospectos comerciales** en `sendEmail.txt`.
- **311 eventos de envío exitoso** en `sent_emails.jsonl`.
- Los primeros **2 eventos fueron pruebas**; los otros **309 corresponden a la campaña comercial registrada**.
- Los envíos documentados se realizaron entre el 12 y el 14 de octubre de 2026.

Esto demuestra que el flujo de búsqueda, clasificación, personalización, envío y registro ya se utilizó en una campaña real.

### 3.5 Activos existentes

- Portafolio publicado: https://dev.danielrdz.site/
- Base local de prospectos: `sendEmail.txt`.
- Historial local de envíos: `sent_emails.jsonl`.
- Scraper y extractor de correos: `google_maps_scraper/`.
- Automatización de propuestas comerciales: `send_email.py`.
- Credenciales SMTP locales configuradas para la operación.

## 4. Estado real del proyecto

### Ya validado técnicamente

- Es posible obtener prospectos públicos desde Google Maps y sus sitios web.
- Es posible ordenarlos por sector y evitar duplicados.
- Es posible generar mensajes especializados por nicho.
- Es posible enviar y registrar campañas mediante Brevo.
- Ya existe un portafolio al cual dirigir a los prospectos.

### Todavía no validado comercialmente

No hay evidencia almacenada en este proyecto sobre:

- Cuántos prospectos abrieron el correo.
- Cuántos hicieron clic en el portafolio.
- Cuántos respondieron.
- Cuántos pidieron cotización.
- Cuántas reuniones se agendaron.
- Cuántas ventas se cerraron.
- Cuánto ingreso produjo la campaña.

Por lo tanto, el reto principal ya no es solamente técnico: ahora es validar y mejorar la conversión comercial.

## 5. Lo que falta

### Prioridad 1: definir una oferta fácil de comprar

- Elegir de uno a tres nichos iniciales en vez de intentar vender a todos al mismo tiempo.
- Definir paquetes claros con alcance, precio inicial, tiempo de entrega y número de revisiones.
- Separar costos únicos de los recurrentes: dominio, hosting, mantenimiento, cambios y SEO.
- Definir anticipo, forma de pago, condiciones y política de cancelación.
- Crear una promesa concreta sin garantizar resultados imposibles.
- Preparar ejemplos o demos específicos para los nichos elegidos.

### Prioridad 2: construir el proceso de seguimiento

- Centralizar respuestas y estados en un CRM o una hoja de cálculo.
- Usar etapas como: nuevo, contactado, respondió, interesado, reunión, propuesta, negociación, ganado y perdido.
- Preparar entre dos y cuatro seguimientos breves por prospecto.
- Detener automáticamente los seguimientos cuando alguien responda o pida no recibir mensajes.
- Crear respuestas listas para objeciones de precio, tiempo, confianza y necesidad.
- Preparar un guion de llamada de diagnóstico y una plantilla formal de cotización.

### Prioridad 3: medir el embudo

- Registrar entregas, rebotes, aperturas y clics cuando sean confiables y legales.
- Medir respuestas positivas, reuniones, cotizaciones, cierres e ingreso.
- Comparar resultados por nicho, ciudad, asunto, mensaje y seguimiento.
- Calcular tasas de conversión entre cada etapa.
- Tomar decisiones con datos y no solo con cantidad de correos enviados.

### Prioridad 4: mejorar entregabilidad y cumplimiento

- Configurar y verificar SPF, DKIM y DMARC para el dominio remitente.
- Calentar y cuidar la reputación del dominio.
- Establecer límites diarios y pausas entre envíos.
- Procesar rebotes y suprimir direcciones inválidas.
- Incluir una forma clara y sencilla de no recibir más mensajes.
- Mantener una lista de exclusión permanente.
- Revisar las reglas aplicables a correo comercial y protección de datos en los mercados donde se contacte.
- Usar solo información de contacto publicada para fines comerciales legítimos.

### Prioridad 5: hacer más segura y robusta la automatización

- No compartir ni subir el archivo `.smtp_password` a Claude, Git, Drive ni otros servicios.
- No usar las listas con correos personales como contexto de una IA; compartir solamente métricas agregadas.
- Mover secretos a variables de entorno o a un gestor de secretos.
- Añadir un modo de vista previa o `dry-run` que nunca envíe correos.
- Añadir límite por lote, pausa configurable y confirmación antes de una campaña.
- Validar mejor el formato de los correos.
- Registrar fallos y rebotes, no solo éxitos.
- Añadir pruebas automatizadas para plantillas, deduplicación y clasificación.
- Documentar instalación y ejecución completa en un único README.
- Inicializar control de versiones y excluir secretos, bases de prospectos y registros mediante `.gitignore`.

### Prioridad 6: convertir el servicio en un producto repetible

- Crear una plantilla base reutilizable por nicho.
- Preparar un formulario de levantamiento de información del cliente.
- Estandarizar diseño, desarrollo, revisión, publicación y entrega.
- Crear listas de verificación para dominio, analítica, SEO, seguridad, accesibilidad y respaldos.
- Ofrecer mantenimiento mensual y servicios adicionales.
- Solicitar testimonios y casos de estudio después de cada proyecto exitoso.

## 6. Metas

### Meta principal

Conseguir clientes de páginas web de forma constante mediante un sistema de prospección, seguimiento y venta que sea medible, respetuoso y repetible.

### Metas de corto plazo: próximos 7 días

- Elegir el nicho inicial con mejor oportunidad.
- Definir tres paquetes y sus precios.
- Revisar las respuestas recibidas por la campaña ya enviada.
- Crear el CRM con los 309 prospectos y su estado real.
- Preparar dos mensajes de seguimiento.
- Configurar correctamente la autenticación y reputación del dominio de correo.

### Metas de 30 días

- Tener un embudo comercial funcionando y actualizado.
- Conseguir respuestas calificadas y reuniones de diagnóstico.
- Enviar cotizaciones con una plantilla uniforme.
- Cerrar los primeros clientes atribuibles a este sistema.
- Identificar con datos el nicho, oferta y mensaje con mejor conversión.

### Metas de 90 días

- Tener un flujo constante de prospectos nuevos y seguimientos.
- Contar con casos de estudio y testimonios verificables.
- Reducir el tiempo de producción mediante plantillas reutilizables.
- Generar ingreso recurrente con mantenimiento, hosting u optimización.
- Conocer el valor promedio de cada venta y el rendimiento de cada campaña.

## 7. Indicadores que debemos registrar

Para cada periodo y campaña:

- Prospectos encontrados.
- Prospectos válidos y únicos.
- Correos enviados.
- Correos entregados y rebotados.
- Respuestas totales.
- Respuestas positivas.
- Solicitudes de baja.
- Reuniones agendadas y realizadas.
- Cotizaciones enviadas.
- Ventas ganadas y perdidas.
- Ingreso total y mensual recurrente.
- Conversión por nicho, ciudad, mensaje y seguimiento.
- Tiempo promedio desde el primer contacto hasta el cierre.

## 8. Próximo plan de ejecución recomendado

1. Auditar las respuestas de los 309 contactos ya abordados.
2. Pasar la campaña a un CRM sin volver a enviar a toda la lista.
3. Elegir un nicho según las señales reales de interés.
4. Diseñar una oferta y una demo específica para ese nicho.
5. Enviar seguimientos personalizados en lotes pequeños.
6. Medir respuestas, reuniones y cierres semanalmente.
7. Mejorar mensaje, oferta y selección de prospectos después de cada lote.
8. Automatizar más solamente cuando el proceso manual ya muestre conversión.

## 9. Cómo debe ayudar Claude en este proyecto

Claude debe actuar como colaborador de estrategia comercial, copywriting, automatización y documentación. Sus propuestas deben:

- Priorizar ventas reales y aprendizaje medible, no solo volumen de envíos.
- Mantener los mensajes breves, personalizados y relevantes.
- No inventar respuestas, clientes, métricas ni ventas.
- Distinguir siempre entre lo construido, lo probado y lo todavía supuesto.
- Proteger contraseñas y datos personales.
- No enviar campañas ni ejecutar acciones externas sin aprobación explícita.
- Proponer cambios pequeños que puedan probarse y compararse.
- Mantener actualizado este documento cuando cambie el estado del proyecto.

## 10. Archivos importantes y precauciones

| Archivo o carpeta | Función | Precaución |
|---|---|---|
| `send_email.py` | Plantillas, personalización, envío SMTP y registro | Probar antes de hacer campañas |
| `google_maps_scraper/` | Búsqueda de negocios y extracción de correos públicos | Google o los sitios pueden limitar la automatización |
| `sendEmail.txt` | Base de prospectos | Contiene datos de contacto; no subir como contexto |
| `sent_emails.jsonl` | Historial de envíos | Contiene datos de contacto; no subir como contexto |
| `.smtp_password` | Clave SMTP | Secreto: nunca compartir ni versionar |

## 11. Decisiones pendientes

Claude debe ayudarnos a decidir, con preguntas concretas y opciones comparables:

- ¿Qué nicho priorizar primero?
- ¿En qué ciudad o región concentrarnos?
- ¿Qué incluyen los paquetes y cuánto cuestan?
- ¿Qué tecnología y hosting se usarán para los sitios de clientes?
- ¿Qué parte se cobra por única vez y qué parte será mensual?
- ¿Qué capacidad semanal de ventas y producción tenemos?
- ¿Cómo se manejarán soporte, revisiones y mantenimiento?
- ¿Qué métricas reales produjo la primera campaña?

## 12. Definición de éxito

El proyecto será exitoso cuando el sistema no solo encuentre y contacte negocios, sino que produzca de manera predecible conversaciones calificadas, cotizaciones, ventas de páginas web y clientes satisfechos, con métricas claras y sin comprometer la reputación del dominio ni la privacidad de los prospectos.
