################################################################
## views.py
################################################################

### to clear out ex. all but item 1, for reloading
##  ex., Item.objects.filter(project=1).exclude(id = 1).delete()

from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext

from django import forms
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
#from django.forms.models import modelformset_factory 

# ++ was "pengine.models"
from pim1.pengine.models import Item, Project, ProjectSet

import datetime, sys, simplejson, codecs

#D410 sys.path.append('C:\\Documents and Settings\\Owner\\My Documents\\Python\\library');
#D610 #sys.path.append('C:\\Documents and Settings\\Bernard Hecker\\My Documents\\python\\lib')
#Battlestar
#sys.path.append('C:\\Users\\Bernard\\Documents\\python64\\library');

#DreamHost - UNIX
sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/library');

import gooOps, dirlist, south;
from rfc3339 import rfc3339;

import drag_actions, sharedMD, checkHealth;

#import test1;


LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'
IMPORTDIR='/home/bhadmin13/dx.bernardhecker.com/pim1/benk_imports/'
BACKUPDIR='/home/bhadmin13/dx.bernardhecker.com/pim1/benk_backups/'

## https://docs.djangoproject.com/en/1.2/topics/forms/
## https://docs.djangoproject.com/en/1.3/intro/tutorial04/
class ImportForm(forms.Form):
    fileToImport=forms.CharField(max_length=300)
    projectToAdd=forms.IntegerField()

class ssearchForm(forms.Form):
    searchfx=forms.CharField(max_length=200)

DRAGACTIONS=drag_actions.dragOps();

@csrf_protect


##################################################################
def homepage(request):
    current_projs = Project.objects.filter(projType=1)
    current_sets = ProjectSet.objects.all()
    c = Context({'home_page':'homepage',
                 'current_projs':current_projs,
                 'current_sets':current_sets,
                 'nowx':datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")})
    t = loader.get_template('pim1_tmpl/home_page.html')
    return HttpResponse(t.render(c))
##################################################################

def itemlist(request,proj_id):
    sharedMD.logThis("Entering itemlist <==============ProjID ="+str(proj_id)+". ")
    
    ##current_items=Item.objects.all()
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()
    
    displayList = buildDisplayList(current_projs, proj_id,'follows',0,[])
    projObj = Project.objects.get(pk=proj_id)

    titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"

    t = loader.get_template('pim1_tmpl/items/index.html')
                       
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs, 
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':titleCrumbBlurb,
        'thisSet':projObj.set.id,
        'current_sets':current_sets,

    })
    return HttpResponse(t.render(c))
##################################################################
def allMyChildren(targetID, resultList):
    sharedMD.logThis("Entering allMyChildren <====================")

    children= Item.objects.filter(parent=targetID)
    for cx in children:
        resultList.append(cx.id)
        allMyChildren(cx.id, resultList)
    
    return(resultList)    

##################################################################

def hoistItem(request,pItem):
    ## hoistList takes a target item ID
    ## and builds an array of all of its children
    ##   1. can't just truncate, or you get the entire rest of the file
    ##   2. need to find all children, and then draw children and their children
    ## Fourth buildlist arg is hoist ID #. BuildDisplayList calls allMyChildren
    hoistID=pItem
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    hoistProj=Item.objects.get(pk=hoistID).project_id 

    projObj = Project.objects.get(pk=hoistProj)

    titleCrumbBlurb = str(hoistProj)+':'+projObj.name+"   ("+projObj.set.name+")"


    
    displayList=buildDisplayList(current_projs, hoistProj, 'follows', hoistID,[])


    t = loader.get_template('pim1_tmpl/items/dragdrop.html')
 
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': str(pItem)+"Hoist",
        'pItem':pItem,
        'projectNum':hoistProj,
        'titleCrumbBlurb':titleCrumbBlurb,
    })
    return HttpResponse(t.render(c))




