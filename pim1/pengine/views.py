################################################################
## views.py
################################################################

### to clear out ex. all but item 1, for reloading
##  ex., Item.objects.filter(project=1).exclude(id = 1).delete()

from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import login, logout
#from django.template import Context, loader
from django.template import RequestContext

from django import forms
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
#from django.forms.models import modelformset_factory 

# ++ was "pengine.models"
from pim1.pengine.models import Item, Project, ProjectSet

import datetime, sys, simplejson, codecs, csv

#D410 sys.path.append('C:\\Documents and Settings\\Owner\\My Documents\\Python\\library');
#D610 #sys.path.append('C:\\Documents and Settings\\Bernard Hecker\\My Documents\\python\\lib')
#Battlestar
#sys.path.append('C:\\Users\\Bernard\\Documents\\python64\\library');

#DreamHost - UNIX
#sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/library');

# paths to the modules I installed locally
# shouldn't have to do this to the specific egg files. Complicated b/c
# I can't install to standard (dreamhost) module location
eggPaths = ['/home/bhadmin13/python_pkgs/lib/python2.5/site-packages/httplib2-0.7.4-py2.5.egg', '/home/bhadmin13/python_pkgs/lib/python2.5/site-packages/python_gflags-2.0-py2.5.egg','/home/bhadmin13/python_pkgs/lib/python2.5/site-packages/google_api_python_client-1.0c2-py2.5.egg', '/home/bhadmin13/python_pkgs/lib/python2.5/site-packages/oauth2client-1.0c2-py2.5.egg' ]


import drag_actions, sharedMD, checkHealth;

#sharedMD.logThis('init',str(sys.path))

sys.path += eggPaths

import  httplib
import gflags
import gooOps, dirlist, south;
from rfc3339 import rfc3339;



LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'
IMPORTDIR='/home/bhadmin13/dx.bernardhecker.com/pim1/benk_imports/'
BACKUPDIR='/home/bhadmin13/dx.bernardhecker.com/pim1/benk_backups/'
QUICKNOTEDIR = '/home/bhadmin13/dx.bernardhecker.com/pim1/quicknotes/'

## https://docs.djangoproject.com/en/1.2/topics/forms/
## https://docs.djangoproject.com/en/1.3/intro/tutorial04/
class ImportForm(forms.Form):
    fileToImport=forms.CharField(max_length=300)
    projectToAdd=forms.IntegerField()

class ssearchForm(forms.Form):
    searchfx=forms.CharField(max_length=200)

class addProjectSetForm(forms.Form):
    newProjectSetName =  forms.CharField(max_length = 120, label = "project set name")
    newProjectSetColor = forms.CharField(max_length = 24, label = "background color")
    newProjectSetIDhidden = forms.IntegerField(widget = forms.HiddenInput, required=False )
    ##newProjectSetOwner = forms.CharField(max_length = 30)

class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file  = forms.FileField(label = "simple text file")
    projectID = forms.IntegerField(label = "project ID")

DRAGACTIONS=drag_actions.dragOps();

@csrf_protect


##################################################################
def homepage(request):
    sharedMD.logThis(request.user.username, "VIEW: homepage")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    return render_to_response("pim1_tmpl/home_page.html", {
        'home_page':'homepage',
        'current_projs':current_projs,
        'current_sets':current_sets,
        'nowx':datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )
    
##################################################################

def itemlist(request,proj_id):
    sharedMD.logThis(request.user.username, "VIEW: itemlist")

    ### THE ORIGINAL LIST VIEW
    ### still functional, but deprecated, and not exposed

    sharedMD.logThis(request.user.username, "Entering the original view: itemlist <==============ProjID ="+str(proj_id)+". ")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)
    
    displayList = buildDisplayList(current_projs, proj_id,'follows',0,[])
    projObj = Project.objects.get(pk=proj_id)

    titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"

    return render_to_response("pim1_tmpl/items/index.html", {
        'current_items':displayList,
        'current_projs':current_projs, 
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':titleCrumbBlurb,
        'thisSet':projObj.set.id,
        'current_sets':current_sets,
        }, context_instance=RequestContext(request) )

 
##################################################################
def allMyChildren(targetID, resultList):

    sharedMD.logThis('---', "VIEW: allMyChildren ")

    children= Item.objects.filter(parent=targetID)
    for cx in children:
        resultList.append(cx.id)
        allMyChildren(cx.id, resultList)
    
    return(resultList)    

##################################################################
@login_required 
def hoistItem(request,pItem):
    ## hoistList takes a target item ID
    ## and builds an array of all of its children
    ##   1. can't just truncate, or you get the entire rest of the file
    ##   2. need to find all children, and then draw children and their children
    ## Fourth buildlist arg is hoist ID #. BuildDisplayList calls allMyChildren

    sharedMD.logThis(request.user.username, "VIEW: hoistItem")

    hoistID=pItem
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    hoistProj=Item.objects.get(pk=hoistID).project_id 
    projObj = Project.objects.get(pk=hoistProj)

    if projObj.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 


    titleCrumbBlurb = str(hoistProj)+':'+projObj.name+"   ("+projObj.set.name+")"

    
    displayList=buildDisplayList(current_projs, hoistProj, 'follows', hoistID,[])

    return render_to_response("pim1_tmpl/items/dragdrop.html", {
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': str(pItem)+"Hoist",
        'pItem':pItem,
        'projectNum':hoistProj,
        'titleCrumbBlurb':titleCrumbBlurb,
        }, context_instance=RequestContext(request) )




##################################################################
def buildDisplayList(projectx, projID, ordering, hoistID, useListIDs):
    sharedMD.logThis('---', "   Entering buildDisplayList")

    ### Select the items to operate on ###############

    ## items in the explicit useListID (used by search0
    if useListIDs != []:
        if ordering == 'provided':
            itemList=[]
            for ULid in useListIDs:
                itemList.append(Item.objects.get(id=ULid))
            items2List = itemList
        else:
            items2List=Item.objects.filter(id__in=useListIDs).order_by(ordering)

    ## the hoist ID
    elif hoistID != 0:
        ## insures that the target item appears in the final list.
        resultList=[] 
        resultList=allMyChildren(hoistID,resultList)
        resultList.append(hoistID)
 
        ## get querySet that only has items with those IDs in it
        items2List=Item.objects.filter(id__in=resultList).order_by( ordering)
        projlist=Project.objects.get(pk=projID)

    ## the projID
    elif projID != '0': 
        ##specified project
        items2List=Item.objects.filter(project__id=projID).order_by( ordering)
        projlist=Project.objects.get(pk=projID)

    ## otherwise, all
    else:
        ##all projects, requires project sort
        items2List=Item.objects.all().order_by( ordering)
        projlist=projectx

    ### Build the parent list
    ixList=[]
    jxHash={}
    #sharedMD.logThis('---', "      ..queries done...")


    parentList=[] ## list of all items that are parents
    for px in items2List:
        if px.parent not in parentList: parentList.append(px.parent)

    ###SLOW BLOCK BEGINS########################################################################
        
    #sharedMD.logThis('---', "      ....parent list built...")
    ### get project string to where it can be displayed    
    for ix in items2List:
        
        ### count the number of ancestors to determine indent level
        ### THIS CALL IS VERY SLOW, accounting for 39sec out of 47sec total. Removed.
        ### indentLevel is now stored in model, countIndent only used for single items
        #ix.indent=countIndent(ix)
        
        if ordering=='follows':
            ix.indentString=ix.indentLevel*4*'&nbsp;'  
        else:
            ix.indentString=''

        ix.projectForOrdering=ix.project.name
        ixList.append(ix)
        jxHash[ix.id]=ix

        ## inControl uses a triangle for parents, dots for others
        if ix.id in parentList:
            ix.outlineBullet="+"
            ix.isParent=True 
        else:
            ix.outlineBullet="&bull;"
            ix.isParent=False
            

    #sharedMD.logThis('---',  "      .....ix built.....")

    displayList=[]
    followHash={}
    
    if ordering=='follows':
        ## generate outline-ordered and formatted output list
        for f2 in ixList:
            if followHash.has_key(f2.follows): 
                sharedMD.logThis('---',   "      =====> WARNING!! followHash duplicate")
                fh1=Item.objects.get(pk=followHash[f2.follows])
                sharedMD.logThis('---',  "      =====>ID:"+str(fh1.id)+":" + str(fh1) +"  follows=" + str(fh1.follows)+']')
                sharedMD.logThis('---',  "      =====>ID:"+str(f2.id)+":" + str(f2) +"  follows=" + str(f2.follows)+']\n')

            ## this is the critial line for list-building
            followHash[f2.follows] = f2.id

        ## If the minimum followHash index (i.e., field ID if field to be followed) != 0,
        ## the first item won't list, b/c it's "parent" never comes up in the chain
        ## So if there is no key=0 (ex., for listing on a single project), add one, with a
        ## value of the field ID of the first item.

        ## WRONG. The IDs could be in any order whatsoever, ex. from moving, deleting, creating
        ## items. Confusing, because they generally ARE in numeric order.
        ## Can't rely on numerical minimum of followHash index. Must find first one in
        ## "natural" benk order ,and see that.
        ##  Deduce it: FollowHash[N] has a value of the item that follows it. and FollowHash
        ##  *includes the item preceding the first item*.
        ##  So look for item with index X, where X does not appear as a value in FollowHash.
        ##    
        ##  IMPORTANT CHANGE: Allows each project to have a follower of item 0, as well as parent =0
        ##  This allows for unambiguous starting point for all list operations.
            
        ##  ALSO REQUIRED that we stop using the original all-project view, since it assumes
        ##  only one follower of "0"
            
        if min(followHash.keys()) != 0:
            for fhk in followHash.keys():
                if fhk in followHash.values():
                    continue
                else:
                    break
            sharedMD.logThis('---',  "FHK is="+str(fhk))
            followHash[0]=followHash[fhk]
            followHash.pop(fhk)
            ###sharedMD.logThis('---',  'new followhash'+str(followHash))
            
        currentID = 0

        #sharedMD.logThis('---',  "      ...built followhash....")

        ## OK, now follow the chain of who follows whom, starting with whoever follows Parent ID = 0
        while  followHash.has_key(currentID):
            displayList.append(jxHash[followHash[currentID]])
            currentID=followHash[currentID]

        # theoretically, having no followHash key for currentID means you're on the last item
        # but beware re: data integrity / lost items
        #sharedMD.logThis('---',  "      .....displayList built...")
    else:

        displayList=ixList
    sharedMD.logThis('---',  "   Exiting buildDisplayList")
    return(displayList)

