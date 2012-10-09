This is a django app which provides a web-based interface to run OCR on
uploaded documents. OCR and image processing are handled asynchronously
via Celery. 

An incomplete list of major dependencies:
- Django
- Celery
- django-celery
- poppler >= 0.19.0
- tesseract
- ocropus

Very much a work-in-progress.
