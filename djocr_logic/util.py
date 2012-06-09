from settings import MEDIA_ROOT, PAGES_FOLDER
from models import Document, DocumentPage, DocumentOCRJob

import magic
import pyPdf
import os, subprocess, shutil
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
        from djocr_logic.models import Document #TODO: Does this work?
        doc = Document.objects.get(pk=instance.document)
        return doc.internal_name + "/pages/" + filename

def is_valid_doc(docid):
    """Checks to see if a document id is valid within the db"""
    if docid is not None:
        doc = Document.objects.get(pk=docid)

        if doc is None:
            pass
            #TODO: Error
        else:
            return doc
    else:
        pass
        #TODO: Error

def determine_format(doc):
    """Uses libmagic to determine file format"""
    m = magic.Magic(mime=True)
    doc.doc_file.open(mode='rb')
    #TODO: Make sure reading first 1024 bytes is enough
    mime = m.from_buffer(doc.doc_file.read(1024))
    doc.doc_file.close()
    try:
        #TODO: Why bother? Just use mime-type directly.
        fmt = mime_to_fmt[mime] # Lookup table
    except KeyError:
        fmt = 'unk'

    return fmt

def count_pages(doc):
    """Count the number of pages in the document's source file."""
    num_pages = -1
    if doc.file_format not in ('pdf','tif'): # single-image format
        num_pages = 1
    else:
        if doc.file_format == 'tif':
            pass
            #TODO: Multipage TIFF support
        else:
            doc.doc_file.open(mode='rb')
            try:
                pdf_doc = pyPdf.PdfFileReader(doc.doc_file)
                num_pages = pdf_doc.getNumPages()
            except AssertionError:
                pass # Return -1 if number cannot be determined

    return num_pages

def count_images(doc):
    """Counts embedded images in a PDF document."""
    cmd = ['pdfimages','-list',MEDIA_ROOT+str(doc.doc_file)]
    child = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out,err) = child.communicate()

    num_imgs = -1
    if len(err) == 0:
        num_imgs = len(out.split('\n'))-3 # 2 header lines, 1 blank at end

    return num_imgs

def detect_text(doc):
    """Checks to see if a PDF has embedded text."""
    try:
        doc.doc_file.open(mode='rb')
        pdf_doc = pyPdf.PdfFileReader(doc.doc_file)
        txt = [pg.extractText() for pg in pdf_doc.pages]
        # Strip empty entries
        for t in txt:
            if len(t) == 0:
                txt.remove(t)
        if len(txt) > 0:
            has_text = True
        else:
            has_text = False
    except AssertionError:
        has_text = None
    return has_text

#Split multi-page files into one file per page, return paths
#as a list of (folder,file) pairs. [(folder,f1),...]
def split_to_files(doc, folder=None):
    if folder == None:
        folder = MEDIA_ROOT + doc.internal_name + "/" + PAGES_FOLDER
        os.mkdir(folder) #TODO: Check for pre-existing directory

    page_files = []
    #doc.doc_file.open(mode="rb")
    
    if doc.file_format == 'pdf':
        cmd = ['pdfimages',doc.doc_file.path,folder]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print(e)
            handle_error(page)

        files = os.listdir(folder)
        files.sort()
        page_files = [(folder,f) for f in files]

    elif doc.file_format == 'tif':
        #TODO: Split a multi-page tiff. Don't feel like messing with PIL atm
        pass
    else: #Guaranteed single-page formats
        prefix = folder
        #print "Prefix: " + str(prefix)
        #print "MEDIA_ROOT+File: " + MEDIA_ROOT + str(doc.doc_file)
        shutil.copy(MEDIA_ROOT+str(doc.doc_file), prefix+'0.'+doc.file_format)
        page_files.append((prefix,'0.'+doc.file_format))

    return page_files

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
