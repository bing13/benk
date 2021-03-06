from django.conf.urls.defaults import *
# was ...patterns, include, url (instead of *)

from django.views.generic.simple import direct_to_template


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
    #url(r'^pim1/list-items/$','pim1.pengine.views.itemlist',{'proj_id':'0'}),
    url(r'^pim1/drag/(?P<proj_id>\d+)/$','pim1.pengine.views.draglist'),                       
    url(r'^pim1/grid-view/$','pim1.pengine.views.gridview'),
    url(r'^pim1/list-items/hoist/(?P<pItem>\d+)/$','pim1.pengine.views.hoistItem'),
    #url(r'^pim1/psd/(?P<pSort>\w+)/$','pim1.pengine.views.psd'),
    url(r'^pim1/psd/(?P<pSort>\w+)/(?P<targetProject>\w+)/$','pim1.pengine.views.psd'),

    ## see https://docs.djangoproject.com/en/1.3/intro/tutorial03/#design-your-urls               
    #url(r'^pim1/projdetail/(?P<proj_id>\d+)/$','pim1.pengine.views.itemlist'),       

    url(r'^pim1/item/detail/(?P<pItem>\d+)/$','pim1.pengine.views.detailItem'),
    url(r'^pim1/item/edititem/(?P<pItem>\d+)/$','pim1.pengine.views.editItem'),

    url(r'^pim1/item/add/(?P<pItem>\d+)/$','pim1.pengine.views.addItem'),
    url(r'^pim1/item/deleteINACTIVE/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'delete'}),
    url(r'^pim1/item/demote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'demote'}),
    url(r'^pim1/item/promote/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'promote'}),
    url(r'^pim1/item/moveup/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'moveup'}),
    url(r'^pim1/item/movedown/(?P<pItem>\d+)/$','pim1.pengine.views.actionItem',{'action':'movedown'}),

    url(r'^pim1/importfile/$','pim1.pengine.views.importfile'),
    url(r'^pim1/serialize/$','pim1.pengine.views.backupdata'),
    url(r'^pim1/csvdownload/(?P<projectID>\d+)/$','pim1.pengine.views.csvDownload'),                       

    url(r'^pim1/search/$','pim1.pengine.views.ssearch'),
    url(r'^pim1/advsearch/$','pim1.pengine.views.advsearch'),                                              

    url(r'^pim1/item/gooUpdate$','pim1.pengine.views.gooTaskUpdate'),
    url(r'^pim1/xhr_test$','pim1.pengine.views.xhr_test'),
    url(r'^pim1/xhr_actions$','pim1.pengine.views.xhr_actions'),
    url(r'^pim1/healthcheck/(?P<proj_id>\d+)/$','pim1.pengine.views.healthcheck'),
    url(r'^pim1/showchains/(?P<proj_id>\d+)/$','pim1.pengine.views.showChains'),
    url(r'^pim1/repairchain/(?P<proj_id>\d+)/$','pim1.pengine.views.repairChain'),                       
                       
    url(r'^pim1/addproject/$','pim1.pengine.views.createOrEditProject',{'projID':0}),
    url(r'^pim1/editproject/(?P<projID>\d+)/$','pim1.pengine.views.createOrEditProject'),


    url(r'^pim1/addprojectset/$','pim1.pengine.views.createOrEditProjectSet',{'projsetID':0}),
    url(r'^pim1/editprojectset/(?P<projsetID>\d+)/$','pim1.pengine.views.createOrEditProjectSet'),

    url(r'^pim1/maint/(?P<pLockRequest>\w+)/$','pim1.pengine.views.maintPage'),
    url(r'^pim1/maint/$','pim1.pengine.views.maintPage',{'pLockRequest':'no'}),

    url(r'^pim1/linearize/(?P<flattenMe>\w+)/$','pim1.pengine.views.linearizePage'),
    url(r'^pim1/linearize/$','pim1.pengine.views.linearizePage',{'flattenMe':'0'}),


    url(r'^pim1/manage/(?P<pLockRequest>\w+)/$','pim1.pengine.views.managePage'),
    url(r'^pim1/manage/$','pim1.pengine.views.managePage',{'pLockRequest':'no'}),


    url(r'^pim1/today/$','pim1.pengine.views.today'),                       

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'pim1_tmpl/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'pim1_tmpl/logout.html'}),
    url(r'^accounts/profile/$',  'pim1.pengine.views.profilePage',  ) , 
    url(r'^pim1/uploaditems/$','pim1.pengine.views.uploadItems'),
    url(r'^pim1/help/(?P<helpSection>\w+)/$','pim1.pengine.views.help'),
    url(r'^pim1/help/$','pim1.pengine.views.help',{ 'helpSection':''}),                       

                   
)
