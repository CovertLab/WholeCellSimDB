from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from WholeCellDB.settings import HDF5_ROOT
import glob
import os

class Command(BaseCommand):
    args = ''
    help = 'Resets the SQL database, deletes all HDF5 files, rebuilds search index'

    def handle(self, *args, **options):
        interactive = options['interactive'] if 'interactive' in options else True
        
        #reset SQL db
        call_command('reset', 'wcdb', interactive=interactive)
        
        #delete HDF files
        for file in glob.glob(os.path.join(HDF5_ROOT, '*.h5')):
            os.remove(file)
        
        #rebuild search index
        call_command('rebuild_index', interactive=interactive)
            
        #status message
        self.stdout.write('Successfully reset SQL and HDF databases and search indices\n')