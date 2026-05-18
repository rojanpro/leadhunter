
import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.core.config import get_settings
from app.services.emailer import EmailClient
from app.services.evolution import EvolutionClient

settings = get_settings()
print(f'SMTP HOST: {settings.smtp_host}')
print(f'SMTP USER: {settings.smtp_user}')
print(f'SMTP PASS: {settings.smtp_password}')
print(f'SMTP FROM: {settings.smtp_from_email}')

async def test_all():
    print('Testing Email...')
    try:
        email_client = EmailClient()
        email_id = email_client.send_email(
            to_email='99fyre@gmail.com',
            subject='Test Email from LeadHunter',
            body='This is a test email.'
        )
        print(f'Email sent successfully! ID: {email_id}')
    except Exception as e:
        print(f'Failed to send email: {e}')

    print('\nTesting WhatsApp...')
    try:
        wa_client = EvolutionClient()
        exists = await wa_client.check_whatsapp_number('+9779823304013')
        if exists:
            msg_id = await wa_client.send_whatsapp_message(
                '+9779823304013',
                'Test message'
            )
            print(f'WhatsApp message sent successfully! ID: {msg_id}')
        else:
            print('WhatsApp number not registered on WhatsApp according to Evolution API.')
    except Exception as e:
        print(f'Failed to send WhatsApp message: {e}')

if __name__ == '__main__':
    asyncio.run(test_all())

