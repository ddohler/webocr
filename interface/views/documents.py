from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from interface.models import Document

@login_required
def main(request):
    all_docs = Document.objects.filter(owner=request.user)

    return render_to_response('documents.html', RequestContext(request, {
        'docs': all_docs,
    }))

@login_required
def get_doc(request,internal_id):
    user_docs = Document.objects.filter(owner=request.user)
    doc = get_object_or_404(user_docs, internal_name=internal_id)

    #Todo: set mimetype from doc data (gotta determine it, first)
    #Todo: switch to django-private-files or xsendfiles or similar
    #Todo: Test security
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+doc.upload_name
    f = doc.doc_file
    f.open(mode='rb')
    response.write(f.read())

    return response
