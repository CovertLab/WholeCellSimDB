from django.contrib import admin
from wcdb.models import *

class SimulationAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'model', 'organism', 't', 'date')
    list_filter = ('date', 'model', 'organism')


admin.site.register(Simulation, SimulationAdmin)
