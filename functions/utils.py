
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(subject, body, to_email):
    smtp_email = os.environ.get('SMTP_EMAIL')
    password = os.environ.get('SMTP_PASSWORD')

    # Imposta il server SMTP di Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Creazione del messaggio
    msg = MIMEMultipart()
    msg["From"] = "noreply@chome.it"  # Indirizzo del mittente che vuoi mostrare
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Protegge la connessione con TLS
        server.login(smtp_email, password)

        print("Sending email to:", to_email)
        
        server.sendmail("noreply@chome.it", to_email, msg.as_string())

        print("Email inviata con successo!")
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")
    finally:
        server.quit()