##################################################################

@login_required
def actionItem(request, pItem, action):
    #sharedMD.logThis(request.user.username,  "item "+ pItem + " to " + action);
    #sharedMD.logThis(request.user.username,  "actionItem request:" + str(request))
    sharedMD.logThis(request.user.username, "VIEW: ")

    if request.is_ajax():
        sharedMD.logThis(request.user.username,  "actionItem: AJAX request,item " + pItem + " to " + action);
        ajaxRequest = True
    else:
        sharedMD.logThis(request.user.username,  "actionItem: Not an AJAX request"+ pItem + " to " + action);
        ajaxRequest = False
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)
    
    clickedItem = Item.objects.get(pk=pItem)
    clickedProjNum=clickedItem.project.id
    lastItemID=sharedMD.getLastItemID(clickedProjNum)

    origlastKidofCI,origkidList=sharedMD.findLastKid(clickedItem,lastItemID)
        
    #assigning project [many to many]...convoluted?.... 
    projIDc=clickedItem.project.id
    projObjc=Project.objects.get(pk=projIDc)


    ### SECURITY - permission check

    if projObjc.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        sharedMD.logThis("Permission denied, not the owner.")
        return HttpResponseRedirect('/pim1/') 



    ### ADD ###################################################################
    
    ## find the item that was following pItem
    if action=='add':
        try:
            oldFollower = Item.objects.get(follows=pItem)
            follower=True
        except:
            sharedMD.logThis(request.user.username,  "Item has no follower: ID" + str(pItem))
            follower=False

        newItem = Item(title="[NEW ITEM]",priority='0', status='0', \
           follows=pItem, parent=clickedItem.parent, indentLevel=clickedItem.indentLevel)
        newItem.project=clickedItem.project

        newItem.save()
        
        if follower:
            oldFollower.follows = newItem.id
            oldFollower.save()
    ###DELETE###################################################################

    elif action=='delete':
        if int(pItem) != lastItemID:
            
            sharedMD.logThis(request.user.username,  "===pItem, lastItemID============"+str(pItem)+ '  '+str(lastItemID)+"==============")
            followingMe = Item.objects.get(follows=pItem)
            followingMe.follows=clickedItem.follows
            if followingMe.parent==clickedItem.id:
                followingMe.parent=clickedItem.parent
            followingMe.save()

        # remove entry from Projects
        projObjc.item_set.remove(clickedItem)
        # remove item
        clickedItem.delete()

    ###DEMOTE###################################################################
    elif action=='demote':
        if clickedItem.parent==clickedItem.follows:
            sharedMD.logThis(request.user.username,  "Can't demote further, item "+str(clickedItem.id))
        else:
            ## if CI and the item following it have same parent, just shift CI parent, and indent CI

            lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)

            ## find the first preceeding item is the same level as the demoted CI,
            ## and adopt the same parent
            ##indx=clickedItem;
            ##while indx.indentLevel != clickedItem.indentLevel+1:
            ##    indx=Item.objects.get(pk=indx.follows)
            ##clickedItem.parent=indx.parent


            # find first preceeding item at same level, make it CI's parent
            indx=Item.objects.get(pk=clickedItem.follows)
            while indx.indentLevel != clickedItem.indentLevel:
                indx=Item.objects.get(pk=indx.follows)
            clickedItem.parent=indx.id
            clickedItem.indentLevel += 1
            clickedItem.save()


            ## fix the indentLevel of the item's children
            if lastKidID != 0:
                thisItem = clickedItem

                while thisItem.id != lastKidID:
                    thisItem=Item.objects.get(follows=thisItem.id)
                    thisItem.indentLevel += 1;
                    thisItem.save()


    ###PROMOTE##################################################################
    elif action=='promote':
        runKids='no'
        lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)
        CIoriginalParent=clickedItem.parent
        
        if clickedItem.parent ==  0:
            sharedMD.logThis(request.user.username,  "CAN'T PROMOTE TOP-LEVEL "+ str(pItem))

        else:
            ### Deal with parent assignments first
            
            sharedMD.logThis(request.user.username, "Promoting: " +str(clickedItem.id))
            indx=Item.objects.get(pk=clickedItem.follows)
            while indx.indentLevel >= clickedItem.indentLevel:
                indx=Item.objects.get(pk=indx.follows)
            clickedItem.parent=indx.parent

            ### Now promote the parent
            clickedItem.indentLevel -= 1
            clickedItem.save()
            runKids='yes'

        if runKids == 'yes' and clickedItem.id != lastItemID:

            ## now deal with  the kids

            # if items following the promotee are of the same level, we have to turn
            # the consecutive run of a same level/parent items into children (parent, indent)
            if Item.objects.get(follows=clickedItem.id).parent == CIoriginalParent:
                sharedMD.logThis(request.user.username, "converting subsequent items to children...")
                indx = Item.objects.get(follows=clickedItem.id)
                while indx.parent == CIoriginalParent:
                    indx.parent=clickedItem.id
                    indx.save()
                    if indx.id != lastItemID:
                        indx=Item.objects.get(follows=indx.id)
                    else:
                        indx.parent='LAST ITEM - BAIL'

            else:
                # promotee has real kids
                sharedMD.logThis(request.user.username, "k-promote: LastKidID="+str(lastKidID))
                if lastKidID != 0:
                    thisItem=Item.objects.get(follows=clickedItem.id)
                    while thisItem.id != lastKidID:
                        thisItem.indentLevel -= 1;
                        thisItem.save()
                        thisItem=Item.objects.get(follows=thisItem.id)

                    #pick up the last child, since it increments after the action
                    thisItem.indentLevel -= 1
                    thisItem.save()
  

    ###MOVE UP##################################################################
    elif action=='moveup':

        if clickedItem.follows==0:
            sharedMD.logThis(request.user.username,  "CAN'T MOVE UP TOP item "+ str(pItem))
        else:
            hasFollower=False             
            lastKid,kidList=sharedMD.findLastKid(clickedItem,lastItemID)

            targetToSwap=Item.objects.get(pk=clickedItem.follows)

            if lastKid==0: ### no kids
                bottomToSwap=Item.objects.get(pk=clickedItem.id)
            else:
                bottomToSwap=Item.objects.get(pk=lastKid)

            ## targetToSwap - the item above the clicked item
            ## bottom to swap - either the target item, or its last kid (if any)
            ## follow_bts - the item that follows the bottom to swap item, if such an item exists
            ## the swaps are then obvious.

            tts_follows=targetToSwap.follows
            bts_follows=bottomToSwap.follows

            #swap 'em
            if bottomToSwap.id != lastItemID:
                follows_bts=Item.objects.get(follows=bottomToSwap.id)
                follows_bts.follows=targetToSwap.id
                follows_bts.save()


            clickedItem.follows=tts_follows
            clickedItem.parent=targetToSwap.parent
            targetToSwap.follows=bottomToSwap.id
            clickedItem.save()
            targetToSwap.save()


    ### MOVE DOWN ################################################################
  
    elif action=='movedown':
        
        ### may wish to remodel so it looks like "moveup", which uses the findLastKid method
        lastKidofCI,kidList=sharedMD.findLastKid(clickedItem,lastItemID)
        if clickedItem.id == lastItemID or lastKidofCI == lastItemID:
            sharedMD.logThis(request.user.username,  "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
        else:
            #ciFollower=Item.objects.get(follows=clickedItem.id)
            if lastKidofCI !=0:
                fciFollower=Item.objects.get(follows=lastKidofCI)
            else:
                fciFollower=Item.objects.get(follows=clickedItem.id)
            lastKidOfFollower,kidList=sharedMD.findLastKid(fciFollower, lastItemID)
            if lastKidOfFollower==0:
                bottomToSwap= fciFollower
            else:
                bottomToSwap= Item.objects.get(pk=lastKidOfFollower)

            ## swap them
            fciFollower.follows=clickedItem.follows
            clickedItem.follows=bottomToSwap.id

            if bottomToSwap.id != lastItemID:
                bottomFollower=  Item.objects.get(follows=bottomToSwap.id)
                #bottomFollower.follows = clickedItem.id
                if lastKidofCI==0:
                    bottomFollower.follows = clickedItem.id
                else:
                    bottomFollower.follows = lastKidofCI
                bottomFollower.save()

            clickedItem.save()
            fciFollower.save()


    ###ACTION UNKNOWN########

    else:
        sharedMD.logThis(request.user.username,  "===WARNING!=========== Unknown action=" + action)
        exit()

    ###########################################################################
    ## let's restrict default view to the clicked item project
        
    sharedMD.logThis(request.user.username,  "      Action done. current project #"+str(clickedProjNum)+ " " +\
             current_projs.get(pk=clickedProjNum).name + "Ajax:"+str(ajaxRequest))

    if not ajaxRequest:
        displayList = buildDisplayList(current_projs,clickedProjNum, 'follows',0,[])

        #t = loader.get_template('pim1_tmpl/items/index.html')
        #t = loader.get_template('/drag/'+str(clickedProjNum)+'/#'+str(pItem))


        projObj = Project.objects.get(pk=proj_id)
    
        titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"
        sharedMD.logThis(request.user.username, "    Action completed, for Non-ajax call.  " + titleCrumbBlurb)  
        return render_to_response("pim1_tmpl/draglist.html", {
            'current_items':displayList,
            'current_projs':current_projs, 
            'current_sets':current_sets,

            'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
            'pagecrumb': titleCrumbBlurb,
            'pItem':pItem,
            'projectNum':clickedProjNum,
        
        }, context_instance=RequestContext(request) )

    else:
        ## for all of these operations, we may need to refresh CI, ci.follows, ci.parent, ci children, the item that follows CI
        return (clickedItem.id)


    ##############################################(end of actionItem)########

@login_required
def psd(request,pSort,targetProject):
    sharedMD.logThis(request.user.username, "VIEW: psd")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    request.session['viewmode'] = 'psd'


    ### SECURITY - permission check
    targProjObj = Project.objects.get(pk=targetProject)

    if targProjObj.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 

    
    if pSort=='goo_date': pSort='date_gootask_display'
    # priority, status, date_mod, date_created

    if pSort=='date_created' or pSort=='date_mod': 
        pSort="-"+pSort
    elif  pSort=="date_gootask_display":
        pSort="-"+pSort

    displayList =  buildDisplayList(current_projs,targetProject,pSort,0,[])

    titleCrumbBlurb = "sort view   "+ targProjObj.name+"   ("+targProjObj.set.name+")"

    return render_to_response("pim1_tmpl/items/psd.html", {
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets, 
        'targetProject':targetProject,
        'pSort':pSort,
        'titleCrumbBlurb':titleCrumbBlurb,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )


###################################################################
@login_required
def gridview(request):
    sharedMD.logThis(request.user.username, "VIEW: gridview")

    ITEMS_PER_CELL = 10;
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    displayList = [] ; 

    for thisProject in current_projs:
        cellItems = [];
        #(projlist, projID, ordering, hoistID, useList)

        # limit = min(ITEMS_PER_CELL, Item.objects.filter(project=thisProject.id).count());

        # complexity comes b/c you can't slice a query set, and expect it to be ordered the
        # way you want. It just takes the first [:n] items, and orders those
        
        cellObjs = []
        for priorityLevel in (1,2,3,4,5,6,7,8,9,0,99,''):
            cx = Item.objects.filter(project=thisProject, priority=priorityLevel, owner = request.user.username)[:ITEMS_PER_CELL]


            #works in TODAY:    todayIDs = Item.objects.filter(priority=1).filter(project__projType=1, owner = request.user.username).order_by('project__name')
            # ,  owner = request.user.username
            # preceding line returns no results for jmoss. Works on projects.
            #####################################################################
            
            ## i.e., no need to consider more than ITEMS_PER_CELL max in a category, since that's
            ## the *overall* limit for gridview
            
            for co in cx:
                cellItems.append(co.id)

        sharedMD.logThis(request.user.username, "   cellItems=" + str(cellItems))       
        dx =   buildDisplayList(current_projs,thisProject.id, 'provided', 0, cellItems[:ITEMS_PER_CELL])
        displayList = displayList + dx

    return render_to_response("pim1_tmpl/items/gridview.html", {
        
        'titleCrumbBlurb':'grid view',
        'displayList':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )



##################################################################
@login_required
def detailItem(request,pItem):
    # shows a full screen view of one item, non-editable
    
    sharedMD.logThis(request.user.username, "VIEW: detailItem")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)


    ix=Item.objects.get(pk=pItem)
    #get project to where it can be displayed; was project_s
    ###ix.project=ix.project 

    projObj = Project.objects.get(pk=ix.project.id)


    ### SECURITY - permission check

    if projObj.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 

    
    titleCrumbBlurb = str(ix.project.id)+':'+projObj.name+"   ("+projObj.set.name+")"


    displayList=[ix]

    return render_to_response("pim1_tmpl/items/itemDetail.html", {
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'item detail',
        'thisSet': ix.project.set.id
        }, context_instance=RequestContext(request) )



##################################################################
@login_required
def gooTaskUpdate(request):

    sharedMD.logThis(request.user.username, "VIEW: gooTaskUpdate")

    request.session['viewmode'] = 'psd'


    benkId = u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0Mzow'
    GOOTASK=gooOps.gooOps()
    sharedMD.logThis(request.user.username, "   ... instantiating service connector")

    serviceConn, redirX=GOOTASK.taskAPIconnect(request)

    sharedMD.logThis(request.user.username, "   ...serviceConn="+serviceConn)
    #77777
    ## get tasks from  tasklist=benk from google
    sharedMD.logThis('gooOps','....user()='+str(request.user.user_id()))

    if redirX != '':
        return(HttpResponseRedirect(serviceConn))
    

    gootasks = serviceConn.tasks().list(tasklist=benkId).execute()
    gooTaskIdList=[]

    sharedMD.logThis(request.user.username, "   ...gootasks loop")


    for g in gootasks['items']:
        gooTaskIdList.append(g['id'])

    sharedMD.logThis(request.user.username,  "gooTaskIdList="+str(gooTaskIdList))

    ## update all items that have google task display dates
    pushableItems=Item.objects.filter(date_gootask_display__gte=datetime.date(2000, 1, 1), owner = request.user.username)
    #newIds=GTO.pushBenkToGooTasks(TASKLISTNAME, USER, pushableItems)

    # RFC 3339 timestamp
    resultIDs=[]

    for x in pushableItems:
        task = { 
                 'title': x.title, 
                 'notes': x.HTMLnoteBody,  
                 'due': rfc3339(x.date_gootask_display, utc=True)
                }

        ## the rfc3339.py module doesn't include fractions of seconds(?), 
        ## which the API seems to require(!)
        task['due'] = task['due'][:-1]+'.000Z'

        if x.gtask_id in gooTaskIdList:
            task['id']=x.gtask_id
            result = serviceConn.tasks().update(tasklist=benkId, task=x.gtask_id, body=task).execute()
            resultIDs.append( (result['id'],'update') )
        else:
            result = serviceConn.tasks().insert(tasklist=benkId, body=task).execute()
            resultIDs.append( (result['id'],'create') )
            x.gtask_id=result['id']
            x.save()

    # bypassing builddisplaylist, since it only filters by project
    # ...oops, we need to adorn it with project and ???
    
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    displayList =  buildDisplayList(current_projs,'0','-date_gootask_display',0,[])

    return render_to_response("pim1_tmpl/items/psd.html", {

        'pSort':'-date_gootask_display',
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': "Google task date sort"        
    }, context_instance=RequestContext(request) )

 
##################################################################
@login_required
def gooTaskUpdateOLD(request):

    sharedMD.logThis(request.user.username, "VIEW: gooTaskUpdate")

    request.session['viewmode'] = 'psd'


    benkId = u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0Mzow'
    GOOTASK=gooOps.gooOps()
    sharedMD.logThis(request.user.username, "   ... instantiating service connector")

    serviceConn=GOOTASK.taskAPIconnect(request)

    sharedMD.logThis(request.user.username, "   ...calling connector")



    ## get tasks from  tasklist=benk from google
    gootasks = serviceConn.tasks().list(tasklist=benkId).execute()
    gooTaskIdList=[]

    sharedMD.logThis(request.user.username, "   ...gootasks loop")


    for g in gootasks['items']:
        gooTaskIdList.append(g['id'])

    sharedMD.logThis(request.user.username,  "gooTaskIdList="+str(gooTaskIdList))

    ## update all items that have google task display dates
    pushableItems=Item.objects.filter(date_gootask_display__gte=datetime.date(2000, 1, 1), owner = request.user.username)
    #newIds=GTO.pushBenkToGooTasks(TASKLISTNAME, USER, pushableItems)

    # RFC 3339 timestamp
    resultIDs=[]

    for x in pushableItems:
        task = { 
                 'title': x.title, 
                 'notes': x.HTMLnoteBody,  
                 'due': rfc3339(x.date_gootask_display, utc=True)
                }

        ## the rfc3339.py module doesn't include fractions of seconds(?), 
        ## which the API seems to require(!)
        task['due'] = task['due'][:-1]+'.000Z'

        if x.gtask_id in gooTaskIdList:
            task['id']=x.gtask_id
            result = serviceConn.tasks().update(tasklist=benkId, task=x.gtask_id, body=task).execute()
            resultIDs.append( (result['id'],'update') )
        else:
            result = serviceConn.tasks().insert(tasklist=benkId, body=task).execute()
            resultIDs.append( (result['id'],'create') )
            x.gtask_id=result['id']
            x.save()

    # bypassing builddisplaylist, since it only filters by project
    # ...oops, we need to adorn it with project and ???
    
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    displayList =  buildDisplayList(current_projs,'0','-date_gootask_display',0,[])

    return render_to_response("pim1_tmpl/items/psd.html", {

        'pSort':'-date_gootask_display',
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': "Google task date sort"        
    }, context_instance=RequestContext(request) )

 

##################################################################


def example_task():
    result= {u'status': u'needsAction', 
             u'kind': u'tasks#task', 
             u'title': u'Prototype a PIM', 
             u'updated': u'2011-10-27T02:30:45.000Z', 
             u'due': u'2011-10-28T00:00:00.000Z', 
             u'etag': u'"ptcy4AHsJo00xaxzUf9tbyBY9Zc/LTEzNjgyMjE4OTQ"',
             u'position':u'00000000000000000032', 
             u'id': u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0MzoxMTU2MDEyNzUy', 
             u'selfLink': u'https://www.googleapis.com/tasks/v1/lists/MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0Mzow/tasks/MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0MzoxMTU2MDEyNzUy'}
    return(result)

#############################################################################
@login_required
def ssearch(request):
    sharedMD.logThis(request.user.username, "VIEW: search")


    request.session['viewmode'] = 'ssearch'

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    c = {}
    c.update(csrf(request))
    error_message=''
    searchTerm=''
     
    if request.method == 'GET':
        sform = ssearchForm(request.GET)
        if sform.is_valid():
            searchTerm=sform.cleaned_data['searchfx']
            sharedMD.logThis(request.user.username, "Search term="+searchTerm)

            request.session['searchterm'] = searchTerm

            ## Execute the search ##
            ## get the querySets
            # Item.objects.filter(priority=1).filter(project__projType=1, owner = request.user.username).order_by('project__name')

            #titleHits=Item.objects.filter(title__icontains=searchTerm)
            #noteHits=Item.objects.filter(HTMLnoteBody__icontains=searchTerm)

            titleHits = Item.objects.filter(project__projType=1, owner = request.user.username, title__icontains=searchTerm)
            noteHits  = Item.objects.filter(project__projType=1, owner = request.user.username, HTMLnoteBody__icontains=searchTerm)
            
            ## enumerate the hit IDs
            totalHits=[]
            for h in titleHits:
                totalHits.append(h.id)
            for h in noteHits:
                totalHits.append(h.id)
            if totalHits != []:
                displayList=buildDisplayList(current_projs, 0, 'project', 0, totalHits)
                #buildDisplayList(projectx, projID, ordering, hoistID, useList):
            else:
                ## no hits
                displayList=[]

        else:
            error_message="Form was not valid, search term = "
            displayList=['Form not valid, no results to display']

    return render_to_response("pim1_tmpl/items/psd.html", {
        
        'searchterm':searchTerm,
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'titleCrumbBlurb':'search result',
        'error_message':error_message,
        'is_search_result':'true'
        
        }, context_instance=RequestContext(request) )


#############################################################################
@login_required
def addItem(request, pItem):
    sharedMD.logThis(request.user.username, "VIEW: addItem")

    clickedItem=Item.objects.get(pk=pItem)

    ### SECURITY - permission check
    targProjObj = Project.objects.get(pk=clickedItem.project_id)

    if targProjObj.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 


    
    lastItemID=sharedMD.getLastItemID(clickedItem.project_id)
    newItem=DRAGACTIONS.addItem(request, clickedItem, lastItemID)
    sharedMD.logThis(request.user.username, 'edit new item: ' + str(newItem.id))
    #follow does not work, no idea why
    return HttpResponseRedirect('/pim1/item/edititem/'+str(newItem.id))
                                        
#############################################################################
@login_required
def editItem(request, pItem):
    
    itemProject = Item.objects.get(pk=pItem).project_id
    projectName = Project.objects.get(pk=itemProject).name
    projectOwner = Project.objects.get(pk=itemProject).owner

    ### AUTH CHECK
    if projectOwner != request.user.username:
        sharedMD.logThis(request.user.username, "WARNING: attempt to edit item #" + str(pItem) + "in project " + projectName + ".  Not owned by this user!")
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 


    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    # model formsets
    ###https://docs.djangoproject.com/en/1.2/topics/forms/modelforms/#using-a-model-formset-in-a-view
    
    itemFormSet = forms.models.modelformset_factory(Item, max_num=0,fields=("title","priority","status","HTMLnoteBody", 'date_gootask_display'));
    #exclude=('IS_import_ID', 'gtask_id', 'project', 'date_gootask_display', 'owner', 'follows', 'parent', 'indentLevel'))
    #u'2011-10-28T00:00:00.000Z'

    
    ## "field" and "exclude" operands supported

    if request.method == 'POST':
        formset=itemFormSet(request.POST, request.FILES)
        changedInstances=formset.save()
        sharedMD.logThis(request.user.username, "   Formset saved: "+str(changedInstances))

        ## POST completed, now redirect to the correct view
        if request.session['viewmode'] == 'today':
            return HttpResponseRedirect('/pim1/today/')
        elif request.session['viewmode'] == 'psd':
            return HttpResponseRedirect('/pim1/psd/date_mod/' + str(itemProject) + '/#' + str(pItem))
        elif request.session['viewmode'] == 'ssearch':
            return HttpResponseRedirect('/pim1/search/?searchfx=' + request.session['searchterm'])
       
        else:
            return HttpResponseRedirect('/pim1/drag/'+str(itemProject)+'/#'+str(pItem))
    
    else:
        formset = itemFormSet(queryset=Item.objects.filter(pk=pItem))


        formsetOut = formset.as_table()
        sharedMD.logThis(request.user.username, "Edit item: Formset generated, pItem="+str(pItem))
        ##sharedMD.logThis(request.user.username, formsetOut)
        
    return render_to_response("pim1_tmpl/items/editItem.html", {
        "pItem": pItem,
        "rawform": formset,
        "projectNum": itemProject,
        "projectName": projectName,
        "formset": formsetOut,
        'pagecrumb':'edit an item',
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )

                                     
############################################################################
@login_required
@user_passes_test(sharedMD.validate_maint_membership,login_url='/pim1/')

def importfile(request):
    sharedMD.logThis(request.user.username, "VIEW: importfile")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    c = {}
    c.update(csrf(request))	  
 
    if request.method == 'POST': # If the form has been posted...
        form = ImportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            fileToImport=form.cleaned_data['fileToImport']
            projectToAdd=form.cleaned_data['projectToAdd']
            sharedMD.logThis(request.user.username,  "fileToImport="+fileToImport)
            sharedMD.logThis(request.user.username,  "projectToAdd="+str(projectToAdd))

            sharedMD.logThis(request.user.username,  "+++ departing to importISdata")
            importISdata(fileToImport,projectToAdd)

            # Redirect after POST
            return HttpResponseRedirect('/pim1/drag/'+str(projectToAdd)) 
    else:
        form = ImportForm() # An unbound form

    return render_to_response('pim1_tmpl/importIS.html', {
                'dirlist':dirlist.dirlist(IMPORTDIR),
                'form':form,
                'pagecrumb':'import',
                'current_projs':current_projs,
                'current_sets':current_sets,

                'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
                }, context_instance=RequestContext(request) )
  
#############################################################################
@login_required
def importISdata(importFile,newProjectID):
    sharedMD.logThis(request.user.username, "VIEW: importISdata")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)


    textAccumulator = ''
    ISparentFirst = ''
    selectorTitle = ''
    read_indentLevel = ''
    read_priority = ''
    read_status = ''
    read_date_created = ''
    read_date_mod = ''
    read_date_goo_task = ''
    read_goo_task_id = ''
    currentISid = 0
    previousNewItemBenkID=sharedMD.getLastItemID(newProjectID)
    firstRecord = 'yes'
    numberOfRecordsImported = 0

    sharedMD.logThis(request.user.username,  ">>> importISdata from " + IMPORTDIR + importFile)
    
    INFILE=open(IMPORTDIR + importFile,'r')
    allLines=INFILE.readlines()

    importedRecordIDs = []

    ## this makes sure the last record gets written out
    allLines.append('@@!! NEW_RECORD =====================================')
    
    
    for lx in allLines[:]:
        if lx[0:4] != '@@!!':  # we assume it's a continuing note body
            textAccumulator += lx
        else:
            #print lx[:-1]
            marker, itemType, data = lx[:-1].split(' ', 2)
            if itemType == 'NEW_RECORD':
                if firstRecord == 'yes':
                    firstRecord = 'no'
                else:
                    ## you've hit a NEW_RECORD line, and it's not the very first record, so it's
                    ## time to save the (previous) record
                    
                    newItem = Item(title=selectorTitle, \
                              follows=previousNewItemBenkID, \
                              IS_import_ID = currentISid,     \
                             
                              gtask_id = read_goo_task_id, \
                              HTMLnoteBody = textAccumulator)

                    if ISparentFirst == 0:
                        newItem.parent = 0
                    else:
                        sharedMD.logThis(request.user.username, "  Import: currentISid="+str(currentISid)+"  ISparentFirst="+str(ISparentFirst))
                        newItem.parent=Item.objects.get(IS_import_ID=ISparentFirst).id
                    newItem.project=Project.objects.get(pk=newProjectID)


                    if read_priority == '':
                        newItem.priority = 0
                    else:
                        newItem.priority = read_priority


                    if read_status == '':
                        newItem.status = 0
                    else:
                        newItem.status = read_status


                    if read_indentLevel == '':
                        newItem.indentLevel=sharedMD.countIndent(newItem)
                    else:
                        newItem.indentLevel = read_indentLevel


                    if read_date_created != '':
                        newItem.date_created = datetime.datetime.strptime(read_date_created,'%Y-%m-%d %H:%M:%S')

                    if read_date_mod != '':
                        newItem.date_mod = datetime.datetime.strptime(read_date_mod,'%Y-%m-%d %H:%M:%S')

                    if read_date_goo_task != 'None' and read_date_goo_task != '':
                        newItem.date_gootask_display = datetime.datetime.strptime(read_date_goo_task,'%Y-%m-%d %H:%M:%S')

                    newItem.save()
                    numberOfRecordsImported += 1


                    
                    importedRecordIDs.append(newItem.id)
                    ### PURGE PREVIOUS VALUES ###

                    textAccumulator = ''                   
                    previousNewItemBenkID = newItem.id
                    ISparentFirst = ''
                    selectorTitle = ''
                    read_indentLevel = ''
                    read_priority = ''
                    read_status = ''
                    read_date_created = ''
                    read_date_mod = ''
                    read_date_goo_task = ''
                    read_goo_task_id = ''

            elif itemType == 'ID':
                ## this is the non-unique Info Select exported item ID
                previousISid = currentISid
                currentISid = data

            elif itemType == 'FOLLOWS':
                # everyone follows the previousNewItemBenkID, see NEW_RECORD
                pass;

            elif itemType == 'PARENTS':
                #print "parent data=%s=" % data
                splitter = []
                splitter = data.split(',',1)
                if len(splitter) > 0 :
                    if splitter[0].isdigit():
                        ## added int() 1/7/2012
                        ISparentFirst = int(splitter[0])
                    else:
                        ISparentFirst=0
                else:
                    ISparentFirst=0

            elif itemType == 'SELECTOR':
                selectorTitle=data;

            elif itemType == 'INDENT_LEVEL':
                ## assume if it's provided, it's good 
                read_indentLevel = data;
                

            elif itemType == 'PROJECT':
                ## won't override the form data, so this value isn't used
                read_project = data;


            elif itemType == 'PRIORITY':
                read_priority = data;


            elif itemType == 'STATUS':
                read_status = data;

            elif itemType == 'DATE_CREATED':
                read_date_created = data;
                sharedMD.logThis(request.user.username, 'Date_created:'+str(read_date_created)+' ['+str(id)+']')

            elif itemType == 'DATE_MODIFIED':
                read_date_mod = data;
                sharedMD.logThis(request.user.username, 'Date_modified:'+str(read_date_mod))

            elif itemType == 'DATE_GOO_TASK':
                read_date_goo_task = data;
                sharedMD.logThis(request.user.username, 'read_date_goo_task:'+str(read_date_goo_task))

            elif itemType == 'GOO_TASK_ID':
                read_goo_task_id = data; 


            elif itemType == 'NOTE':
                # nothing to do here. We're accumulating all row bodies that do not start
                # with the marker, and then dumping them when we hit a NEW_RECORD
                pass;

            else:
                sharedMD.logThis(request.user.username,  "* * RECORD TYPE MISSED * *:"+ str(lx))
    newItem.save()
    importedRecordIDs.append(newItem.id)

    ### now clear out all the IS_import_ID's to make way for future imports
    for importID in importedRecordIDs:
        cleanUp=Item.objects.get(pk=importID)
        cleanUp.IS_import_ID=-999
        cleanUp.save()

    sharedMD.logThis(request.user.username, ">>> Completed. # of imported records: " + str(numberOfRecordsImported))
    
##################################################################
@login_required
def draglist(request, proj_id):
    sharedMD.logThis(request.user.username, "VIEW: draglist")
    
    sharedMD.logThis(request.user.username, "     Proj "+str(proj_id))

    if request.user.username != Project.objects.get(id=proj_id).owner:
        sharedMD.logThis(request.user.username, "      Invalid user for this project, aborting.")
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 
    

    request.session['viewmode'] = 'draglist'
    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    displayList = buildDisplayList(current_projs, proj_id,'follows',0,[])


    projObj = Project.objects.get(pk=proj_id)

    titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"
    totalProjItems = Item.objects.filter(project=proj_id).count()



    return render_to_response("pim1_tmpl/items/dragdrop.html", {

        'titleCrumbBlurb':titleCrumbBlurb,
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'thisSet':projObj.set.id,
        'totalProjItems':totalProjItems,
       
        }, context_instance=RequestContext(request) )


######################################################################
def xhr_test(request):
    sharedMD.logThis(request.user.username, "VIEW: xhr_test")
    
    myRequest=request.GET
    sharedMD.logThis(request.user.username, "xhr_test entered........")

    sharedMD.logThis(request.user.username, "request.GET="+str(myRequest))

    a=[(1,11),(2,22),(3,33),(4,44), (5,55)]
    jsona=simplejson.dumps(a)
    
    message = 'nix'
    if request.is_ajax():
        message = "Request is from AJAX"
        
    else:
        message = "not ajax"
    sharedMD.logThis(request.user.username, "xhr_test, message="+message)
    
    mimetypex = 'application/javascript'
    return HttpResponse(jsona,mimetype=mimetypex)

#(r'^xhr_test$','your_project.your_app.views.xhr_test'),
######################################################################
#@login_required
def xhr_actions(request):
    sharedMD.logThis(request.user.username, "VIEW: xhr_actions")

    mimetypex = 'application/javascript'

    
    actionRequest=request.GET
    ##sharedMD.logThis(request.user.username, str(actionRequest))
    message = 'nix'

    ### make sure it's an AJAX request
    if request.is_ajax():
        message = "xhr:AJAX request: "+actionRequest['ajaxAction']+'  ci='+str(actionRequest['ci'])+"  ti="+str(actionRequest['ti'])
        sharedMD.logThis(request.user.username, "=====> xhr_actions: ="+message)
    else:
        message = "xhr:Not an AJAX request.  Action:"+actionRequest['ajaxAction']+'  ci='+str(actionRequest['ci'])+"  ti="+str(actionRequest['ti'])
        sharedMD.logThis(request.user.username, "=====> xhr_actions: ="+message)
        return HttpResponse(simplejson.dumps(['NOT_AJAX']+[message]), mimetype=mimetypex)
        
    lockStatus = sharedMD.testLock(request.user.username)

    if lockStatus != 'no lock':
        sharedMD.logThis(request.user.username, "         ==> LOCK FILE exists:" + str(lockStatus))
        
        lockInfo=simplejson.dumps(['LOCKED']+[lockStatus])
        return HttpResponse(lockInfo, mimetype=mimetypex)
    


    elif actionRequest['ajaxAction'] == 'getQuicknote':
        
        ## open, reading quicknotes
        QN = open(QUICKNOTEDIR+'/'+request.user.username+'/quicknote.txt', 'r')
        quicknote = QN.readlines()
        QN.close;
        quickText = ''
        for q in quicknote:
            quickText = quickText + q

        quickNoteText = simplejson.dumps(['getQuicknote']+[quickText])
        return HttpResponse(quickNoteText, mimetype=mimetypex);

    elif actionRequest['ajaxAction'] == 'putQuicknote':
        QN = open(QUICKNOTEDIR+'/'+request.user.username+'/quicknote.txt', 'w')
        QN.write(actionRequest['datax']);
        QN.close;

        qbname = datetime.datetime.now().strftime("%Y:%m:%d_%H:%M:%S_") + 'quicknote.bkp'
        QBACK = open(QUICKNOTEDIR+'/'+request.user.username+'/'+qbname, 'w')
        QBACK.write(actionRequest['datax']);
        QBACK.close;
        
        quickNoteText = simplejson.dumps(['saveQuicknote']+['nix'])        
        return HttpResponse(quickNoteText, mimetype=mimetypex);
    
    clickedItem=Item.objects.get(pk=actionRequest['ci'])


    ## security - PERMISSION CHECK
    if clickedItem.project.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 



    ## set lock
    sharedMD.createLock(request.user.username, actionRequest['ajaxAction']+"  Proj:"+str(clickedItem.project_id)+" ci:"+str(clickedItem.id) +"  ti:"+ str(actionRequest['ti']) )

    lastItemID=sharedMD.getLastItemID(clickedItem.project_id)

    ## to dragmove #################################

    if actionRequest['ajaxAction'] == 'dragKid':
        #BEWARE - if you require login on drag_move, the next line will fail. User/int decorator
        refreshThese= DRAGACTIONS.drag_move(request, int(actionRequest['ci']),int(actionRequest['ti']));
  
    # this is where the shift-drag action should go
    elif actionRequest['ajaxAction']== 'dragPeer':
        refreshThese= DRAGACTIONS.drag_peer(request, int(actionRequest['ci']), int(actionRequest['ti']))

    elif actionRequest['ajaxAction']== 'moveUp':
        refreshThese=DRAGACTIONS.moveUp(clickedItem,  lastItemID)

    elif actionRequest['ajaxAction']== 'moveDown':
        refreshThese=DRAGACTIONS.moveDown(clickedItem, lastItemID)

    elif actionRequest['ajaxAction']== 'promote':
        refreshThese=DRAGACTIONS.promote(clickedItem, lastItemID)

    elif actionRequest['ajaxAction']== 'demote':
        refreshThese=DRAGACTIONS.demote(clickedItem, lastItemID)

    elif actionRequest['ajaxAction']== 'delete':
        # javascript on the form already deleted the item from the DOM
        refreshThese=DRAGACTIONS.delete(clickedItem, lastItemID)

    elif actionRequest['ajaxAction']== 'archiveThisItem':
        # javascript on the form already deleted the item from the DOM
        refreshThese=DRAGACTIONS.swapWithArchivePair(clickedItem, lastItemID)

    elif actionRequest['ajaxAction']== 'incPriority':
        refreshThese=DRAGACTIONS.priorityChange(clickedItem, 'up')
    elif actionRequest['ajaxAction']== 'decPriority':
        refreshThese=DRAGACTIONS.priorityChange(clickedItem, 'down')

    elif actionRequest['ajaxAction']== 'incStatus':
        refreshThese=DRAGACTIONS.statusChange(clickedItem, 'up')
    elif actionRequest['ajaxAction']== 'decStatus':
        refreshThese=DRAGACTIONS.statusChange(clickedItem,  'down')

    elif actionRequest['ajaxAction']== 'prioritySelected':
        refreshThese=DRAGACTIONS.prioritySelected(clickedItem, actionRequest['datax'])
    elif actionRequest['ajaxAction']== 'statusSelected':
        refreshThese=DRAGACTIONS.statusSelected(clickedItem, actionRequest['datax'])

    elif actionRequest['ajaxAction']== 'doOrderSelected':
        refreshThese=DRAGACTIONS.doOrderSelected(clickedItem, actionRequest['datax'])




    elif actionRequest['ajaxAction']== 'fastAdd':
        
        refreshThese,newItemTemplate=DRAGACTIONS.fastAdd(clickedItem, actionRequest['FADtitle'], actionRequest['FADstatus'], actionRequest['FADpriority'], actionRequest['FADhtmlBody'] )



    else:
        sharedMD.logThis(request.user.username, "+++ERROR+++. Uncaught actionRequest['ajaxAction']:"+actionRequest['ajaxAction'])
        refreshThese=[]

    ### test project validity, release lock if clean
    validateResult = sharedMD.validate_project(request, clickedItem.project_id)
    if validateResult == 'No errors':
        sharedMD.releaseLock(request.user.username);
    else:
        sharedMD.logThis(request.user.username, "     VALIDATE_PROJECT found errors: %s " % str(validateResult));
        #http://docs.python.org/library/exceptions.html#exceptions.RuntimeError
        try:
            raise RuntimeError("Project did not validate. Reverting action.")
        except RuntimeError:
            
            sharedMD.logThis(request.user.username, "     Exception raised. ");

        sharedMD.releaseLock(request.user.username);
        sharedMD.logThis(request.user.username, "     Lock cleared. ");    

        #request.user.message_set.create (message="Action did not validate. Please reload page and try again.")
        
    if actionRequest['ajaxAction']== 'fastAdd':
        jRefresh=simplejson.dumps(refreshThese+[newItemTemplate])
        return HttpResponse(jRefresh, mimetype=mimetypex)
        
    else:
        jRefresh=simplejson.dumps(refreshThese)
        return HttpResponse(jRefresh, mimetype=mimetypex)
        

#############################################################################

@login_required 
def uploadItems(request):
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    c = {}
    c.update(csrf(request))
    warning = ''
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            allLines = request.FILES['file'].read().split('\n')
            uploadedFileName = request.FILES['file'].name
            uploadedFileSize = request.FILES['file'].size
            
            
            projectID = form.cleaned_data['projectID']
            sharedMD.logThis(request.user.username,"VIEW: item import, "+str(len(allLines))+" items, project "+str(projectID));            


            ### SECURITY - permission check
            targProjObj = Project.objects.get(pk=projectID)

            if targProjObj.owner != request.user.username:
                request.user.message_set.create (message="You do not have permission to upload to that project.")
                return HttpResponseRedirect('/pim1/uploaditems/') 

 
            isBinary = False
            for lx in allLines:
                if '\0' in lx:
                    isBinary =True

            ## subvert the data to deliver warning messages
            if isBinary:
                request.user.message_set.create (message='WARNING! You attempted to upload binary data. Please upload only simple text files. File: ' + uploadedFileName )
                sharedMD.logThis(request.user.username,'WARNING! Attempt to load binary file. File: ' + uploadedFileName +'  project: '+str(projectID));                     
                return HttpResponseRedirect('/pim1/uploaditems')
            
                ## 50 items is about 2k, min
            elif uploadedFileSize > 30000:
                request.user.message_set.create (message='WARNING! You attempted to upload a file that was too damn big! Try something less ambitious, please.  File: ' + uploadedFileName )
                sharedMD.logThis(request.user.username,' WARNING! Attempt to load large file. File: ' + uploadedFileName +'  project: '+str(projectID));
                return HttpResponseRedirect('/pim1/uploaditems')
            else:

                for thisItemTitle in allLines:
                    lastItemID=sharedMD.getLastItemID(projectID)                
                    clickedItem = Item.objects.get(pk=lastItemID) ## i.e., add it to the bottom

                    newItem=DRAGACTIONS.addItem(request, clickedItem, lastItemID)
                    newItem.title = thisItemTitle
                    newItem.parent='0'
                    newItem.indentLevel='0'
                    newItem.owner = request.user.username
                    newItem.save()

            #return HttpResponseRedirect('/pim1/uploaditems')
        else:
            sharedMD.logThis(request.user.username, "uploaded items: FORM IS INVALID");
            warning = "Form data was invalid, please try again."
    else:
        form = UploadFileForm()
    return render_to_response('pim1_tmpl/upload_items.html', {
        'warning': warning,
        'form':form,
        'pagecrumb':'upload items',
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )
 


#############################################################################
@login_required    
def csvDownload(request, projectID):
              
    sharedMD.logThis(request.user.username, ' csvDownload ==> project:'+ str(projectID))
    
    fhandle=Project.objects.get(pk=projectID).name.replace(' ','_').replace('-','_')
    pnum="%04d" % int(projectID)
    suggestedFilename="P"+pnum+'-'+fhandle+'-'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'.csv'

    targProjObj = Project.objects.get(pk=projectID)

    if targProjObj.owner != request.user.username:
        request.user.message_set.create (message="You do not have permission to access that resource.")
        return HttpResponseRedirect('/pim1/') 
    
    #see: https://docs.djangoproject.com/en/1.2/howto/outputting-csv/
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % suggestedFilename

    writer = csv.writer(response)
    ThisProjItems = Item.objects.filter(project=projectID)
    lx = len(ThisProjItems)
    j=0

    # this array will store item IDs in Outline order for this project
    projItemsIDs=[]
    for i in range(0,lx):
        thisItem=ThisProjItems.get(follows=j)
        projItemsIDs.append(thisItem.id)
        j = thisItem.id
    
    writer.writerow(['id', 'follows', 'parent', 'indent level', 'title', 'project', 'priority', 'status', 'date created', 'last modification date', 'note'])
    
    ## csv module doesn't handle unicode, so must transcode to utf-8 before writing
    for itemID in projItemsIDs:
        x = Item.objects.get(pk=itemID)
        writer.writerow([x.id, x.follows, x.parent, x.indentLevel, x.title.encode('utf-8'), x.project, x.priority, x.status, x.date_created, x.date_mod,  x.HTMLnoteBody.encode('utf-8')])

    return response

#############################################################################
@login_required
@user_passes_test(sharedMD.validate_maint_membership,login_url='/pim1/')

def backupdata(request):
    sharedMD.logThis(request.user.username, "VIEW: backupdata")
    
    # projlist=0 is default value, overridden by passed parameters

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    #BackupTheseProjects = []
    if request.method == 'POST': # If the form has been posted...
        #form = ImportForm(request.POST) # A form bound to the POST data
        #if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        if "BackupTheseProjects" in request.POST:
            sharedMD.logThis(request.user.username, "backup request:"+str(request.POST))

            for reqData in request.POST.lists():
                if reqData[0] == 'BackupTheseProjects':
                    BackupTheseProjects=reqData[1]
                
              
            sharedMD.logThis(request.user.username, ' backup ==> projlist:'+ str(BackupTheseProjects))


            for thisBackupID in BackupTheseProjects:
                count=0
                fhandle=Project.objects.get(pk=thisBackupID).name[:6].replace(' ','_')
                pnum="%03d" % int(thisBackupID)
                filename="P"+pnum+fhandle+'_'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'.bnk'
                ## open in a way that handles UTF-8
                OUTX = codecs.open(BACKUPDIR+filename,'w',encoding='utf-8')
                
                
                # no, gotta save them in outline order, for sanity's sake
                #thisProjItems=Item.objects.filter(project=thisBackupID)

                ThisProjItems = Item.objects.filter(project=thisBackupID)
                lx = len(ThisProjItems)
                j=0

                # this array will store item IDs in Outline order for this project
                projItemsIDs=[]
                for i in range(0,lx):
                    thisItem=ThisProjItems.get(follows=j)
                    projItemsIDs.append(thisItem.id)
                    j = thisItem.id
            
                for tx in projItemsIDs:
                    thisItem=ThisProjItems.get(pk=tx)
                    OUTX.write('@@!! NEW_RECORD =====================================\n')
                    OUTX.write('@@!! ID '+str(thisItem.id)+'\n')
                    OUTX.write('@@!! FOLLOWS '+str(thisItem.follows)+'\n')
                    OUTX.write('@@!! PARENTS '+str(thisItem.parent)+'\n')
                    OUTX.write('@@!! INDENT_LEVEL '+str(thisItem.indentLevel)+'\n')
                    OUTX.write('@@!! SELECTOR '+thisItem.title+'\n')
                    OUTX.write('@@!! PROJECT '+str(thisItem.project)+'\n')
                    OUTX.write('@@!! PRIORITY '+str(thisItem.priority)+'\n')
                    OUTX.write('@@!! STATUS '+str(thisItem.status)+'\n')

                    OUTX.write('@@!! DATE_CREATED '+str(thisItem.date_created)+'\n')
                    OUTX.write('@@!! DATE_MODIFIED '+str(thisItem.date_mod)+'\n')

                    OUTX.write('@@!! DATE_GOO_TASK '+str(thisItem.date_gootask_display)+'\n')
                    OUTX.write('@@!! GOO_TASK_ID '+thisItem.gtask_id+'\n')
                    OUTX.write('@@!! NOTE follows \n')
                    OUTX.write(thisItem.HTMLnoteBody+'\n')

                    count += 1

                sharedMD.logThis(request.user.username, "Project "+str(thisBackupID)+": "+str(count)+" items backed up to "+filename)
                OUTX.close()
            #return HttpResponseRedirect('/serialize/')
    else:
        #form = serializeForm() # An unbound form
        pass




    return render_to_response('pim1_tmpl/serialize.html', {
        'dirlist':dirlist.dirlist(BACKUPDIR),
        'backupdir':BACKUPDIR,
        'titleCrumbBlurb':'serialize/backup',
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )


#############################################################################
@login_required
@user_passes_test(sharedMD.validate_maint_membership,login_url='/pim1/')

def healthcheck(request, proj_id):
    sharedMD.logThis(request.user.username, "VIEW: healthcheck")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)


    proj_id = int(proj_id)

    ### each routine returns an array of tables
    healthTables = []

    healthTables += checkHealth.projectList(request, proj_id);

    healthTables += checkHealth.projectlessItems(request);

    healthTables +=  checkHealth.followerCheck(request, proj_id);
    

    return render_to_response('pim1_tmpl/healthcheck.html', {
        'titleCrumbBlurb':'health check',
        'displayTables':healthTables,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )


###########################################################################

@login_required
def createOrEditProject(request, projID):

    ## projID = 0 means "new project". Otherwise, the ID of the project to edit
    
    sharedMD.logThis(request.user.username, "VIEW: createOrEditProject")

    class addProjectForm(forms.Form):
        # projIDhidden must be optional, b/c for a new form its empty to start
        projIDhidden = forms.IntegerField(widget = forms.HiddenInput, required=False )
        newProjectName =  forms.CharField(max_length = 120, label = "project name")
        newProjectColor = forms.CharField(max_length = 24, label = "background color")
        #newProjectOwner = forms.CharField(max_length = 30)
        newProjProjectSet = forms.ModelChoiceField(queryset = ProjectSet.objects.filter(owner = request.user.username ), label = "project set")
        ## was ....objects.all()
        #newProjProjectSetOwner = forms.CharField(max_length = 30)

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    c = {}
    c.update(csrf(request))	  
 
    if request.method == 'POST': # If the form has been posted...
        form = addProjectForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            if form.cleaned_data.has_key('projIDhidden'):
                projIDhidden = form.cleaned_data['projIDhidden']
            else:
                projIDhidden = 0
            newProjectName = form.cleaned_data['newProjectName']
            newProjectSet = form.cleaned_data['newProjProjectSet']
            newProjectColor = form.cleaned_data['newProjectColor']
            #newProjectOwner = form.cleaned_data['newProjectOwner']

            if projIDhidden == 0:
                sharedMD.logThis(request.user.username,  "creating project: "+newProjectName + "projset = "+str(newProjectSet))

                newProjectObject = Project(name = newProjectName, color = newProjectColor, \
                                           set = newProjectSet, projType = 1, \
                                           owner = request.user.username )
                newProjectObject.save()
             
                newArchiveProj = Project(name = newProjectName + " ARCHIVE", color = "#cccccc",\
                                         set = newProjectSet, projType = 3, \
                                         archivePair = newProjectObject , \
                                         owner = request.user.username )

                newArchiveProj.save()

                newProjectObject.archivePair = newArchiveProj
                newProjectObject.save()

                ### create anchor items for both projects

                npAnchor = '== ' + newProjectObject.name + ' ANCHOR =='
                archAnchor =  '== ' + newArchiveProj.name + ' ANCHOR =='

                newProjItem = Item(title = npAnchor, priority = '0', status = '0', \
                                   follows = 0,  parent = 0, indentLevel = 0, \
                                   project = newProjectObject, \
                                   owner = request.user.username)
                newProjItem.save()

                newArchItem = Item(title = archAnchor, priority = '0', status = '0', \
                                   follows = 0,  parent = 0, indentLevel = 0, \
                                   project = newArchiveProj, \
                                   owner = request.user.username)
                newArchItem.save()
                returnThisID = newProjectObject.id
                return HttpResponseRedirect('/pim1/drag/'+str(returnThisID) ) 
            else:
                sharedMD.logThis(request.user.username,  "editing project: "+str(projIDhidden)+"  "+newProjectName + "projset:"+str(newProjectSet))
                projectToEdit = Project.objects.get(pk=projIDhidden)
                
                projectToEdit.name = newProjectName
                projectToEdit.set = newProjectSet
                projectToEdit.color = newProjectColor
                projectToEdit.save()
                returnThisID = projectToEdit.id
                return HttpResponseRedirect('/pim1/addproject/')

            # Redirect after POST

    else:
        sharedMD.logThis(request.user.username, "    ...building form, projID="+str(projID))
    
        if projID == 0:
            #projData = { 'projIDhidden': 0 , 'newProjectName':'', 'newProjProjectSet':'', 'newProjectColor':''}
            form = addProjectForm() # An unbound form
        else:
            projObj = Project.objects.get(pk=projID)
            projData = {'projIDhidden':projID, 'newProjectName':projObj.name, 'newProjectColor':projObj.color, 'newProjProjectSet':projObj.set.id }
            form = addProjectForm( projData )

    return render_to_response('pim1_tmpl/addProject.html', {
                'form':form,
                'titleCrumbBlurb':'add a new project',
                'current_projs':current_projs,
                'current_sets':current_sets,

                'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
                }, context_instance=RequestContext(request) )


###########################################################################

@login_required
def createOrEditProjectSet(request, projsetID):
    sharedMD.logThis(request.user.username, "VIEW: createOrEditProjectSet")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    c = {}
    c.update(csrf(request))	  
 
    if request.method == 'POST': # If the form has been posted...
        form = addProjectSetForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            if form.cleaned_data.has_key('newProjectSetIDhidden'):
                newProjectSetIDhidden = form.cleaned_data['newProjectSetIDhidden']
            else:
                newProjectSetIDhidden = 0
            newProjectSetName = form.cleaned_data['newProjectSetName']
            newProjectSetColor = form.cleaned_data['newProjectSetColor']


            if newProjectSetIDhidden == 0:
                sharedMD.logThis(request.user.username,  "    creating projectSet: "+newProjectSetName )

                newProjectSetObject = ProjectSet(name = newProjectSetName, \
                                                 color = newProjectSetColor, \
                                                 owner = request.user.username )
                newProjectSetObject.save()
                return HttpResponseRedirect('/pim1/addprojectset')            
             
            else:
                
                sharedMD.logThis(request.user.username,  "    editing projectSet: "+newProjectSetName + "   projset:"+str(newProjectSetIDhidden))
                projectSetToEdit = ProjectSet.objects.get(pk=newProjectSetIDhidden)
                  
                projectSetToEdit.name = newProjectSetName
                #projectSetToEdit.set = newProjectSet
                projectSetToEdit.color = newProjectSetColor
                projectSetToEdit.save()
                
                return HttpResponseRedirect('/pim1/addprojectset')            


    else:
        if projsetID == 0:
            form = addProjectSetForm() # An unbound form
        else:
            projsetObj = ProjectSet.objects.get(pk = projsetID)
            projsetData = {'newProjectSetIDhidden':projsetID, 'newProjectSetName':projsetObj.name, 'newProjectSetColor':projsetObj.color }
            form = addProjectSetForm( projsetData )
            

    return render_to_response('pim1_tmpl/addProjectset.html', {
                'form':form,
                'titleCrumbBlurb':'add a new project set',
                'current_projs':current_projs,
                'current_sets':current_sets,

                'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
                }, context_instance=RequestContext(request) )


######################################################################
@login_required
@user_passes_test(sharedMD.validate_maint_membership,login_url='/pim1/')

def maintPage(request, pLockRequest):
    sharedMD.logThis(request.user.username, "VIEW: maintPage")
    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)


    if pLockRequest == "clearlock":
        lockActionStatus = sharedMD.releaseLock(request.user.username)

    lockMessage=sharedMD.testLock(request.user.username)

    logLineText = ''
    logLines = sharedMD.tailLog(30);
    for llt in logLines:
        if  ('ERROR') in llt:
            llt = '<span class="error">'+llt+'</span>';
        elif ('WARNING') in llt:
            llt = '<span class="warn">'+llt+'</span>';
        elif ('BAD LAST') in llt:
            llt = '<span class="badlast">'+llt+'</span>';
    
        logLineText += llt +'<br/>' ;
        
    return render_to_response('pim1_tmpl/maint.html', {
        'titleCrumbBlurb':'maint page',
        'current_projs':current_projs,
        'current_sets':current_sets,
        'lockMsg':lockMessage,
        'logLines':logLineText,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )

######################################################################
@login_required
@user_passes_test(sharedMD.validate_maint_membership,login_url='/pim1/')

def linearizePage(request, flattenMe):
    sharedMD.logThis(request.user.username, "VIEW: linearizePage, proj=%s" % flattenMe)
    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    if flattenMe != "0":
        ### flatten project flattenMe
        allItems = Item.objects.filter(project = flattenMe).order_by('follows')

        firstRegular = True
        for ix in allItems[1:]:  ## anchor should be first, skip that one.
            if firstRegular:
                firstRegular = False
                ix.follows = allItems[0].id
                ix.save()
                ixLast = ix
            else:
                ix.follows = ixLast.id
                ix.parent = 0;
                ix.indentLevel = 0;
                ix.save()
                ixLast = ix;

        sharedMD.logThis(request.user.username, "     Completed linearizePage, proj=%s" % flattenMe)

        return HttpResponseRedirect('/pim1/drag/'+str(flattenMe)) 


    return render_to_response('pim1_tmpl/linearize.html', {
        'titleCrumbBlurb':'linearize page',
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )

######################################################################
@login_required
def managePage(request, pLockRequest):
    sharedMD.logThis(request.user.username, "VIEW: managePage")
    request.session['viewmode'] = 'managePage'

    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    if pLockRequest == "clearlock":
        lockActionStatus = sharedMD.releaseLock(request.user.username)

    lockMessage=sharedMD.testLock(request.user.username)

        
    return render_to_response('pim1_tmpl/manage.html', {
        'titleCrumbBlurb':'maint page',
        'current_projs':current_projs,
        'current_sets':current_sets,
        'lockMsg':lockMessage,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )

###########################################################################




@login_required
def today(request):

    sharedMD.logThis(request.user.username, "VIEW: today")
    request.session['viewmode'] = 'today'


    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)
    
    #current_projs = Project.objects.filter(projType=1).order_by('name')
    #current_sets = ProjectSet.objects.all()

    todayIDs = Item.objects.filter(priority__gte=1, priority__lt=3).filter(project__projType=1, owner = request.user.username).values_list('id', flat=True).order_by('project__name', 'priority')

    displayList =  buildDisplayList(current_projs,0,'provided',0,todayIDs)

    titleCrumbBlurb = "TODAY "
    return render_to_response("pim1_tmpl/items/psd.html", {

        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,
        'targetProject':0,
        'pSort':'project',
        'titleCrumbBlurb':titleCrumbBlurb,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")        
        }, context_instance=RequestContext(request) )



###########################################################################
# showChains
#               provide user interface to link un-linked segments

@login_required
def showChains(request, proj_id):
    sharedMD.logThis(request.user.username, "VIEW: showchains")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    thisProjItems=Item.objects.filter(project__id = proj_id);

    ## the start of each chain is its endpoint - an item with no followers.
    ##   chain with the anchor is chain 0
    ## the chain is built back from there, for each endpoint.
 
    ### need to duplicate logic from getLastItemId (since calling that
    ### leaves a lock open, logs errors, etc

    allFollows=Item.objects.filter(project=proj_id).values_list('follows', flat=True)
    allinProj=Item.objects.filter(project=proj_id).values_list('id', flat=True)


    lastItemIDs = []
    for itemx in thisProjItems:
        if itemx.id not in allFollows:
            lastItemIDs.append(itemx.id)

    sharedMD.logThis(request.user.username,  "ShowChains: Proj "+ str(proj_id) +"======================================")
    sharedMD.logThis(request.user.username,  "            Found these un-followed items: "+ str(lastItemIDs))
    noFollowers = Item.objects.filter(id__in = lastItemIDs);


    ##build chain display tables ################################

    displayTables = []
    anchor= Item.objects.get(project__id = proj_id, follows=0);

    # values_list doesn't return a normal array, consequently
    # .count() is buggy, so we trasfer to a normal array
    remainingIDs =  [];
    remainingIDs += allinProj;

    ix = anchor
    chainEnd = False;
    outx = '<table><tr><th colspan="3">chain 0</th></tr>';
    
    while not chainEnd:
        outx += '<tr class="chainTableRow"><td>%s</td><td>%s</td><td>%s/%s:%s</td></tr>' % (ix.id,  ix.parent, ix.follows, ix.indentLevel, ix.title)
        remainingIDs.remove(ix.id)
        
        try:
            follows_ix = Item.objects.get(follows=ix.id)
            ix = follows_ix
        except:
            #sharedMD.logThis(request.user.username, str(sys.exec_info()))
            outx += "<tr><td colspan='3'>error getting follower of %s, error: %s</td></tr>" % (ix.id, str(sys.exc_info()));
            mfString = '';
            multiFollows = Item.objects.filter(follows = ix.id)
            
            for k in multiFollows:
                mfString += '['+str(k.id) + ":" + k.title[:50] + '],';
            
            outx +="<tr><td colspan='3'>followers of ix.id are: %s</td></tr>" % mfString[:-1];
            chainEnd = True;

    outx += '</table>';


    displayTables.append(outx);


    #####################################################
    # first try: just list all of the items not in chain 0

    outx = ''
    outx += '<h4>items not in chain 0</h4>\n<table>'

    for rid in remainingIDs:
        r = Item.objects.get(id=rid);
        outx += '<tr><td>%s</td><td>%s</td><td>%s/%s:%s</td></tr>' % (r.id, r.title, r.follows, r.parent, r.indentLevel)

    outx += '</table>';

        
    displayTables.append(outx);


    #########################################################################
    # again, with follower order intact
    # working from LAST ITEMS backward

    outx = '<hr/>'
    outx += '<h4>item chains, derived by endpoint </h4>\n'

    # take the items with no followers, and GO BACKWARDS from them
    # that would be one chain per no-follower items
    # Most of the time, the segments will all chase back to the anchor
    # could then potentially create one segment that has all of the items automatically

  


    ix = anchor
    tableID = 0
    tables = []
    for endPoint in noFollowers:

        outx += '<table><tr><th colspan="5">endpoint for segment: %s %s' % (endPoint.id, endPoint.title);
        outx += '<tr><th>id</th><th>parent</th><th>follows</th><th>indent</th><th>title</th></tr>'
        chainEnd = False;
        ix = endPoint
        outputRows = []
        #tables.append([])
        thisRun = []
        while not chainEnd:
            outputRows.append('<tr class="chainTableRow"><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (ix.id,  ix.parent, ix.follows, ix.indentLevel, ix.title) )
            thisRun.append(ix.id)
            try:
                ix = Item.objects.get(id=ix.follows);
                
            except:
                #sharedMD.logThis(request.user.username, str(sys.exec_info()))
                outx += "<tr><td colspan='5'>error getting preceeder of %s, error: %s</td></tr>" % (ix.id, str(sys.exc_info()));
                mfString = '';
                multiFollows = Item.objects.filter(follows = ix.id)
                
                for k in multiFollows:
                    mfString += '['+str(k.id) + ":" + k.title[:50] + '],';
                    
                    outx +="<tr><td colspan='5'>followers of ix.id are: %s</td></tr>" % mfString[:-1];
                    chainEnd = True;

        thisRun.reverse()
        tables.append(thisRun)
        
        outputRows.reverse()
        for row in outputRows:
            outx += row;
        outx +=  '</table>'
        displayTables.append(outx);

        outx = ''
        #### calculate a recommended chain

    recommendedResult = []

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ### make sure tables[0][0] is anchor, if not move the chain continaing the
    ### anchor over to [0]
    
    if tables[0][0] != anchor.id:
        anchorHere = 999; ## if ever this generates an error, we've lost the nachor
        indexCount = -1
        for tx in tables:
            indexCount += 1;
            if tx[0] == anchor.id:
                anchorHere = indexCount

        if anchorHere == 999:
            sharedMD.logThis(request.user.username, "             ERROR! Anchor missing from tables array, or not in position 0")
            exit();
        elif anchorHere == 0:
            sharedMD.logThis(request.user.username, "             ...anchor in chain 0...")
        else:
            arrayContainingAnchor = tables.pop(anchorHere)
            tables.insert(0, arrayContainingAnchor)
            sharedMD.logThis(request.user.username, "             ...anchor moved from chain %s to chain 0..." % anchorHere)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
            
    
    for cx in range(0, len(tables)-1):
        
        ##select each value in the first table
        for j in tables[cx]:
            for k in range(cx+1, len(tables)):
                
                
                if j in tables[k]:
                    tables[k].remove(j)
                
    sharedMD.logThis(request.user.username, "            Tables w/dupes removed:" + str(tables))


    outx += '<hr/>'
    if len(tables) > 1:
        outx += '<h4>tables with dupes removed</h4>';

        for i in (0, len(tables)-1):
            outx += "<p>%s: %s</p>" % (i, tables[i]);
            recommendedResult += tables[i];

        outx += "<p>Recommended fix: " + str(recommendedResult)+'</p>';

        outx += '<a href="/pim1/repairchain/'+ proj_id +'">execute this repair</a>'

        displayTables.append(outx);

    else:
        outx += '<p><strong>SUMMARY: No chain errors found.</strong></p>'
        displayTables.append(outx);
    
    displayTables.append("\n<p>fin</p>"); 
    #######################################################

    return render_to_response("pim1_tmpl/showchains.html", {

        'displayTables':displayTables, 
        'current_projs':current_projs,
        'current_sets':current_sets,
        'noFollowers':noFollowers,
        'recommendedList':str(recommendedResult)[1:-1],
        'titleCrumbBlurb':'showchain proj:'+str(proj_id),
        'proj_id':proj_id,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        
        }, context_instance=RequestContext(request) )


###########################################################################
# repairChain
#               repairs un-linked segments. naively.

@login_required
def repairChain(request, proj_id):
    sharedMD.logThis(request.user.username, "VIEW: repairchain")

    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    # CHANGES HERE MUST BE INCORPORATED INTO SHOWCHAINS and vice versa,
    # until we re-factor
    anchor= Item.objects.get(project__id = proj_id, follows=0);
    thisProjItems=Item.objects.filter(project__id = proj_id);
    allFollows=Item.objects.filter(project=proj_id).values_list('follows', flat=True)
    #allinProj=Item.objects.filter(project=proj_id).values_list('id', flat=True)


    lastItemIDs = []
    for itemx in thisProjItems:
        if itemx.id not in allFollows:
            lastItemIDs.append(itemx.id)
    
    noFollowers = Item.objects.filter(id__in = lastItemIDs);

    ix = anchor
    tableID = 0
    tables = []
    for endPoint in noFollowers:

        chainEnd = False;
        ix = endPoint
        outputRows = []

        thisRun = []
        while not chainEnd:
            thisRun.append(ix.id)
            try:
                ix = Item.objects.get(id=ix.follows);
                
            except:
                chainEnd = True;

        thisRun.reverse()
        tables.append(thisRun)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ### make sure tables[0][0] is anchor, if not move the chain continaing the
    ### anchor over to [0]
    
    if tables[0][0] != anchor.id:
        anchorHere = 999; ## if ever this generates an error, we've lost the nachor
        indexCount = -1
        for tx in tables:
            indexCount += 1;
            if tx[0] == anchor.id:
                anchorHere = indexCount

        if anchorHere == 999:
            sharedMD.logThis(request.user.username, "             ERROR! Anchor missing from tables array, or not in position 0")
            exit();
        elif anchorHere == 0:
            sharedMD.logThis(request.user.username, "             ...anchor in chain 0...")
        else:
            arrayContainingAnchor = tables.pop(anchorHere)
            tables.insert(0, arrayContainingAnchor)
            sharedMD.logThis(request.user.username, "             ...anchor moved from chain %s to chain 0..." % anchorHere)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    recommendedResult = []
    for cx in range(0, len(tables)-1):
        
        ##select each value in the first table
        for j in tables[cx]:
            for k in range(cx+1, len(tables)):
                if j in tables[k]:
                    tables[k].remove(j)
                    
    if len(tables) == 1:
        sharedMD.logThis(request.user.username, "            TABLE HAS ONLY 1 CHAIN. Aborting");
    else:
        
        for i in (0, len(tables)-1):
            recommendedResult += tables[i];


        sharedMD.logThis(request.user.username, "RepairChain: Proj " + str(proj_id) + "===================================")
        sharedMD.logThis(request.user.username, "            recommendedResult:" + str(recommendedResult))
        sharedMD.logThis(request.user.username, "            Starting rechaining....anchor="+str(anchor.id));
        

        ##recommendedResult removes duplicate items across chains.
        ##That means we can't just chain first-to-last across chains, we have to
        ##relink the entire list. Otherwise entire duplicate sections could remain


        # start by skipping the first item, which should be the anchor.
        for index in range(1, len(recommendedResult)):
            item = Item.objects.get(id = recommendedResult[index])
            item.follows = recommendedResult[index - 1]
            item.save()



    return HttpResponseRedirect('/pim1/showchains/'+str(proj_id)) 

######################################################################
@login_required
def help(request, helpSection):
    sharedMD.logThis(request.user.username, "VIEW: help")
    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    
    helptarget = 'pim1_tmpl/help.html'+helpSection
    
    return render_to_response(helptarget, {
        'titleCrumbBlurb':'help',
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )
#######################################################
@login_required
def profilePage(request):
    sharedMD.logThis(request.user.username, "VIEW: profile")
    
    current_projs = Project.objects.filter(projType=1).filter(owner = request.user.username).order_by('name')
    current_sets = ProjectSet.objects.filter(owner = request.user.username)

    

    
    return render_to_response('pim1_tmpl/profile.html', {
        'titleCrumbBlurb':'user home',
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )

