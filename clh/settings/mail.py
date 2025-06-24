#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "clh.test.vlt@gmail.com"
EMAIL_HOST_PASSWORD = "uoqojfyrdcchathu"  

EMAIL_SENDER_NAME = "Coperate Legal Hub"

# Email Header Configuration
EMAIL_CUSTOM_HEADER = {
    "text": (
        "Email sent by Coperate Legal Hub (CLH)<br>"
        "Hotline: +94 7711111111<br>"
        "Email: contact@clh.com"
    ),
    "style": "font-size: 12px; color: #555; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 10px;"
}


#When mail is disabled (set to false), emails won't be sent except for password reset.
ENABLE_EMAIL = True

