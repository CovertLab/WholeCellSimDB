from django.contrib import admin
from wcdb.models import SimulationBatch

class SimulationBatchAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('organism_version', 'name', 'description', 'investigator', 'date')
    list_filter = ('organism_version', 'investigator', 'date')

admin.site.register(SimulationBatch, SimulationBatchAdmin)
