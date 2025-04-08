import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
import os
from jinja2 import Template

# Cargar variables de entorno
load_dotenv()

EMAIL_USER = os.getenv("MAIL_USERNAME")
EMAIL_PASS = os.getenv("MAIL_PASSWORD")


def render_template(template_name: str, context: dict) -> str:
    """
    Renderiza una plantilla HTML con Jinja2.
    """
    template_path = Path(__file__).parent.parent / "resources" / "templates" / template_name
    template_content = template_path.read_text(encoding="utf-8")
    template = Template(template_content)
    return template.render(context)


def send_email(recipient: str, subject: str, context: dict, template: str):
    """
    Envía un correo electrónico con una plantilla HTML.
    """
    # Renderizar la plantilla
    html_content = render_template(template, context)

    # Configurar el mensaje
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_USER
    message["To"] = recipient
    message["Subject"] = subject

    # Agregar el contenido HTML
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # Conectar al servidor de Gmail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, recipient, message.as_string())