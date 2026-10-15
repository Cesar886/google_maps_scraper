#!/usr/bin/env python3
"""Envía propuestas comerciales por nicho mediante Brevo SMTP."""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_LIST = SCRIPT_DIR / "sendEmail.txt"
PASSWORD_FILE = SCRIPT_DIR / ".smtp_password"
DEFAULT_LOG = SCRIPT_DIR / "sent_emails.jsonl"
PORTFOLIO_URL = "https://dev.danielrdz.site/"

TEMPLATES = {
    "general": (
        "Propuesta para mejorar la presencia digital de {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Ayudamos a negocios a conseguir una presencia digital profesional con páginas rápidas, adaptadas a celular y preparadas para aparecer en Google.

Podemos crear para {business} un sitio con información clara, servicios, ubicación, reseñas y contacto directo por WhatsApp. La idea es facilitar que nuevos clientes encuentren el negocio y se comuniquen.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta sin compromiso con alcance, precio y tiempo de entrega.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "restaurante": (
        "Una página web para atraer más clientes a {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Hemos revisado la presencia digital de {business} y consideramos que una página propia podría ayudarles a convertir más búsquedas en visitas y pedidos.

La solución web puede estructurarse en secciones claras y orientadas a convertir visitas en clientes:

- Menú digital actualizado y organizado por categorías.
- Horarios, ubicación e integración con Google Maps.
- Galería profesional de platillos, instalaciones y ambiente.
- Integración de reseñas para fortalecer la confianza.
- Sistema de reservaciones o solicitudes de mesa.
- Contacto directo y llamados a la acción mediante WhatsApp.
- Diseño responsive optimizado para teléfonos y computadoras.
- SEO local para mejorar la visibilidad en búsquedas de Google.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos prepararles una propuesta concreta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "consultorio": (
        "Propuesta de sitio web para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos ayudar a {business} con una página profesional que genere confianza y facilite que los pacientes encuentren información y soliciten una cita.

Podría incluir servicios, especialidades, perfil profesional, ubicación, horarios, preguntas frecuentes y un botón de WhatsApp para agendar.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Con gusto podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "dental": (
        "Sitio web y citas para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Una página moderna para {business} puede mostrar tratamientos, instalaciones y experiencia profesional, además de facilitar las citas desde Google y WhatsApp.

El sitio puede incluir servicios dentales, casos o testimonios autorizados, ubicación, horarios, preguntas frecuentes y contacto inmediato.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos enviarles una propuesta con precio y tiempo de entrega.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "abogados": (
        "Presencia web profesional para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Nos gustaría proponer una página profesional para {business}, enfocada en transmitir confianza y explicar claramente sus áreas de práctica.

Podría incluir servicios legales, perfil del despacho, preguntas frecuentes, ubicación y un formulario confidencial de contacto o enlace directo a WhatsApp.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si lo consideran útil, podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "contadores": (
        "Sitio web profesional para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página clara y profesional que presente sus servicios contables y facilite la captación de empresas y clientes independientes.

Puede incluir servicios, paquetes, preguntas frecuentes, formulario de diagnóstico y contacto por WhatsApp.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Quedamos disponibles para enviarles una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "inmobiliaria": (
        "Catálogo inmobiliario para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos desarrollar para {business} una página con catálogo de propiedades, fotografías, filtros, ubicación y contacto directo con cada asesor.

Una web propia les permite controlar sus publicaciones y captar prospectos sin depender únicamente de redes sociales o portales externos.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta con alcance, precio y plazo.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "gimnasio": (
        "Página web y registros para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Una página para {business} podría mostrar planes, horarios, entrenadores, instalaciones y promociones, además de recibir registros o consultas por WhatsApp.

El sitio estaría optimizado para celular y para búsquedas locales en Google.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Con gusto podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "belleza": (
        "Reservaciones y presencia web para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página visual y rápida con servicios, precios, galería, ubicación y reservaciones por WhatsApp.

Esto ayudaría a convertir visitas de Google e Instagram en citas de forma más directa.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos enviar una propuesta concreta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "barberia": (
        "Página de servicios y citas para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Nos gustaría ayudar a {business} con una página que muestre cortes, servicios, precios, horarios y ubicación, con un botón directo para reservar por WhatsApp.

Estaría optimizada para celular y búsquedas locales.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Podemos prepararles una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "veterinaria": (
        "Sitio web y citas para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Una página profesional para {business} puede mostrar servicios, horarios, ubicación, atención de urgencias y facilitar las citas por WhatsApp.

También puede incluir recomendaciones para pacientes y perfiles del equipo veterinario.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta con precio y tiempo de entrega.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "taller": (
        "Página web para captar clientes de {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página que muestre servicios automotrices, ubicación, horarios, garantías y un botón para solicitar cotización por WhatsApp.

La web estaría preparada para búsquedas locales como taller, reparación o mantenimiento en su zona.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Con gusto podemos enviarles una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "construccion": (
        "Portafolio web profesional para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos desarrollar para {business} un sitio profesional donde presenten proyectos, servicios, experiencia y medios de contacto para solicitar cotizaciones.

Una galería bien organizada y una página optimizada para Google ayudan a generar confianza antes del primer contacto.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta concreta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "hotel": (
        "Sitio web y reservaciones para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Nos gustaría proponer una página propia para {business} con habitaciones, servicios, galería, ubicación, preguntas frecuentes y solicitud directa de reservación.

Una web propia puede reducir la dependencia de plataformas externas y facilitar reservas por WhatsApp.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Podemos prepararles una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "tienda": (
        "Catálogo o tienda en línea para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos ayudar a {business} con un catálogo o tienda en línea rápida y adaptada a celular, con productos, precios, pagos o pedidos por WhatsApp.

La solución puede comenzar sencilla y crecer conforme aumenten las ventas.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos enviarles una propuesta con opciones y precios.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "escuela": (
        "Sitio web e inscripciones para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página con programas, horarios, requisitos, docentes, preguntas frecuentes e inscripción o solicitud de informes.

El objetivo sería que padres y alumnos encuentren toda la información y contacten fácilmente desde el celular.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Con gusto podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "eventos": (
        "Página web para eventos de {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos desarrollar para {business} una página con paquetes, galería, disponibilidad, ubicación y solicitud de cotización por WhatsApp.

Una web visual permite mostrar mejor el espacio o los servicios y convertir consultas en reservaciones.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "psicologia": (
        "Sitio web profesional para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página cálida, profesional y clara con enfoque terapéutico, modalidades de consulta, preguntas frecuentes y solicitud de cita.

El sitio puede cuidar especialmente la privacidad y facilitar el contacto desde celular.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos enviar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "fotografia": (
        "Portafolio y reservaciones para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} un portafolio rápido y visual con sesiones, paquetes, galerías optimizadas y solicitud de fecha o cotización por WhatsApp.

Una página propia permite presentar el trabajo con mayor control que una red social.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Con gusto podemos preparar una propuesta sin compromiso.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
    "seguros": (
        "Página profesional para {business}",
        """Hola{greeting},

Le contactamos desde Website Developer, especializado en Web Development y soluciones digitales. Podemos crear para {business} una página que explique coberturas y servicios de forma clara, genere confianza y facilite solicitudes de cotización.

Puede incluir formularios, preguntas frecuentes y contacto directo por WhatsApp.

Conozca nuestro portafolio profesional y proyectos publicados:
{portfolio}

Si les interesa, podemos preparar una propuesta con precio y plazo.

Saludos,
Website Developer
Web Development & Digital Solutions
WhatsApp: +52 826 128 8953
Email: contact@danielrdz.site""",
    ),
}

ALIASES = {
    "restaurantes": "restaurante",
    "cafe": "restaurante",
    "cafeteria": "restaurante",
    "bar": "restaurante",
    "medico": "consultorio",
    "clinica": "consultorio",
    "dentista": "dental",
    "abogado": "abogados",
    "contador": "contadores",
    "inmuebles": "inmobiliaria",
    "gym": "gimnasio",
    "spa": "belleza",
    "salon": "belleza",
    "estetica": "belleza",
    "barbero": "barberia",
    "mecanico": "taller",
    "arquitectura": "construccion",
    "constructora": "construccion",
    "ecommerce": "tienda",
    "comercio": "tienda",
    "colegio": "escuela",
    "cursos": "escuela",
    "salon_eventos": "eventos",
    "psicologo": "psicologia",
    "fotografo": "fotografia",
    "aseguradora": "seguros",
}


NICHE_FEATURES = {
    "general": (
        "Presentación clara de servicios, ventajas y propuesta de valor.",
        "Diseño responsive optimizado para teléfonos, tabletas y computadoras.",
        "Formularios y llamados a la acción orientados a generar prospectos.",
        "Integración con WhatsApp, Google Maps y redes sociales.",
        "SEO técnico y local para mejorar la visibilidad en Google.",
    ),
    "consultorio": (
        "Secciones para especialidades, tratamientos y perfil profesional.",
        "Solicitud de citas mediante formulario o contacto directo por WhatsApp.",
        "Horarios, ubicación e integración con Google Maps.",
        "Preguntas frecuentes para orientar a nuevos pacientes.",
        "Diseño confiable, accesible y optimizado para búsquedas locales.",
    ),
    "dental": (
        "Catálogo organizado de tratamientos y servicios odontológicos.",
        "Galería de instalaciones y casos autorizados.",
        "Agendamiento de valoraciones mediante formulario o WhatsApp.",
        "Perfiles profesionales, horarios y ubicación del consultorio.",
        "SEO local para búsquedas de dentistas y tratamientos en la zona.",
    ),
    "abogados": (
        "Presentación profesional del despacho y sus áreas de práctica.",
        "Perfiles del equipo, experiencia y credenciales relevantes.",
        "Formulario confidencial para evaluar nuevas consultas.",
        "Preguntas frecuentes y contenido informativo por especialidad.",
        "SEO local para aumentar la visibilidad del despacho en Google.",
    ),
    "contadores": (
        "Descripción clara de servicios fiscales, contables y administrativos.",
        "Paquetes o soluciones para empresas y profesionales independientes.",
        "Formulario de diagnóstico para captar prospectos calificados.",
        "Sección de preguntas frecuentes y fechas fiscales importantes.",
        "Contacto directo mediante WhatsApp, correo y formularios.",
    ),
    "inmobiliaria": (
        "Catálogo de propiedades con fotografías, precios y características.",
        "Filtros por operación, ubicación, tipo de inmueble y presupuesto.",
        "Mapas, fichas detalladas y formularios para solicitar información.",
        "Contacto directo con el asesor responsable de cada propiedad.",
        "Panel de administración para publicar y actualizar inmuebles.",
    ),
    "gimnasio": (
        "Presentación de planes, precios, clases y horarios.",
        "Perfiles de entrenadores e información de instalaciones.",
        "Registro para clases de prueba o solicitud de membresía.",
        "Promociones, testimonios y resultados autorizados.",
        "SEO local y contacto directo mediante WhatsApp.",
    ),
    "belleza": (
        "Catálogo visual de servicios, tratamientos y precios.",
        "Galería profesional de resultados e instalaciones.",
        "Reservación de citas mediante formulario o WhatsApp.",
        "Promociones, paquetes y testimonios de clientes.",
        "Diseño móvil orientado a convertir visitas de redes sociales en citas.",
    ),
    "barberia": (
        "Servicios, precios y duración estimada de cada cita.",
        "Galería de cortes, estilos y trabajo realizado.",
        "Reservaciones mediante WhatsApp o formulario.",
        "Horarios, ubicación e integración con Google Maps.",
        "SEO local para búsquedas de barberías cercanas.",
    ),
    "veterinaria": (
        "Servicios médicos, preventivos, estéticos y de urgencias.",
        "Perfiles del equipo veterinario e información de instalaciones.",
        "Solicitud de citas mediante formulario o WhatsApp.",
        "Horarios, ubicación y teléfonos para atención inmediata.",
        "Contenido informativo para orientar a propietarios de mascotas.",
    ),
    "taller": (
        "Catálogo de servicios de diagnóstico, mantenimiento y reparación.",
        "Solicitud de cotizaciones y citas mediante WhatsApp.",
        "Información sobre garantías, refacciones y procesos de servicio.",
        "Ubicación, horarios e integración con Google Maps.",
        "SEO local para búsquedas de talleres y servicios automotrices.",
    ),
    "construccion": (
        "Portafolio visual de obras, remodelaciones y proyectos terminados.",
        "Descripción de servicios, procesos y áreas de especialidad.",
        "Fichas de proyectos con fotografías, alcance y resultados.",
        "Formulario para solicitar evaluación o cotización.",
        "Diseño profesional orientado a generar confianza comercial.",
    ),
    "hotel": (
        "Presentación de habitaciones, servicios, tarifas y disponibilidad.",
        "Galería profesional de instalaciones y experiencias.",
        "Solicitudes de reservación directa mediante formulario o WhatsApp.",
        "Ubicación, recomendaciones cercanas y preguntas frecuentes.",
        "SEO turístico y local para reducir la dependencia de intermediarios.",
    ),
    "tienda": (
        "Catálogo organizado con productos, fotografías, precios y variantes.",
        "Carrito de compra, pagos en línea o pedidos mediante WhatsApp.",
        "Control de inventario y administración de productos.",
        "Información de envíos, cambios, devoluciones y métodos de pago.",
        "Diseño optimizado para aumentar conversiones desde dispositivos móviles.",
    ),
    "escuela": (
        "Presentación de programas, niveles, cursos y metodología.",
        "Información de inscripciones, requisitos, costos y calendarios.",
        "Perfiles docentes, instalaciones y preguntas frecuentes.",
        "Formulario para solicitar informes o iniciar una inscripción.",
        "Diseño accesible para estudiantes y familias desde cualquier dispositivo.",
    ),
    "eventos": (
        "Presentación de paquetes, capacidades, servicios y precios.",
        "Galería profesional de eventos e instalaciones.",
        "Calendario de disponibilidad y solicitud de cotización.",
        "Ubicación, preguntas frecuentes y contacto por WhatsApp.",
        "Diseño visual orientado a convertir consultas en reservaciones.",
    ),
    "psicologia": (
        "Presentación profesional de enfoques, servicios y modalidades de consulta.",
        "Solicitud privada de citas presenciales o en línea.",
        "Preguntas frecuentes sobre el proceso terapéutico.",
        "Información de horarios, ubicación y medios de contacto.",
        "Diseño cálido, accesible y enfocado en privacidad y confianza.",
    ),
    "fotografia": (
        "Portafolio visual organizado por tipo de sesión o proyecto.",
        "Paquetes, entregables, cobertura y proceso de contratación.",
        "Solicitud de disponibilidad y cotización mediante formulario.",
        "Galerías rápidas y optimizadas sin perder calidad visual.",
        "Integración con redes sociales y contacto directo por WhatsApp.",
    ),
    "seguros": (
        "Presentación clara de pólizas, coberturas y beneficios.",
        "Comparación de opciones para facilitar la decisión del prospecto.",
        "Formularios para solicitar cotizaciones personalizadas.",
        "Preguntas frecuentes y explicación del proceso de contratación.",
        "Contacto directo con un asesor mediante WhatsApp o correo.",
    ),
}


def normalize_niche(value: str) -> str:
    key = value.strip().lower().replace(" ", "_")
    key = ALIASES.get(key, key)
    return key if key in TEMPLATES else "general"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enviar propuestas por nicho mediante Brevo")
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--to", help="Destinatario (separa varios con comas)")
    target.add_argument("--all", action="store_true", help="Usar todos los contactos de sendEmail.txt")
    parser.add_argument("--file", type=Path, default=DEFAULT_LIST)
    parser.add_argument("--niche", help="Nicho para destinatarios escritos manualmente")
    parser.add_argument("--business", default="", help="Nombre del negocio")
    parser.add_argument("--contact-name", default="", help="Nombre de la persona")
    parser.add_argument("--list-niches", action="store_true", help="Mostrar nichos disponibles")
    parser.add_argument("--from-email", default="contact@danielrdz.site")
    parser.add_argument("--from-name", default="Website Developer")
    parser.add_argument(
        "--log-file", type=Path, default=DEFAULT_LOG,
        help="Registro JSONL de envíos exitosos",
    )
    parser.add_argument(
        "--resend", action="store_true",
        help="Reenviar aunque el destinatario figure en el registro",
    )
    return parser.parse_args()


def normalize_email(value: str) -> str:
    return value.strip().lower()


def read_sent_emails(path: Path) -> set[str]:
    sent: set[str] = set()
    if not path.exists():
        return sent
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            print(
                f"Aviso: registro inválido en {path}, línea {line_number}; se ignoró.",
                file=sys.stderr,
            )
            continue
        if record.get("status") == "sent" and record.get("email"):
            sent.add(normalize_email(str(record["email"])))
    return sent


def log_success(path: Path, contact: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "sent",
        "email": normalize_email(contact["email"]),
        "niche": contact["niche"],
        "business": contact["business"],
        "contact_name": contact["contact_name"],
    }
    with path.open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_contacts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    contacts = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split("|")]
        contacts.append({
            "email": normalize_email(parts[0]),
            "niche": normalize_niche(parts[1] if len(parts) > 1 else "general"),
            "business": parts[2] if len(parts) > 2 else "",
            "contact_name": parts[3] if len(parts) > 3 else "",
        })
    return contacts


def manual_contacts(args: argparse.Namespace, addresses: list[str]) -> list[dict[str, str]]:
    niche_value = args.niche
    if not niche_value:
        print("Nichos: " + ", ".join(sorted(TEMPLATES)))
        niche_value = input("Nicho: ").strip() or "general"
    niche = normalize_niche(niche_value)
    business = args.business or input("Nombre del negocio (opcional): ").strip()
    contact_name = args.contact_name or input("Nombre del contacto (opcional): ").strip()
    return [
        {"email": email, "niche": niche, "business": business, "contact_name": contact_name}
        for email in addresses
    ]


def resolve_contacts(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.all:
        return read_contacts(args.file)
    if args.to:
        addresses = [item.strip() for item in args.to.split(",") if item.strip()]
        return manual_contacts(args, addresses)

    target = input(
        f"Destinatario (correo, varios separados por comas, o Enter para {args.file.name}): "
    ).strip()
    if not target:
        return read_contacts(args.file)
    return manual_contacts(args, [item.strip() for item in target.split(",") if item.strip()])


def render(contact: dict[str, str]) -> tuple[str, str]:
    niche = contact["niche"]
    subject_template, body_template = TEMPLATES[niche]
    business = contact["business"] or "su negocio"
    greeting = f" {contact['contact_name']}" if contact["contact_name"] else ""
    values = {"business": business, "greeting": greeting, "portfolio": PORTFOLIO_URL}
    subject = subject_template.format(**values)
    body = body_template.format(**values)

    features = NICHE_FEATURES.get(niche)
    if features:
        feature_lines = "\n".join(f"- {feature}" for feature in features)
        feature_section = (
            "La solución web puede estructurarse con funcionalidades específicas "
            "para este sector:\n\n"
            f"{feature_lines}\n\n"
        )
        portfolio_heading = "Conozca nuestro portafolio profesional y proyectos publicados:"
        body = body.replace(portfolio_heading, feature_section + portfolio_heading, 1)

    return subject, body


def make_message(args: argparse.Namespace, contact: dict[str, str]) -> EmailMessage:
    subject, body = render(contact)
    message = EmailMessage()
    message["From"] = f"{args.from_name} <{args.from_email}>"
    message["To"] = contact["email"]
    message["Subject"] = subject
    message.set_content(body)
    return message


def main() -> int:
    args = parse_args()
    if args.list_niches:
        print("\n".join(sorted(TEMPLATES)))
        return 0

    try:
        contacts = resolve_contacts(args)
    except (OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    if not contacts:
        print("Error: no hay destinatarios.", file=sys.stderr)
        return 2

    sent_emails = read_sent_emails(args.log_file)
    pending: list[dict[str, str]] = []
    seen_in_batch: set[str] = set()
    skipped = 0
    for contact in contacts:
        email = normalize_email(contact["email"])
        contact["email"] = email
        if email in seen_in_batch:
            print(f"Omitido duplicado en la lista: {email}")
            skipped += 1
            continue
        seen_in_batch.add(email)
        if not args.resend and email in sent_emails:
            print(f"Omitido; ya fue enviado anteriormente: {email}")
            skipped += 1
            continue
        pending.append(contact)

    if not pending:
        print(f"Listo: 0 enviados; {skipped} omitido(s).")
        return 0

    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_password and PASSWORD_FILE.exists():
        smtp_password = PASSWORD_FILE.read_text(encoding="utf-8").strip()
    if not smtp_password:
        print(f"Error: guarda la clave SMTP en {PASSWORD_FILE}", file=sys.stderr)
        return 2

    smtp_host = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "bde115001@smtp-brevo.com")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            smtp.login(smtp_username, smtp_password)
            sent_count = 0
            failed_count = 0
            for contact in pending:
                try:
                    smtp.send_message(make_message(args, contact))
                    log_success(args.log_file, contact)
                    sent_count += 1
                    print(
                        f"Enviado y registrado: {contact['email']} "
                        f"({contact['niche']})"
                    )
                except (OSError, smtplib.SMTPException) as error:
                    failed_count += 1
                    print(
                        f"Error al enviar a {contact['email']}: {error}",
                        file=sys.stderr,
                    )
    except (OSError, smtplib.SMTPException) as error:
        print(f"Error SMTP: {error}", file=sys.stderr)
        return 1

    print(
        f"Listo: {sent_count} enviado(s), {skipped} omitido(s), "
        f"{failed_count} fallido(s). Registro: {args.log_file}"
    )
    return 1 if failed_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
