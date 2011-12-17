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
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^pim1/$','pim1.pengine.views.homepage'),
    url(r'^list-items/$','pim1.pengine.views.itemlist',{'proj_id':'0'}),
    url(r'^grid-view/$','pim1.pengine.views.gridview'),
    #url(r'^$', 'pim1.pengine.views.homepage'),
    url(r'^psd/(?P<pSort>\w+)/$','pim1.pengine.views.psd'),

    ## see https://docs.djangoproject.com/en/1.3/intro/tutorial03/#design-your-urls               
    url(r'^projdetail/(?P<proj_id>\d+)/$','pim1.pengine.views.itemlist'),       

    url(r'^item/detail/(?P<pItem>\d+)/$','pim1.pengine.views.detailItem'),

    url(r'^item/add/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'add'}),
    url(r'^item/delete/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'delete'}),
    url(r'^item/demote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'demote'}),
    url(r'^item/promote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'promote'}),
    url(r'^item/moveup/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'moveup'}),
    url(r'^item/movedown/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'movedown'}),

    url(r'^importfile/$','pim1.pengine.views.importfile'),



    url(r'^item/gooUpdate$','pim1.pengine.views.gooTaskUpdate'),

                   
)
