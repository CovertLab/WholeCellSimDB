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
urlpatterns += patterns('wcdb.views',    
    #home page
    url(r'^$', 'index'),
    
    #investigators
    url(r'^list/investigator/*$', 'list_investigators'),
    url(r'^investigator/(?P<id>[0-9]+)/*$', 'investigator'),
    
    #organisms
    url(r'^list/organism/*$', 'list_organisms'),
    url(r'^organism/(?P<id>[0-9]+)/*$', 'organism'),
    
    #simulations
    url(r'^list/batches/*$', 'list_simulation_batches'),
    url(r'^simulation_batch/(?P<id>[0-9]+)/*$', 'simulation_batch'),
    url(r'^simulation/(?P<id>[0-9]+)/*$', 'simulation'),
    
    #search
    url(r'^search_basic/*$', 'search_basic'),
    url(r'^search_advanced/*$', 'search_advanced'),    
    
    #documentation
    url(r'^tutorial/*$', 'tutorial'),
    url(r'^about/*$', 'about'),
    
    #sitemap
    url(r'^sitemap.xml$', 'sitemap'),
)