##################################################################
def buildDisplayList(projectx, projID, ordering, hoistID, useListIDs):
    sharedMD.logThis("Entering buildDisplayList <=====")

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
    sharedMD.logThis("..queries done...")


    parentList=[] ## list of all items that are parents
    for px in items2List:
        if px.parent not in parentList: parentList.append(px.parent)

    ###SLOW BLOCK BEGINS########################################################################
        
    sharedMD.logThis("....parent list built...")
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
        #if ix.parent==0: pzero.append(ix) // commented out 12/17/2011

        ## inControl uses a triangle for parents, dots for others
        if ix.id in parentList:
            ix.outlineBullet="+"
            ix.isParent=True 
        else:
            ix.outlineBullet="&bull;"
            ix.isParent=False
            

    sharedMD.logThis( ".....ix built.....")

    displayList=[]
    followHash={}
    
    if ordering=='follows':
        ## generate outline-ordered and formatted output list
        for f2 in ixList:
            if followHash.has_key(f2.follows): 
                sharedMD.logThis( "=====> WARNING!! followHash duplicate")
                fh1=Item.objects.get(pk=followHash[f2.follows])
                sharedMD.logThis("=====>ID:"+str(fh1.id)+":" + str(fh1) +"  follows=" + str(fh1.follows)+']')
                sharedMD.logThis("=====>ID:"+str(f2.id)+":" + str(f2) +"  follows=" + str(f2.follows)+']\n')

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
            sharedMD.logThis("FHK is="+str(fhk))
            followHash[0]=followHash[fhk]
            followHash.pop(fhk)
            ###sharedMD.logThis('new followhash'+str(followHash))
            
        currentID = 0

        sharedMD.logThis("...built followhash....")

        ## OK, now follow the chain of who follows whom, starting with whoever follows Parent ID = 0
        while  followHash.has_key(currentID):
            displayList.append(jxHash[followHash[currentID]])
            currentID=followHash[currentID]

        # theoretically, having no followHash key for currentID means you're on the last item
        # but beware re: data integrity / lost items
        sharedMD.logThis(".....displayList built...")
    else:

        displayList=ixList
    sharedMD.logThis("Exiting buildDisplayList ========>")
    return(displayList)
##################################################################

def countIndent(anItem):
    
    indentCount=0
    
    while anItem.parent != 0: 
        indentCount+=1
        if anItem.parent !=0:
            anItem=Item.objects.get(pk=anItem.parent)
            
    return(indentCount)
##################################################################


