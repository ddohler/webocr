from celery.task import task
from interface.models import Document
from pyPdf import PdfFileWriter, PdfFileReader
import magic # Python wrapper for libmagic
import os

from interface.util import mime_to_fmt
from settings import MEDIA_ROOT, PAGES_FOLDER

#Todo: Figure out returns and error codes
#Todo: refactor interface to doc_manager or something

def is_valid_doc(docid):
    if docid is not None:
        doc = Document.objects.get(pk=docid)

        if doc is None:
            pass
            #Todo: Error
        else:
            return doc
    else:
        pass
        #Todo: Error

@task
def determine_format(docid):
    doc = is_valid_doc(docid)
    
    m = magic.Magic(mime=True)
    doc.doc_file.open(mode='rb')
    #Todo: Make sure reading first 1024 bytes is enough
    mime = m.from_buffer(doc.doc_file.read(1024))
    doc.doc_file.close()
    try:
        fmt = mime_to_fmt[mime] # Lookup table
    except KeyError:
        fmt = 'unk'

    doc.file_format = fmt
    doc.save()

    doc_to_png.delay(docid)

@task
def doc_to_png(docid):
    doc = is_valid_doc(docid)

    if doc.file_format == 'pdf':
        split_pdf(doc)
        pdfs_to_png(doc)
    elif doc.file_format == 'tif':
        split_tif(doc)
        img_to_png(doc)

def split_pdf(doc, folder=None):
    if folder == None:
        folder = MEDIA_ROOT + doc.internal_name + "/" + PAGES_FOLDER
        os.mkdir(folder) #Todo: Check for pre-existing directory

    doc.doc_file.open(mode="rb")
    iPdf = PdfFileReader(doc.doc_file)
    
    for i in range(iPdf.getNumPages()):
        oPdf = PdfFileWriter()
        oPdf.addPage(iPdf.getPage(i))
        oPdf.write(file(''.join([folder,str(i),".pdf"]),"w"))

#Uses ImageMagick to convert PDFs to PNG
def pdfs_to_png(doc, pdf_loc=None):
    if pdf_loc == None:
       pdf_loc = MEDIA_ROOT + doc.internal_name + "/" + PAGES_FOLDER

    png_loc = pdf_loc + "png/"
    os.mkdir(png_loc) #Todo: Check for pre-existing directory

    pdf_files = os.listdir(pdf_loc)
    for s in pdf_files:
        if s[-3:] == 'pdf':
            cmd = 'mogrify -density 300 -format png -path '+png_loc
            cmd += ' '+pdf_loc + s
            print cmd
            os.system(cmd)

#Todo
def split_tif(doc):
    pass

#Todo
def img_to_png(doc):
    pass
