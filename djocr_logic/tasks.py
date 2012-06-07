#TODO: Switch to celery logging
#TODO: Generate ErrorMessages
#TODO: Detect image resolution
#TODO: Add time tracking
from celery.task import task
from django.core.files import File
from models import Document, DocumentPage, DocumentOCRJob
import magic # Python wrapper for libmagic
import os, subprocess
from time import time
from datetime import datetime 
import shutil
import codecs

from util import mime_to_fmt
from settings import MEDIA_ROOT, PAGES_FOLDER

#TODO: Figure out returns and error codes
#TODO: Refactor to use folder / file storage instead of
# inserting the page number everywhere.
def is_valid_doc(docid):
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

@task
def determine_format(docid):
    #TODO: Check for multiple objects?
    doc = is_valid_doc(docid)
    
    m = magic.Magic(mime=True)
    doc.doc_file.open(mode='rb')
    #TODO: Make sure reading first 1024 bytes is enough
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
    print "Splitting document..."
    #TODO: Consider splitting to multi-page TIFF so tesseract can learn
    page_files = split_to_files(doc)
    
    #TODO: Add intelligence here for PDFs in case num imgs != num pages
    #TODO: Detect PDFs with embedded text (which will be discarded)
    #      and raise a warning.
    doc.num_pages = len(page_files)
    doc.save()
    
    # Creates DocumentPages for each file returned by
    # split function, then launches conversion, etc.
    # tasks for each DocumentPage.
    for i in range(doc.num_pages):
        doc_page = DocumentPage(document=doc,
                files_prefix=page_files[i][0],
                stage_output_extension=page_files[i][1],
                page_number=i,
                start_process_date=datetime.now(),
                status='w')
        doc_page.save()

        convert_page.delay(doc_page)

#TODO: Make this extensible so we can build in other analysis easily
#TODO: Improve both Tesseract and OCRopus usage
@task
def convert_page(page):
    print "Convert page "+str(page.page_number)+"!"
    start = time()
    page.status='c'
    page.save()

    cmd = ['mogrify', '-density', '300', '-format', 'png', '-path']
    cmd.append(page.files_prefix)
    cmd.append(page.files_prefix+page.stage_output_extension)
    #print ''.join(cmd)
    try:
        subprocess.check_call(cmd)
        #raise subprocess.CalledProcessError(cmd="command", returncode=2)
    except subprocess.CalledProcessError as e:
        print(e)
        handle_error(page)
    
    page.stage_output_extension = page.stage_output_extension[:-3]+'png'
    page.is_convert_done = True
    page.convert_time = time() - start
    page.save()
    print "Done converting page "+str(page.page_number)
    binarize_page.delay(page)

@task
def binarize_page(page):
    print "Binarize page "+str(page.page_number)+"!"
    start = time()
    page.status = 'b'
    page.save()

    cmd = ['ocropus-binarize', '-o', page.files_prefix+str(page.page_number)]
    cmd.append(page.files_prefix+page.stage_output_extension)
    #print ''.join(cmd)
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(e)
        handle_error(page)

    page.files_prefix = page.files_prefix+str(page.page_number)+"/"
    page.stage_output_extension = '0001.bin.png'
    page.is_binarize_done = True
    page.binarize_time = time() - start
    page.save()
    print "Done binarizing page "+str(page.page_number)

    recognize_page.delay(page)

@task
def recognize_page(page):
    print "Recognize page "+str(page.page_number)+"!"
    start = time()
    page.status = 'r'
    page.save()
    
    cmd = ['tesseract', page.files_prefix+page.stage_output_extension]
    cmd += [page.files_prefix+str(page.page_number),'-l','kat']
    #print ''.join(cmd)
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(e)
        handle_error(page)

    page.is_recognize_done = True
# Read text file output, store in database
# Maybe split this into its own task?
    page.stage_output_extension = str(page.page_number)+'.txt'
    page.recognize_time = time() - start
    
    page.status = 'f'
    txt_file_path = page.files_prefix+str(page.page_number)+'.txt'
    txt_file = codecs.open(txt_file_path,encoding='utf-8')
    page.text = txt_file.read()
    page.save()

    finish_page.delay(page)

#FIFO - Only one worker should deal with this, otherwise potential race condition.
@task
def finish_page(page):
    job = DocumentOCRJob.objects.get(document=page.document)
    job.processed_pages += 1
    
    #print "%d:%d" %(job.processed_pages,page.document.num_pages)
    if job.processed_pages == page.document.num_pages:
        job.is_finished = True

    job.time_so_far += page.convert_time + page.binarize_time + page.recognize_time
    job.save()
    page.finish_process_date = datetime.now()
    page.save()
    print "Done!"

# Super basic error handling. If error occurred, store to job instance.
# Probably will go away later once pipeline is implemented.
def handle_error(page):
    job = DocumentOCRJob.objects.get(document=page.document)

    job.had_error = True
    job.save()

#FIFO
#TODO
@task
def update_job_time(page):
    pass
    #job = DocumentOCRJob.objects.get(document=page.document)
    #job.time_so_far = t
    #job.save()

#TODO: Protections so this doesn't destroy the file system.
@task
def clean_doc_files(path):
    """Currently, simply deletes an entire folder structure starting with path."""
    cmd = ["rm", "-rf", MEDIA_ROOT+path]
    #print cmd
    subprocess.check_call(cmd)

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
        shutil.copy(str(doc.doc_file), prefix+'0.'+doc.file_format)
        page_files.append((prefix,'0.'+doc.file_format))

    return page_files