def actionItem(request, pItem, action):
    #sharedMD.logThis( "item "+ pItem + " to " + action);
    #sharedMD.logThis( "actionItem request:" + str(request))

    if request.is_ajax():
        sharedMD.logThis( "AJAX request,item " + pItem + " to " + action);
        ajaxRequest = True
    else:
        sharedMD.logThis( "Not an AJAX request"+ pItem + " to " + action);
        ajaxRequest = False

    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    
    clickedItem = Item.objects.get(pk=pItem)
    clickedProjNum=clickedItem.project.id
    lastItemID=sharedMD.getLastItemID(clickedProjNum)

    origlastKidofCI,origkidList=sharedMD.findLastKid(clickedItem,lastItemID)
        
    #assigning project [many to many]...convoluted?.... 
    projIDc=clickedItem.project.id
    projObjc=Project.objects.get(pk=projIDc)


    ### ADD ###################################################################
    
    ## find the item that was following pItem
    if action=='add':
        try:
            oldFollower = Item.objects.get(follows=pItem)
            follower=True
        except:
            sharedMD.logThis( "Item has no follower: ID" + str(pItem))
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
            
            sharedMD.logThis( "===pItem, lastItemID============"+str(pItem)+ '  '+str(lastItemID)+"==============")
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
            sharedMD.logThis( "Can't demote further, item "+str(clickedItem.id))
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
            sharedMD.logThis( "CAN'T PROMOTE TOP-LEVEL "+ str(pItem))

        else:
            ### Deal with parent assignments first
            
            sharedMD.logThis("Promoting: " +str(clickedItem.id))
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
                sharedMD.logThis("converting subsequent items to children...")
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
                sharedMD.logThis("k-promote: LastKidID="+str(lastKidID))
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
            sharedMD.logThis( "CAN'T MOVE UP TOP item "+ str(pItem))
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
            sharedMD.logThis( "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
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
        sharedMD.logThis( "===WARNING!=========== Unknown action=" + action)
        exit()

    ###########################################################################
    ## let's restrict default view to the clicked item project
        
    sharedMD.logThis( "Action done. current project #"+str(clickedProjNum)+ " " +\
             current_projs.get(pk=clickedProjNum).name + "Ajax:"+str(ajaxRequest))

    if not ajaxRequest:
        displayList = buildDisplayList(current_projs,clickedProjNum, 'follows',0,[])

        #t = loader.get_template('pim1_tmpl/items/index.html')
        #t = loader.get_template('/drag/'+str(clickedProjNum)+'/#'+str(pItem))
        t = loader.get_template('pim1_tmpl/items/dragdrop.html')

        projObj = Project.objects.get(pk=proj_id)
    
        titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"

        c = Context({
            'current_items':displayList,
            'current_projs':current_projs, 
            'current_sets':current_sets,

            'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
            'pagecrumb': titleCrumbBlurb,
            'pItem':pItem,
            'projectNum':clickedProjNum,
        })
        return HttpResponse(t.render(c))
    else:
        ## for all of these operations, we may need to refresh CI, ci.follows, ci.parent, ci children, the item that follows CI
        return (clickedItem.id)


#####################################################(end of actionItem)########


def psd(request,pSort):
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    if pSort=='goo_date': pSort='date_gootask_display'
    # priority, status, date_mod, date_created

    if pSort=='date_created' or pSort=='date_mod': 
        pSort="-"+pSort
    elif  pSort=="date_gootask_display":
        pSort="-"+pSort

    displayList =  buildDisplayList(current_projs,'0',pSort,0,[])


    t = loader.get_template('pim1_tmpl/items/psd.html')
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'pSort':pSort,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
    })
    return HttpResponse(t.render(c))

###################################################################

def gridview(request):
    ITEMS_PER_CELL = 10;
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    displayList = [] ; 

    for thisProject in current_projs:
        cellItems = [];
        #(projlist, projID, ordering, hoistID, useList)
        j = 0 ; ##Item.objects.filter(project=thisProject.id).get(follows=0).id

        limit = min(ITEMS_PER_CELL, Item.objects.filter(project=thisProject.id).count());
        # count() is more efficienrt than 
        cellobjs=Item.objects.filter(project=thisProject).exclude(status='9').exclude(priority=0, follows=0).order_by('priority')
        #### removed from line above 1/27/2012[:10]
        
        #### WORKAROUND until we change model, which currently has a "choice" of '' for priority=0
        #### which makes it sort high, rather than low on the gridview cell

        #for priorityLevel in (1,2,3,4,5,6,7,8,9,99,0):
        #    for itemz in cellobjs:
        #        if (itemz.priority == priorityLevel):
        ###            cellItems.append(itemz.id)
        # that sucker ends up pulling ALL items into the grid, I have no freakin'idea why.
        # something about querysets I don't understand (likely) or Possible django bug.

        ### routine to generate a list of IDs in a specific priority order. Here, makes un-prioritized items sort lower
        ### than prioritized items. Makes use of "provided" ordering in builddisplaylist()
        priorityCollector={}

        for citem in cellobjs:
            if not priorityCollector.has_key(citem.priority):
                priorityCollector[citem.priority]=[]
            priorityCollector[citem.priority].append(citem.id)

        for priorityLevel in (1,2,3,4,5,6,7,8,9,99,0,''):
            if priorityCollector.has_key(str(priorityLevel)):
                cellItems += priorityCollector[str(priorityLevel)]
                
        #for co in cellobjs:
        #    cellItems.append(co.id)

        #         get=Item.objects.filter(project=thisProject).get(follows=j)
        
        #for i in range(0,limit):
            #was 2012/1/2########################
            #thisItem=Item.objects.filter(project=thisProject).get(follows=j)
            #cellItems.append(thisItem.id)
            #j = thisItem.id
            #####################################

            #thisItem=Item.objects.filter(project=thisProject).get(follows=j)
            ### priority can be '', which causes it to sort wrong
            ##if thisItem.priority == '':
            ##    thisItem.priority = 99
            
            # #        cellObjects = Item.objects.filter(project=thisProject.id).order_by('follows')[:ITEMS_PER_CELL]
            # #        for c in cellObjects:
            # #            cellItems.append(c.id)
            #         #sharedMD.logThis("Gridview  thisProject.id:"+str(thisProject.id)+" "+str(cellItems))
            
            # was dx =   buildDisplayList(current_projs,thisProject.id, 'follows',0,cellItems)

        sharedMD.logThis("cellitems:"+str(cellItems))

        dx =   buildDisplayList(current_projs,thisProject.id, 'provided',0,cellItems)
        displayList = displayList + dx


        

    t = loader.get_template('pim1_tmpl/items/gridview.html')
    c = Context({
        'titleCrumbBlurb':'grid view',
        'displayList':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,
        
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")

    })
    return HttpResponse(t.render(c))

