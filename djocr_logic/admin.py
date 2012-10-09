from django.contrib import admin
from djocr_logic.models import Document, DocumentPage, DocumentOCRJob

class DocumentAdmin(admin.ModelAdmin):
    pass

class DocumentOCRJobAdmin(admin.ModelAdmin):
    pass

class DocumentPageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentOCRJob, DocumentOCRJobAdmin)
admin.site.register(DocumentPage, DocumentPageAdmin)
