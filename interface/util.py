import uuid

# Generate a filesystem path for files to be uploaded to.
def upload_path(instance=None,filename=None):
    if filename not None and instance not None:
        folder = instance.internal_name
        name = instance.upload_name
        return folder + "/" + name
    else:
        raise Exception("upload_path requires an instance and filename.")
