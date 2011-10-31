from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ocrweb/', include('ocrweb.foo.urls')),
    (r'^$', 'interface.views.main.main'),
    url(r'^login$', login, {'template_name': 'login.html'},name="login"),
    url(r'^logout$', logout, {'next_page': '/'}, name="logout"),
    # Uncomment the admin/doc line below to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