##################################################################

def detailItem(request,pItem):
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()


    ix=Item.objects.get(pk=pItem)
    #get project to where it can be displayed; was project_s
    ###ix.project=ix.project 

    projObj = Project.objects.get(pk=ix.project.id)

    titleCrumbBlurb = str(ix.project.id)+':'+projObj.name+"   ("+projObj.set.name+")"


    displayList=[ix]

    t = loader.get_template('pim1_tmpl/items/itemDetail.html')
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'item detail',
        'thisSet': ix.project.set.id
    })
    return HttpResponse(t.render(c))

##################################################################

def gooTaskUpdate(request):
    benkId = u'MDA5MTI3NjgzODg0MDUzMjk1MTI6MTk1Mjg0MjA0Mzow'
    GOOTASK=gooOps.gooOps()
    serviceConn=GOOTASK.taskAPIconnect()

    ## get tasks from  tasklist=benk from google
    gootasks = serviceConn.tasks().list(tasklist=benkId).execute()
    gooTaskIdList=[]

    for g in gootasks['items']:
        gooTaskIdList.append(g['id'])

    sharedMD.logThis( "gooTaskIdList="+str(gooTaskIdList))

    ## update all items that have google task display dates
    pushableItems=Item.objects.filter(date_gootask_display__gte=datetime.date(2000, 1, 1))
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
    
    t = loader.get_template('pim1_tmpl/items/psd.html')
    c = Context({
        'pSort':'-date_gootask_display',
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': "Google task date sort"
    })
    return HttpResponse(t.render(c))

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

def ssearch(request):
    sharedMD.logThis("Entering ssearch <====================")

    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    c = {}
    c.update(csrf(request))
    error_message=''
    searchTerm=''
     
    if request.method == 'GET':
        sform = ssearchForm(request.GET)
        if sform.is_valid():
            searchTerm=sform.cleaned_data['searchfx']
            sharedMD.logThis("Search term="+searchTerm)

            ## Execute the search ##
            ## get the querySets
            titleHits=Item.objects.filter(title__icontains=searchTerm)
            noteHits=Item.objects.filter(HTMLnoteBody__icontains=searchTerm)
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

    t = loader.get_template('pim1_tmpl/items/index.html')
    c = Context({
        'searchterm':searchTerm,
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'titleCrumbBlurb':'search result',
        'error_message':error_message,
        'is_search_result':'true'
    })
    return HttpResponse(t.render(c))
            

#############################################################################

def addItem(request, pItem):

    clickedItem=Item.objects.get(pk=pItem)
    lastItemID=sharedMD.getLastItemID(clickedItem.project_id)
    newItem=DRAGACTIONS.addItem(clickedItem, lastItemID)
    sharedMD.logThis('edit new item: ' + str(newItem.id))
    #follow does not work, no idea why
    return HttpResponseRedirect('/pim1/item/edititem/'+str(newItem.id))

#############################################################################

