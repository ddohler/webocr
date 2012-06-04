from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from djocr_logic.views import main, documents

#TODO: Make sure these patterns are okay, I have a feeling they suck
#TODO: Does login/logout really need to be this complicated?
urlpatterns = patterns('',
    # Example:
    # (r'^ocrweb/', include('ocrweb.foo.urls')),
    (r'^$', main.main),
    url(r'^documents/$', documents.main,name="documents"),
    #Todo It might be better to do these as a Form with GET, not sure
    (r'^documents/getdoc/([a-f0-9-]+)/', documents.get_doc),
    (r'^documents/delete/([a-f0-9-]+)/', documents.delete),
    (r'^documents/gettext/([a-f0-9-]+)/',documents.get_text),
    url(r'^login/', login, {'template_name': 'login.html'},name="login"),
    url(r'^logout/', logout, {'next_page': '/'}, name="logout"),
    # Uncomment the admin/doc line below to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
