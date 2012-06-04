from django.db import models
from django.contrib.auth.models import User
#TODO: Change DocumentPage to DocumentImage
# Generate a filesystem path for document files to be uploaded to.
def doc_upload_path(instance=None,filename=None):
    if filename is not None and instance is not None:
        folder = instance.internal_name
        name = instance.upload_name
        return folder + "/" + name
    else:
        raise Exception("upload_path requires an instance and filename.")
# A document that has been uploaded for OCRing.
class Document(models.Model):
    owner = models.ForeignKey(User)
    doc_file = models.FileField(upload_to=doc_upload_path,max_length=255)

    upload_date = models.DateTimeField(auto_now_add=True)

    upload_name = models.CharField(max_length=220)
    internal_name = models.CharField(max_length=220)
    
    num_pages = models.IntegerField(null=True,blank=True)

    file_format = models.CharField(max_length=3, choices=(
        ('pdf', 'Adobe PDF'),
        ('tif', 'TIFF'),
        ('bmp', 'Bitmap'),
        ('jpg', 'JPEG'),
        ('png', 'PNG'),
        ('unk', 'Unknown'),
    ))
    color_depth = models.CharField(max_length=1, choices=(
        ('g', 'Grayscale'),
        ('c', 'Color'), # For our purposes, number of bits is irrelevant
        ('b', 'Black and white'),
        ('u', 'Unknown'),
    ))

# Generate a filesystem path for document files to be uploaded to.
#TODO: Create a custom field 
# that acts the same way as the FileField, but which isn't oriented
# toward uploaded files, or figure out a way to use the existing one better.
def page_upload_path(instance=None,filename=None):
    if filename is not None and instance is not None:
        doc = Document.objects.get(pk=instance.document.pk)
        return doc.internal_name + "/pages/" + str(instance.page_number) + filename[-4:]
    else:
        raise Exception("upload path requires instance and filename.")

#Instances should always be generated programmatically
class DocumentPage(models.Model):
    document = models.ForeignKey(Document)

    #page_file = models.FileField(upload_to=page_upload_path,max_length=255)
    files_prefix = models.CharField(blank=True,max_length=255)
    #The file extension for the most recent stage's output.
    stage_output_extension = models.CharField(blank=True,max_length=32)
    #This page's number within document. Zero-indexed
    page_number = models.IntegerField()

    #Dates and times when processing was started, finished.
    start_process_date = models.DateTimeField(null=True,blank=True)
    finish_process_date = models.DateTimeField(null=True,blank=True)
# TODO: Move time reporting into general pipeline class
# TODO: Move status reporting into general pipeline class
# TODO: Can I programmatically access celery's time measurement?
    is_convert_done = models.BooleanField(default=False)
    convert_time = models.FloatField(default=0.0)

    is_binarize_done = models.BooleanField(default=False)
    binarize_time = models.FloatField(default=0.0)

    is_recognize_done = models.BooleanField(default=False)
    recognize_time = models.FloatField(default=0.0)
# TODO: Handle status in pipeline class
    status = models.CharField(max_length=1, choices=(
        ('w', 'Waiting for processing'),
        ('c', 'Conversion in progress'),
        ('b', 'Binarization in progress'),
        ('r', 'Recognition in progress'),
        ('f', 'Finished successfully'),
        ('e', 'Error')),
        default='w')

    text = models.TextField(blank=True,verbose_name='OCR output')

# Class to store job information collected from pages
# This class should usually be updated synchronously, it converts
# asynchronously generated page information into synchronous
# information about the status of the job as a whole.
class DocumentOCRJob(models.Model):
    document = models.ForeignKey(Document)
    is_finished = models.BooleanField(default=False)
    processed_pages = models.IntegerField(default=0)

    time_so_far = models.FloatField(default=0)

#TODO: This is going to change a lot once I add generalized
# pipeline stages; then it will calculate time based on stages
# rather than pages, which will be more granular and provide
# quicker updates
    def estimate_time():
        if processed_pages != 0:
            return (self.time_so_far / self.processed_pages)*(self.document.num_pages - self.processed_pages)
        else:
            return -1
