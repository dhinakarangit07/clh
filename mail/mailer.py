# mailer.py
import threading
import re
import os
from wagtail.images.models import Image
from wagtail.documents.models import Document
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication





def process_rich_text_attachments(rich_text_content):
    """Process embeds (images) and links (documents) in RichTextField and prepare attachments"""
    html_content = str(rich_text_content)
    attachments = []

    # Process embedded images
    embed_pattern = r'<embed[^>]+embedtype="image"[^>]+id="(\d+)"[^>]*>'
    embed_matches = re.finditer(embed_pattern, html_content)

    for match in embed_matches:
        image_id = match.group(1)
        try:
            wagtail_image = Image.objects.get(id=image_id)
            image_path = wagtail_image.file.path
            if os.path.exists(image_path):
                cid = f"image_{image_id}"
                with open(image_path, 'rb') as f:
                    image_content = f.read()
                mime_type = (
                    'image/jpeg' if wagtail_image.filename.lower().endswith(('.jpg', '.jpeg'))
                    else 'image/png'
                )
                attachments.append({
                    'type': 'image',
                    'filename': wagtail_image.filename,
                    'content': image_content,
                    'mime_type': mime_type,
                    'cid': cid
                })
                html_content = html_content.replace(
                    match.group(0),
                    f'<img src="cid:{cid}" alt="{wagtail_image.title}">'
                )
        except Image.DoesNotExist:
            continue

    # Process document links
    doc_pattern = r'<a[^>]+linktype="document"[^>]+id="(\d+)"[^>]*>(.*?)</a>'
    doc_matches = re.finditer(doc_pattern, html_content)

    for match in doc_matches:
        doc_id = match.group(1)
        doc_title = match.group(2)
        try:
            wagtail_doc = Document.objects.get(id=doc_id)
            doc_path = wagtail_doc.file.path
            if os.path.exists(doc_path):
                with open(doc_path, 'rb') as f:
                    doc_content = f.read()
                mime_type = (
                    'application/pdf' if wagtail_doc.filename.lower().endswith('.pdf')
                    else 'application/octet-stream'
                )
                attachments.append({
                    'type': 'document',
                    'filename': wagtail_doc.filename,
                    'content': doc_content,
                    'mime_type': mime_type,
                    'cid': None
                })
        except Document.DoesNotExist:
            continue

    return html_content, attachments










def send_email(subject, rich_text_content,use_thread=False, **kwargs):
    """Send an email with rich text content, custom header, and attachments."""
    if not settings.ENABLE_EMAIL:
        return
    
    def send():

        try:
            # Process HTML content and extract attachments
            html_message, attachments = process_rich_text_attachments(rich_text_content)
            plain_message = strip_tags(html_message)

            # Prepare custom header
            header_text = settings.EMAIL_CUSTOM_HEADER.get("text", "")
            header_style = settings.EMAIL_CUSTOM_HEADER.get("style", "")

            # Final HTML content with header
            full_html = f"""<!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><title>{subject}</title></head>
            <body>
                <div style="{header_style}">{header_text}</div>
                {html_message}
            </body>
            </html>"""

            # Recipients
            to_list = list(kwargs.get('to', []))
            bcc_list = list(kwargs.get('bcc', []))
            cc_list = list(kwargs.get('cc', []))

            # Construct email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_SENDER_NAME,
                to=to_list,
                bcc=bcc_list,
                cc=cc_list
            )
            email.attach_alternative(full_html, "text/html")
            email.mixed_subtype = 'related'
            email.extra_headers['X-Custom-Header'] = "Email sent by CLH"

            # Attach files
            for attachment in attachments:
                content = attachment['content']
                filename = attachment['filename']
                mime_subtype = attachment['mime_type'].split('/')[1]

                if attachment['type'] == 'image':
                    img = MIMEImage(content, _subtype=mime_subtype)
                    img.add_header('Content-ID', f"<{attachment['cid']}>")
                    img.add_header('Content-Disposition', 'inline', filename=filename)
                    email.attach(img)

                elif attachment['type'] == 'document':
                    doc = MIMEApplication(content, _subtype=mime_subtype)
                    doc.add_header('Content-Disposition', 'attachment', filename=filename)
                    email.attach(doc)

            # Send the email
            email.send(fail_silently=False)

        except Exception as e:
            print(f"Error sending email: {e}")
    
    if use_thread:
        thread = threading.Thread(target=send)
        thread.start()
    else:
        send()
