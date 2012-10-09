from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from djocr_logic.models import Document,DocumentPage,DocumentOCRJob
from djocr_logic.util import fmt_to_mime
from djocr_logic.tasks import clean_doc_files

@login_required
def main(request):
    all_jobs = DocumentOCRJob.objects.filter(document__owner=request.user)

    return render_to_response('documents.html', RequestContext(request, {
        'jobs': all_jobs,
    }))
    #TODO: I'm really not sure that using the internal id is the best
    # way to do this.
@login_required
def get_doc(request,internal_id):
    user_docs = Document.objects.filter(owner=request.user)
    doc = get_object_or_404(user_docs, internal_name=internal_id)

    #TODO: switch to django-private-files or xsendfiles or similar
    #TODO: Test security
    response = HttpResponse(mimetype=fmt_to_mime[doc.file_format])
    response['Content-Disposition'] = 'attachment; filename='+doc.upload_name
    f = doc.doc_file
    f.open(mode='rb')
    response.write(f.read())

    return response

@login_required
def get_text(request,internal_id):
    user_docs = Document.objects.filter(owner=request.user)
    doc = get_object_or_404(user_docs, internal_name=internal_id)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition']='attachment; filename='+doc.upload_name[:-3]+'txt'
    
    doc_pages = DocumentPage.objects.filter(document=doc).order_by('page_number')
    for p in doc_pages:
        response.write(p.text)

    return response
    

@login_required
def delete(request,internal_id):
    user_docs = Document.objects.filter(owner=request.user)
    doc = get_object_or_404(user_docs, internal_name=internal_id)

    doc.doc_file.delete()
    folder = doc.internal_name
    doc.delete()

    clean_doc_files.delay(folder)

    return HttpResponseRedirect('/documents/')
