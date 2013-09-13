from django.contrib import admin
from wcdb.models import *

class SimulationAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'organism', 'length', 'date')
    list_filter = ('date', 'organism')


admin.site.register(Simulation, SimulationAdmin)