def editItem(request, pItem):
    itemProject = Item.objects.get(pk=pItem).project_id
    projectName = Project.objects.get(pk=itemProject).name

    #dispPage, dispStart, dispLength):
    # dispPage, dispStart and dispLength allow us to restore the listing page to what it was
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()


    # model formsets
    ###https://docs.djangoproject.com/en/1.2/topics/forms/modelforms/#using-a-model-formset-in-a-view
    
    itemFormSet = forms.models.modelformset_factory(Item, max_num=0, exclude=('IS_import_ID','date_gootask_display', 'gtask_id', 'project'))

    
    ## "field" and "exclude" operands supported

    if request.method == 'POST':
        formset=itemFormSet(request.POST, request.FILES)
        changedInstances=formset.save()
        sharedMD.logThis("Formset saved: "+str(changedInstances))

        ## POST completed, now redirect to the reconstructed view
        return HttpResponseRedirect('/pim1/drag/'+str(itemProject)+'/#'+str(pItem))
    
    else:
        formset = itemFormSet(queryset=Item.objects.filter(pk=pItem))


        formsetOut = formset.as_table()
        sharedMD.logThis("Formset generated, pItem="+str(pItem))
        ##sharedMD.logThis(formsetOut)
        
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

def importfile(request):

    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    c = {}
    c.update(csrf(request))	  
 
    if request.method == 'POST': # If the form has been posted...
        form = ImportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            fileToImport=form.cleaned_data['fileToImport']
            projectToAdd=form.cleaned_data['projectToAdd']
            sharedMD.logThis( "fileToImport="+fileToImport)
            sharedMD.logThis( "projectToAdd="+str(projectToAdd))

            sharedMD.logThis( "+++ departing to importISdata")
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

def importISdata(importFile,newProjectID):

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

    sharedMD.logThis( ">>> importISdata from " + IMPORTDIR + importFile)
    
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
                        sharedMD.logThis("  Import: currentISid="+str(currentISid)+"  ISparentFirst="+str(ISparentFirst))
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
                        newItem.indentLevel=countIndent(newItem)
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
                sharedMD.logThis('Date_created:'+str(read_date_created)+' ['+str(id)+']')

            elif itemType == 'DATE_MODIFIED':
                read_date_mod = data;
                sharedMD.logThis('Date_modified:'+str(read_date_mod))

            elif itemType == 'DATE_GOO_TASK':
                read_date_goo_task = data;
                sharedMD.logThis('read_date_goo_task:'+str(read_date_goo_task))

            elif itemType == 'GOO_TASK_ID':
                read_goo_task_id = data; 


            elif itemType == 'NOTE':
                # nothing to do here. We're accumulating all row bodies that do not start
                # with the marker, and then dumping them when we hit a NEW_RECORD
                pass;

            else:
                sharedMD.logThis( "* * RECORD TYPE MISSED * *:"+ str(lx))
    newItem.save()
    importedRecordIDs.append(newItem.id)

    ### now clear out all the IS_import_ID's to make way for future imports
    for importID in importedRecordIDs:
        cleanUp=Item.objects.get(pk=importID)
        cleanUp.IS_import_ID=-999
        cleanUp.save()

    sharedMD.logThis(">>> Completed. # of imported records: " + str(numberOfRecordsImported))
    
##################################################################

def draglist(request, proj_id):
    sharedMD.logThis("Entering drag list <=========, Project="+str(proj_id))
    
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    displayList = buildDisplayList(current_projs, proj_id,'follows',0,[])


    projObj = Project.objects.get(pk=proj_id)

    titleCrumbBlurb = str(proj_id)+':'+projObj.name+"   ("+projObj.set.name+")"


    t = loader.get_template('pim1_tmpl/items/dragdrop.html')
                       
    c = Context({
        'titleCrumbBlurb':titleCrumbBlurb,
        'current_items':displayList,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'thisSet':projObj.set.id,


    })
    return HttpResponse(t.render(c))

