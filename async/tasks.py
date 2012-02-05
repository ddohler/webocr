from celery.task import task
from django.core.files import File
from interface.models import Document, DocumentPage
from pyPdf import PdfFileWriter, PdfFileReader
import magic # Python wrapper for libmagic
import os, subprocess
from time import clock
from datetime import datetime 
import shutil

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
    #Todo: Check for multiple objects?
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

    doc_to_pages.delay(docid)

@task
def doc_to_pages(docid):
    doc = is_valid_doc(docid)

    page_file_prefixes = split_to_files(doc)
    
    doc.num_pages = len(page_file_prefixes)
    doc.save()
    
    # Creates DocumentPages for each file returned by
    # split function, then launches conversion, etc.
    # tasks for each DocumentPage.
    for i in range(doc.num_pages):
        doc_page = DocumentPage(document=doc,
                files_prefix=page_file_prefixes[i],
                stage_output_extension=doc.file_format,
                page_number=i,
                start_process_date=datetime.now(),
                status='w')
        doc_page.save()
        convert_page.delay(doc_page)

#Todo: Make this extensible so we can build in other analysis easily
@task
def convert_page(page):
    print "Convert page "+str(page.page_number)+"!"
    start = clock()

    cmd = ['mogrify', '-density', '300', '-format', 'png', '-path']
    cmd.append(page.files_prefix)
    cmd.append(page.files_prefix+str(page.page_number)+'.'+page.stage_output_extension)
    print ''.join(cmd)
    subprocess.call(cmd)
    
    page.stage_output_extension = 'png'
    page.convert_time = clock() - start
    page.save()
    print "Done converting page "+str(page.page_number)
    binarize_page.delay(page)

#TODO
@task
def binarize_page(page):
    print "Binarize page "+str(page.page_number)+"!"
    recognize_page.delay(page)

#TODO
@task
def recognize_page(page):
    print "Recognize page "+str(page.page_number)+"!"
    print "Done!"

#Split multi-page files into one file per page, return paths
#This must NOT output files in a format that are different than
#the document format.
def split_to_files(doc, folder=None):
    if folder == None:
        folder = MEDIA_ROOT + doc.internal_name + "/" + PAGES_FOLDER
        os.mkdir(folder) #Todo: Check for pre-existing directory

    page_prefixes = []
    doc.doc_file.open(mode="rb")

    if doc.file_format == 'pdf':
        iPdf = PdfFileReader(doc.doc_file)

        for i in range(iPdf.getNumPages()):
            oPdf = PdfFileWriter()
            oPdf.addPage(iPdf.getPage(i))
            file_path = ''.join([folder,str(i),'.pdf'])
            oPdf.write(file(file_path,'w'))

            page_prefixes.append(folder)

    elif doc.file_format == 'tif':
        #TODO: Split a multi-page tiff. Don't feel like messing with PIL atm
        pass
    else: #Guaranteed single-page formats
        prefix = folder
        shutil.copy(str(doc.doc_file), prefix+'0.'+doc.file_format)
        page_prefixes.append(prefix)

    return page_prefixes
