from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

import uuid

from djocr_logic.forms import DocumentForm
from djocr_logic.models import Document, DocumentOCRJob

from djocr_logic.tasks import document_analysis

@login_required
def main(request):
    if request.method == 'POST': # Standard Django form pattern
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            #Create a skeleton Document instance with owner
            # Todo: Validation
            # Todo: Handle multiple files / provide batch
            d = Document(owner=request.user)

            #Create random name for unique internal filename
            d.internal_name = str(uuid.uuid4())
            
            # Dictionary name comes from form input name.
            d.upload_name = request.FILES['upload_file'].name
            d.doc_file = request.FILES['upload_file']
            d.file_format='unk'
            d.color_depth='u'

            d.save()
            
            j = DocumentOCRJob(document=d)
            j.save()

            document_analysis.delay(d.pk)

            return HttpResponseRedirect('/documents')
    else:
        form = DocumentForm()

    return render_to_response('main.html', RequestContext(request, {
        'form': form,
    }))
