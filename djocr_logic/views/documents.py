from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from djocr_logic.models import Document,DocumentPage
from djocr_logic.util import fmt_to_mime

@login_required
def main(request):
    all_docs = Document.objects.filter(owner=request.user)

    return render_to_response('documents.html', RequestContext(request, {
        'docs': all_docs,
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

    #Todo: Figure out how to delete the folders too.
    doc.doc_file.delete()
    doc.delete()

    return HttpResponseRedirect('/documents/')
