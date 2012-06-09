#TODO: Switch to celery logging
#TODO: Generate ErrorMessages
#TODO: Detect image resolution
from celery.task import task
from django.core.files import File
from models import Document, DocumentPage, DocumentOCRJob
import magic # Python wrapper for libmagic
import os, subprocess
from time import time
from datetime import datetime 
import shutil
import codecs

import util
from settings import MEDIA_ROOT, PAGES_FOLDER

#TODO: Figure out returns and error codes
#TODO: Refactor to use folder / file storage instead of
# inserting the page number everywhere.
@task
def document_analysis(docid):
    #TODO: Check for multiple objects?
    doc = util.is_valid_doc(docid)
    
    doc.file_format = util.determine_format(doc)
    ### Counting pages and repairing damaged documents ###
    num_pages = util.count_pages(doc)
    #TODO: The repair command doesn't quite work; need to make a copy first
    # or update the object's field.
    #if num_pages == -1 and doc.file_format == 'pdf':
        # Try to repair damaged PDF
    #    cmd = ['pdftk', MEDIA_ROOT+doc.doc_file, 'output', MEDIA_ROOT+doc.doc_file]
    #    try:
    #        subprocess.check_call(cmd)
    #    except subprocess.CalledProcessError as e:
    #        print(e)
            #TODO: More error handling if necessary

        #Try again
    #    num_pages = util.count_pages(doc)
        #If it's still undetectable there's not much more we can do
        #TODO: Report error, image cannot be processed.

    if doc.file_format == 'pdf':
        num_imgs = util.count_images(doc)
        has_text = util.detect_text(doc)
    else:
        num_imgs = num_pages #For TIFFS num_pages might be >1
        has_text = False

    # Decide what to do
    if has_text == False and num_imgs == num_pages: #Simple case
        #print "Pages: %d, Images: %d, Text: %d" %(num_pages,num_imgs,has_text)
        doc_to_pages.delay(docid)
    elif has_text == True and num_imgs == 0: #Nothing to OCR
        #print "Pages: %d, Images: %d, Text: %d" %(num_pages,num_imgs,has_text)
        pass #Output text directly
    elif has_text == True and num_imgs > 0: #Mixed image / text
        #print "Pages: %d, Images: %d, Text: %d" %(num_pages,num_imgs,has_text)
        pass #For now, rasterize pages, then OCR
    else: #Fallback to rasterization
        #print "Pages: %d, Images: %d, Text: %d" %(num_pages,num_imgs,has_text)
        pass #rasterize and OCR

    doc.num_pages = num_pages
    doc.save()

@task
def doc_to_pages(docid):
    doc = util.is_valid_doc(docid)
    print "Splitting document..."
    #TODO: Consider splitting to multi-page TIFF so tesseract can learn
    
    page_files = util.split_to_files(doc)
    
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
