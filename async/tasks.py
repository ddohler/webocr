from celery.decorators import task
from interface.models import Document
import magic # Python wrapper for libmagic

from interface.util import mime_to_fmt

#Todo: Figure out returns and error codes
#Todo: refactor interface to doc_manager or something

@task()
def determine_format(docid):
    if docid is not None:
        doc = Document.objects.get(pk=docid)

        if doc is None:
            pass
            #Todo: Return error
        else:
            # Determine filetype, using headers 
            # as detected by libmagic (not perfect)
            m = magic.Magic(mime=True)
            doc.doc_file.open(mode='rb')
            mime = m.from_buffer(doc.doc_file)
            fmt = mime_to_fmt[mime] # Lookup table

            doc.file_format = fmt
            doc.save()
