from pim1.pengine.models import Item, Project, ProjectSet
# ++ was "pengine.models"

from django.contrib import admin

class ProjSetAdmin(admin.ModelAdmin):
    list_display=('id','name','color','owner')
    list_filter= ['owner']   

admin.site.register(ProjectSet, ProjSetAdmin)


class ProjAdmin(admin.ModelAdmin):
    list_display=('id','name','owner','color', 'set', 'projType', 'archivePair')
    list_filter= ['set']   

admin.site.register(Project, ProjAdmin)

    
class ItemAdmin(admin.ModelAdmin):
    fields = [ 'id', 'owner', 'project', 'title','parent','follows','indentLevel', 'IS_import_ID', 'priority', 'status',\
               'date_gootask_display','HTMLnoteBody', \
               'date_created', 'date_mod']
    list_display = ('id','owner', 'project', 'parent','follows', 'indentLevel','IS_import_ID','title', 'date_mod', 'date_gootask_display')
    search_fields = ['HTMLnoteBody', 'title']
    date_hierarchy = 'date_mod'

    ## following needed b/c readonly fields are normally left off admin
    ## auto_now and auto_now_add make fields readonly
    readonly_fields = ['id',  'date_created', 'date_mod',] 

    ## uncomment for QuickBase-like field selection 
    ##filter_horizontal = ['project']

admin.site.register(Item, ItemAdmin)

#class ProjAdmin(admin.TabularInline):
#    model = Project
#    extra = 3
## see also file:///C:/django-docs-1.3-en/ref/contrib/admin/index.html#django.contrib.admin.ModelAdmin.filter_horizontal
    ## for manyTOmany easier to click interface
##file:///C:/django-docs-1.3-en/ref/contrib/admin/index.html#working-with-many-to-many-models
    #inlines=[ProjAdmin]
