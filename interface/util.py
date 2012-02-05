# TODO: Merge with models.py to avoid circular import
# Generate a filesystem path for files to be uploaded to.
def doc_upload_path(instance=None,filename=None):
    if filename is not None and instance is not None:
        folder = instance.internal_name
        name = instance.upload_name
        return folder + "/" + name
    else:
        raise Exception("upload_path requires an instance and filename.")

def page_upload_path(instance=None,filename=None):
    if filename is not None and instance is not None:
        from interface.models import Document #TODO: Does this work?
        doc = Document.objects.get(pk=instance.document)
        return doc.internal_name + "/pages/" + filename

# Lookup tables between internal format codes and mime types
mime_to_fmt = {
    "application/pdf": "pdf",
    "image/tiff":"tif",
    "image/jpeg":"jpg",
    "image/png":"png",
    "image/gif":"gif",
    "image/bmp":"bmp",
}

fmt_to_mime = {
    "pdf": "application/pdf",
    "tif": "image/tiff",
    "jpg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
}
