from django.conf.urls.defaults import *
# was ...patterns, include, url (instead of *)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pim1.views.home', name='home'),
    # url(r'^pim1/', include('pim1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^pim1/admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^pim1/admin/', include(admin.site.urls)),

    url(r'^pim1/$','pim1.pengine.views.homepage'),
    url(r'^pim1/index.html','pim1.pengine.views.homepage'),
    url(r'^$', 'pim1.pengine.views.homepage'),
    url(r'^pim1/list-items/$','pim1.pengine.views.itemlist',{'proj_id':'0'}),
    url(r'^pim1/drag/(?P<proj_id>\d+)/$','pim1.pengine.views.draglist'),                       
    url(r'^pim1/grid-view/$','pim1.pengine.views.gridview'),
    url(r'^pim1/list-items/hoist/(?P<pItem>\d+)/$','pim1.pengine.views.hoistItem'),
    url(r'^pim1/psd/(?P<pSort>\w+)/$','pim1.pengine.views.psd'),

    ## see https://docs.djangoproject.com/en/1.3/intro/tutorial03/#design-your-urls               
    url(r'^pim1/projdetail/(?P<proj_id>\d+)/$','pim1.pengine.views.itemlist'),       

    url(r'^pim1/item/detail/(?P<pItem>\d+)/$','pim1.pengine.views.detailItem'),
    url(r'^pim1/item/edititem/(?P<pItem>\d+)/$','pim1.pengine.views.editItem'),

    url(r'^pim1/item/add/(?P<pItem>\d+)/$','pim1.pengine.views.addItem'),
    url(r'^pim1/item/delete/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'delete'}),
    url(r'^pim1/item/demote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'demote'}),
    url(r'^pim1/item/promote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'promote'}),
    url(r'^pim1/item/moveup/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'moveup'}),
    url(r'^pim1/item/movedown/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'movedown'}),

    url(r'^pim1/importfile/$','pim1.pengine.views.importfile'),
    url(r'^pim1/serialize/$','pim1.pengine.views.backupdata'),

    url(r'^pim1/pim1/search/$','pim1.pengine.views.ssearch'),                       

    url(r'^pim1/item/gooUpdate$','pim1.pengine.views.gooTaskUpdate'),
    url(r'^pim1/xhr_test$','pim1.pengine.views.xhr_test'),
    url(r'^pim1/xhr_actions$','pim1.pengine.views.xhr_actions'),


                   
)
