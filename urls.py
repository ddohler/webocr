from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ocrweb/', include('ocrweb.foo.urls')),
    (r'^$', 'interface.views.main.main'),
    (r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    # Uncomment the admin/doc line below to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
