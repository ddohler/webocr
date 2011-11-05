from django.db import models
from django.contrib.auth.models import User
from interface.util import upload_path

# A document that has been uploaded for OCRing.
class Document(models.Model):
    owner = models.ForeignKey(User)
    doc_file = models.FileField(upload_to=upload_path,max_length=255)

    upload_date = models.DateTimeField(auto_now_add=True)
    start_ocr_date = models.DateTimeField(null=True)
    finish_ocr_date = models.DateTimeField(null=True)

    upload_name = models.CharField(max_length=220)
#Todo: Make sure this gets populated upon creation
    internal_name = models.CharField(max_length=220)
    
    num_pages = models.IntegerField()

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

    # Todo:
# Finish models
# Figure out how file uploads are handled
# Run initial South migration

class OCRJob(models.Model):
    document = models.ForeignKey(Document)
    status = models.CharField(max_length=1, choices=(
        ('w', 'Waiting to be processed'),
        ('p', 'Processing'),
        ('e', 'Error'),
        ('c', 'Completed'),
    ))

    conv_cost = models.IntegerField(null=True) # File format conversion cost
    bw_cost = models.IntegerField(null=True) # B&W conversion cost
    ocr_cost = models.IntegerField(null=True) # OCR computation cost

    error_text = models.CharField(max_length=255,blank=True)
# This next field may eventually contain hOCR
    text = models.TextField(blank=True,verbose_name='OCR output')
