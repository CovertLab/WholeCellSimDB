from django.core.management.base import BaseCommand, CommandError
from WholeCellDB import settings
import os
import subprocess

class Command(BaseCommand):
    args = ''
    help = 'Compiles documentation'

    def handle(self, *args, **options):
        #generate html documentation
        subprocess.call('epydoc -o %s --name=WholeCellDB --url=%s --html --graph all --parse-only --docformat plaintext wcdb wcdbcli wcdbsearch wcdbweb' % (
            os.path.join(settings.ROOT_DIR, '..', 'wcdbweb', 'static', 'doc'), settings.ROOT_URL,
            ), shell=True)
        
        #make images of data model
        subprocess.call('python manage.py graph_models wcdb | dot -Tsvg -o %s' % os.path.join(settings.ROOT_DIR, '..', 'wcdbweb', 'static', 'doc', 'data_model.svg'), shell=True)
        subprocess.call('python manage.py graph_models wcdb | dot -Tpng -o %s' % os.path.join(settings.ROOT_DIR, '..', 'wcdbweb', 'static', 'doc', 'data_model.png'), shell=True)
        
        #status message
        self.stdout.write('Successfully compiled documentation.\n')