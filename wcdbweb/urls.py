from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Admin including documentation
urlpatterns = patterns('',
    # Documentation
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Admin
    url(r'^admin/', include(admin.site.urls)),    
)

# Main WholeCellDB web app
urlpatterns += patterns('wcdbweb.views',    
    #home page
    url(r'^$', 'index'),
    
    #browse
    url(r'^list_batches$', 'list_batches'),
    
    #documentation
    url(r'^tutorial$', 'tutorial'),
    url(r'^about$', 'about'),
)
