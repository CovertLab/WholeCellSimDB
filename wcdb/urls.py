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
    url(r'^investigator/*$', 'list_investigators'),
    url(r'^investigator/(?P<id>[0-9]+)/*$', 'investigator'),
    
    #organisms
    url(r'^organism/*$', 'list_organisms'),
    url(r'^organism/(?P<id>[0-9]+)/*$', 'organism'),

    #organism versions
    url(r'^organism_version/*$', 'list_organism_versions'),
    url(r'^organism_version/(?P<id>[0-9]+)/*$', 'organism_version'),

    #simulation batches
    url(r'^batches/*$', 'list_simulation_batches'),
    url(r'^batches/(?P<id>[0-9]+)/*$', 'simulation_batch'),

    #simulations
    url(r'^simulations/$', 'list_simulations'),
    url(r'^simulations/(?P<id>[0-9]+)/*$', 'simulation'),
    
    #search
    url(r'^search_basic/*$', 'search_basic'),
    url(r'^search_advanced/*$', 'search_advanced'),    
    
    #documentation
    url(r'^tutorial/*$', 'tutorial'),
    url(r'^about/*$', 'about'),
    
    #sitemap
    url(r'^sitemap.xml$', 'sitemap'),
)
