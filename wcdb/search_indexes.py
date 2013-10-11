'''
Whole-cell knowledge base haystack indices

Author: Jonathan Karr, jkarr@stanford.edu
Affiliation: Covert Lab, Department of Bioengineering, Stanford University
Last updated: 2012-07-17
'''

from haystack.indexes import CharField, IntegerField, SearchIndex, ModelSearchIndex
from helpers import truncate_fields
from wcdb import models

class OrganismIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    name = CharField(model_attr='name')
    
    # Hack to avoid error: "xapian.InvalidArgumentError: Term too long (> 245)"
    # See: https://groups.google.com/forum/?fromgroups#!topic/django-haystack/hRJKcPNPXqw
    def prepare(self, object):
        self.prepared_data = truncate_fields(super(OrganismIndex, self).prepare(object))        
        return self.prepared_data
        
    class Meta:
        pass
     
    def get_model(self):
        return Organism 

    def index_queryset(self, using=None):
        return self.get_model().objects.all()   


class SimulationBatchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    name = CharField(model_attr='name')
    description = CharField(model_attr='description')
    
    # Hack to avoid error: "xapian.InvalidArgumentError: Term too long (> 245)"
    # See: https://groups.google.com/forum/?fromgroups#!topic/django-haystack/hRJKcPNPXqw
    def prepare(self, object):
        self.prepared_data = truncate_fields(super(SimulationBatchIndex, self).prepare(object))        
        return self.prepared_data
            
    class Meta:
        pass
    
    def get_model(self):
        return SimulationBatch

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