######################################################################
def xhr_test(request):
    myRequest=request.GET
    sharedMD.logThis("xhr_test entered........")

    sharedMD.logThis("request.GET="+str(myRequest))

    a=[(1,11),(2,22),(3,33),(4,44), (5,55)]
    jsona=simplejson.dumps(a)
    
    message = 'nix'
    if request.is_ajax():
        message = "Request is from AJAX"
        
    else:
        message = "not ajax"
    sharedMD.logThis("xhr_test, message="+message)
    
    mimetypex = 'application/javascript'
    return HttpResponse(jsona,mimetype=mimetypex)

#(r'^xhr_test$','your_project.your_app.views.xhr_test'),
######################################################################
def xhr_actions(request):

    mimetypex = 'application/javascript'
    sharedMD.logThis('Entering xhr_actions...')
    
    actionRequest=request.GET
    message = 'nix'
    
    if request.is_ajax():
        message = "AJAX request, ci="+str(actionRequest['ci'])+"  ti='"+str(actionRequest['ti']+"'  ajaxAction: "+actionRequest['ajaxAction'])
    else:
        message = "Not an AJAX request"

    sharedMD.logThis("=====> xhr_actions: ="+message)

    ## dragmove should also get refactored to the external library
    clickedItem=Item.objects.get(pk=actionRequest['ci'])

    lastItemID=sharedMD.getLastItemID(clickedItem.project_id)

    #lastKid,kidList=findLastKid(clickedItem,lastItemID)

    ## to dragmove #################################

    if actionRequest['ajaxAction'] == 'dragmove':
        refreshThese= drag_move(int(actionRequest['ci']), int(actionRequest['ti']))
    
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

    else:
        sharedMD.logThis("+++ERROR+++. Uncaught actionRequest['ajaxAction']:"+actionRequest['ajaxAction'])
        refreshThese=[]

    #sharedMD.logThis("  REFRESH: "+str(refreshThese))
    jRefresh=simplejson.dumps(refreshThese)
    return HttpResponse(jRefresh, mimetype=mimetypex)
        

######################################################################
def drag_move(CIid, TIid):
    # clicked item ID, target item ID

    CI=Item.objects.get(pk=CIid)
    TI=Item.objects.get(pk=TIid)
    sharedMD.logThis(" ====dragmove=> CIid:TIid    "+str(CIid)+":"+str(TIid))
    
    if CI.follows == TI.id:
        ## invalid move
        sharedMD.logThis('== WARNING: move of item onto item it follows is invalid. Not executing.')
        return([])

 
    lastItemID=sharedMD.getLastItemID(CI.project_id)

    origCIparent=CI.parent
    origCIfollow=CI.follows

    origTIparent=TI.parent
    origTIfollow=TI.follows

    targetFollower = Item.objects.get(follows=TIid)

    lastKidID,kidList=sharedMD.findLastKid(CI, lastItemID)

    ## stitch up the item that followed the CI (or its last kid), and the one that preceded it
    if CIid != lastItemID and lastKidID != lastItemID:
        if lastKidID == 0:
            followedCIorKid = Item.objects.get(follows=CIid)
        else:
            followedCIorKid = Item.objects.get(follows=lastKidID)
        followedCIorKid.follows = origCIfollow
        followedCIorKid.save()
        
    #sharedMD.logThis("DragMove=> stitch around CI done")
    ## now insert the moved item into it's new position
    CI.parent = TIid;  ## was origTIparent
    CI.follows = TIid;
    CI.indentLevel = TI.indentLevel+1
    CI.save()
    sharedMD.logThis("DragMove=> CI saved")
    
    ## item that followed the target now must follow the CI, or the CI's last child (if any)

    sharedMD.logThis('dragmove=> targetFollowerID:'+str(targetFollower.id)+'  targetFollower.follows:'+str(targetFollower.follows) + '  lastkid:'+str(lastKidID))
    ## at this point tF.follows is previous one, 


    kidItems=[]
    
    if lastKidID == 0:
        targetFollower.follows=CI.id
        targetFollower.save()
    else:
        targetFollower.follows=lastKidID
        targetFollower.save()

        ## also correct indentLevel, since parent indent might have changed
        sharedMD.logThis(' dm=>kidList = '+str(kidList))


        
        for kidx in kidList:
            #kidx used to be kidpair[]
            thisKid=Item.objects.get(pk=kidx)
            thisKid.indentLevel=countIndent(thisKid)
            thisKid.save()
            
            #extend kidItems (formerly kidPair( -- add the info JS refreshItem function will need
            
            kidItems.append([thisKid.id, thisKid.follows, thisKid.title, thisKid.parent, thisKid.indentLevel, thisKid.priority, thisKid.status, thisKid.HTMLnoteBody, returnMarker(thisKid)], thisKid.statusText())
            #sharedMD.logThis(' => kidPair '+str(thisKid.id)+": "+str(kidPair))

    
    sharedMD.logThis(' => targetFollower.follows='+str(targetFollower.follows))
    
    parentKidUpdate = []

    parentKidUpdate.append([CI.id, CI.follows, CI.title, CI.parent, CI.indentLevel,CI.priority, CI.status, CI.HTMLnoteBody,returnMarker(CI),CI.statusText() ] )

    ## when drag-moving in CLOSE QUARTERS, and item like TI might go stale, b/c
    ## it was changed by, ex., b/c it was ALSO CI follower or some such. SO for
    ## now, let's get a fresh TI to write out.

    newTI=Item.objects.get(pk=TI.id)

    parentKidUpdate.append([newTI.id, newTI.follows, newTI.title, newTI.parent, newTI.indentLevel,newTI.priority, newTI.status,  newTI.HTMLnoteBody, returnMarker(newTI), newTI.statusText() ] )

    ## have to refresh the CI's parent, in case it's marker has changed w/ the move
    ## IF the parent != 0

    if origCIparent != 0:
        CIparent=Item.objects.get(pk=origCIparent)
        parentKidUpdate.append([CIparent.id, CIparent.follows, CIparent.title, CIparent.parent, CIparent.indentLevel, CIparent.priority, CIparent.status, CIparent.HTMLnoteBody, returnMarker(CIparent), CIparent.statusText()] )
   
    parentKidUpdate += kidItems

    return(parentKidUpdate)

