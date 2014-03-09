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
    
    #investigators
    url(r'^list/investigator/*$', 'list_investigators'),
    url(r'^investigator/(?P<id>[0-9]+)/*$', 'investigator'),
    
    #organisms
    url(r'^list/organism/*$', 'list_organisms'),
    url(r'^organism/(?P<id>[0-9]+)/*$', 'organism'),
    
    #simulations
    url(r'^list/simulation_batch/*$', 'list_simulation_batches'),
    url(r'^simulation_batch/(?P<id>[0-9]+)/*$', 'simulation_batch'),
    url(r'^list/simulation/*$', 'list_simulations'),
    url(r'^simulation/(?P<id>[0-9]+)/*$', 'simulation'),
    
    #downloads    
    url(r'^download/organism/(?P<id>[0-9]+)/*$', 'organism_download'),    
    url(r'^download/simulation_batch/(?P<id>[0-9]+)/*$', 'simulation_batch_download'),
    url(r'^download/simulation/(?P<id>[0-9]+)/*$', 'simulation_download'),
    url(r'^download/investigator/(?P<id>[0-9]+)/*$', 'investigator_download'),
    url(r'^download/*$', 'download'),
    
    #search
    url(r'^search_basic/*$', 'search_basic'),
    url(r'^search_advanced/*$', 'search_advanced'),    
    
    #documentation
    url(r'^tutorial/*$', 'tutorial'),
    url(r'^help/*$', 'help'),
    url(r'^about/*$', 'about'),
    
    #sitemap
    url(r'^sitemap.xml$', 'sitemap'),
    url(r'^sitemap_top_level.xml$', 'sitemap_top_level'),
    url(r'^sitemap_simulation_batch.xml$', 'sitemap_simulation_batch'),
)
