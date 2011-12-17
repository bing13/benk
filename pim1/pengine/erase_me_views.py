# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
#from pengine.models import Item, Project
from django.template import Context, loader
import datetime, sys;



##################################################################
def homepage(request):
        #current_projs = Project.objects.all()
        c = Context({'home_page':'homepage' })
        t = loader.get_template('pim1_tmpl/testpage.html')
        return HttpResponse(t.render(c))
##################################################################
            