#############################################################################
def returnMarker(Itemx):
    ## returns a plus or bullet, depending upon if Item has kids or not
    if len( Item.objects.filter(parent=Itemx.id) ) > 0:
        return("+")
    else:
        return("&bull;")

#############################################################################
def backupdata(request):
    # projlist=0 is default value, overridden by passed parameters

    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()


    #BackupTheseProjects = []
    if request.method == 'POST': # If the form has been posted...
        #form = ImportForm(request.POST) # A form bound to the POST data
        #if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        if "BackupTheseProjects" in request.POST:
            sharedMD.logThis("backup request:"+str(request.POST))

            for reqData in request.POST.lists():
                if reqData[0] == 'BackupTheseProjects':
                    BackupTheseProjects=reqData[1]
                

            #    =request.POST['BackupTheseProjects']

            
            sharedMD.logThis(' backup ==> projlist:'+ str(BackupTheseProjects))


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

                sharedMD.logThis("Project "+str(thisBackupID)+": "+str(count)+" items backed up to "+filename)
                OUTX.close()
            #return HttpResponseRedirect('/serialize/')
    else:
        #form = serializeForm() # An unbound form
        pass




    return render_to_response('pim1_tmpl/serialize.html', {
        'dirlist':dirlist.dirlist(BACKUPDIR),
        'backupdir':BACKUPDIR,
        'pagecrumb':'serialize/backup',
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )


#############################################################################
def healthcheck(request):
    current_projs = Project.objects.filter(projType=1).order_by('name')
    current_sets = ProjectSet.objects.all()

    healthTables = []
    projTable=checkHealth.projectList();
    healthTables.append(projTable);

    itemsNotInProjects=checkHealth.projectlessItems();
    healthTables.append(itemsNotInProjects);

    healthTables +=  checkHealth.followerCheck();

    

    return render_to_response('pim1_tmpl/healthcheck.html', {
        'titleCrumbBlurb':'health check',
        'displayTables':healthTables,
        'current_projs':current_projs,
        'current_sets':current_sets,

        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
        }, context_instance=RequestContext(request) )


