# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from pim1.pengine.models import Item, Project
# ++ was "pengine.models"
from django.template import Context, loader
import datetime, sys;
#D410 sys.path.append('C:\\Documents and Settings\\Owner\\My Documents\\Python\\library');
#D610 #sys.path.append('C:\\Documents and Settings\\Bernard Hecker\\My Documents\\python\\lib')
#DreamHost - UNIX
sys.path.append('/home/bhadmin13/bernardhecker.com/pim1/library');

#Battlestar
#sys.path.append('C:\\Users\\Bernard\\Documents\\python64\\library');

import gooOps;
from rfc3339 import rfc3339;

from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django import forms

LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'
#LOGOUT = open(LOGFILE, 'a')


## https://docs.djangoproject.com/en/1.3/intro/tutorial04/
class ImportForm(forms.Form):
    fileToImport=forms.CharField(max_length=300)
    projectToAdd=forms.IntegerField()

class ssearchForm(forms.Form):
    searchfx=forms.CharField(max_length=200)

@csrf_protect



##################################################################
def homepage(request):
    current_projs = Project.objects.all()
    c = Context({'home_page':'homepage',
                 'current_projs':current_projs,
                 'nowx':datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")})
    t = loader.get_template('pim1_tmpl/home_page.html')
    return HttpResponse(t.render(c))
##################################################################

def itemlist(request,proj_id):
    logThis("Entering itemlist <====================")
    
    ##current_items=Item.objects.all()
    current_projs = Project.objects.order_by('name')
    displayList = buildDisplayList(current_projs, proj_id,'follows',0,[])

    t = loader.get_template('pim1_tmpl/items/index.html')
                       
    c = Context({
        'pagecrumb':'main item list',
        'current_items':displayList,
        'current_projs':current_projs, 
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'item list'

    })
    return HttpResponse(t.render(c))
##################################################################
def allMyChildren(targetID, resultList):
    logThis("Entering allMyChildren <====================")

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
    current_projs = Project.objects.order_by('name')

    hoistProj=Item.objects.get(pk=hoistID).project_id 
    
    displayList=buildDisplayList(current_projs, hoistProj, 'follows', hoistID,[])

    t = loader.get_template('pim1_tmpl/items/index.html')
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'item list (hoist)'
    })
    return HttpResponse(t.render(c))

##################################################################
def logThis(s):
    LX = open(LOGFILE, 'a')
    t = datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
    LX.write(t+": "+s+'\n')
    LX.close
    return()


##################################################################
def buildDisplayList(projectx, projID, ordering, hoistID, useList):
    logThis("Entering buildDisplayList <====================")
    #hoistID = 55

    ### Select the items to operate on: all, or just those from 1 project

    if useList != []:
        items2List=Item.objects.filter(id__in=useList).order_by(ordering)

    elif hoistID != 0:
        ## insures that the target item appears in the final list.
        resultList=[] 
        resultList=allMyChildren(hoistID,resultList)
        resultList.append(hoistID)
 
        ## get querySet that only has items with those IDs in it
        items2List=Item.objects.filter(id__in=resultList).order_by( ordering)
        projlist=Project.objects.get(pk=projID)
 
    elif projID != '0': 
        ##specified project
        items2List=Item.objects.filter(project__id=projID).order_by( ordering)
        projlist=Project.objects.get(pk=projID)
                    
    else:
        ##all projects, requires project sort
        items2List=Item.objects.all().order_by( ordering)
        projlist=projectx

    ### Build the parent list
    ## pzero=[] ## list of top-level items // commented out 12/17/2011
    ixList=[]
    jxHash={}
    logThis("..queries done...")


    parentList=[] ## list of all items that are parents
    for px in items2List:
        if px.parent not in parentList: parentList.append(px.parent)

    ###SLOW BLOCK BEGINS########################################################################
        
    logThis("....parent list built...")
    ### get project string to where it can be displayed    
    for ix in items2List:
        ### count the number of ancestors to determine indent level
        ### THIS CALL IS VERY SLOW, accounting for 39sec out of 47sec total
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
        else:
            ix.outlineBullet="&bull;"
            

    logThis( ".....ix built.....")

    displayList=[]
    followHash={}
    
    if ordering=='follows':
        ## generate outline-ordered and formatted output list
        for f2 in ixList:
            if followHash.has_key(f2.follows): 
                logThis( "\n\n=====> WARNING!! followHash duplicate [" + str(f2) +" " + str(f2.follows)+']')

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
            
        #logThis('ixList='+str(ixList))    

        # Can be voluminous!
        #logThis('followHash'+str(followHash))

        if min(followHash.keys()) != 0:
            # commented 10/23/2011, added two lines below
            #followHash[0]=min(followHash.keys())
            #minfhk=min(followHash.keys())
            #followHash[0]=followHash.pop(minfhk)
            for fhk in followHash.keys():
                if fhk in followHash.values():
                    continue
                else:
                    break
            logThis("FHK is="+str(fhk))
            followHash[0]=followHash[fhk]
            followHash.pop(fhk)
            ###logThis('new followhash'+str(followHash))
            
        currentID = 0

        logThis("...built followhash....")

        ## OK, now follow the chain of who follows whom, starting with whoever follows Parent ID = 0
        while  followHash.has_key(currentID):
            #print "current ID=%s, followHash[currentID]=%s" % (currentID, followHash)
            #print jxHash
            # followHash[currentID]
            displayList.append(jxHash[followHash[currentID]])
            currentID=followHash[currentID]

        # theoretically, having no followHash key for currentID means you're on the last item
        # but beware re: data integrity / lost items
        logThis(".....displayList built...")
    else:

        displayList=ixList
    logThis("Exiting buildDisplayList ========>")
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

def getLastItemID(projID):
    listOfFollowers=[] ## a list of all IDs that appear in item.follows
    thisProjItems = Item.objects.filter(project__id=projID)
    ## 12/18/2011 limited search to one projID.
    for itemx in thisProjItems:
        listOfFollowers.append(itemx.follows)
    lastItemIDs = []
    for itemx in thisProjItems:
        if itemx.id not in listOfFollowers:
            lastItemIDs.append(itemx.id)
    if len(lastItemIDs)!= 1:
        logThis( "===== BAD LAST ITEM IDs, should only be one. Instead: "+ str(lastItemIDs))
        exit()
    else:
        logThis( "Last item ID:"+ str(lastItemIDs[0]))
        return(lastItemIDs[0])
##################################################################

def actionItem(request, pItem, action):
    logThis( "item "+ pItem + " to " + action);


    current_projs = Project.objects.order_by('name')
    clickedItem = Item.objects.get(pk=pItem)
    clickedProjNum=clickedItem.project.id
    lastItemID=getLastItemID(clickedProjNum)

    
    #assigning project [many to many]...convoluted?.... 
    projIDc=clickedItem.project.id
    projObjc=Project.objects.get(pk=projIDc)
    
    ## find the item that was following pItem
    if action=='add':
        try:
            oldFollower = Item.objects.get(follows=pItem)
            follower=True
        except:
            logThis( "Item has no follower: ID" + str(pItem))
            follower=False

        newItem = Item(title="[NEW ITEM]",priority='0', status='0', \
           follows=pItem, parent=clickedItem.parent)
        newItem.project=clickedItem.project

        newItem.save()
        
        if follower:
            oldFollower.follows = newItem.id
            oldFollower.save()
    ###DELETE###################################################################

    elif action=='delete':
        if int(pItem) != lastItemID:
            
            logThis( "===pItem, lastItemID============"+str(pItem)+ '  '+str(lastItemID)+"==============")
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
            logThis( "Can't demote further, item "+str(clickedItem.id))
        elif clickedItem.parent==Item.objects.get(pk=clickedItem.follows).parent:
            clickedItem.parent=clickedItem.follows
            clickedItem.save()
        elif countIndent(Item.objects.get(pk=clickedItem.follows))>countIndent(clickedItem):
            indx=Item.objects.get(pk=clickedItem.follows)
            while countIndent(indx)> countIndent(clickedItem):
                indx=Item.objects.get(pk=indx.follows)
            logThis( "countIndent="+str(countIndent(indx))+ '  ' +str(countIndent(clickedItem))+"<==")
            clickedItem.parent=indx.id
            clickedItem.save()
        else: 
            logThis( "===WARNING!========= DEMOTE CONDITION MISSED. pItem:"+str(pItem))

    ###PROMOTE##################################################################
    elif action=='promote': 
        if clickedItem.parent ==  0:
            logThis( "CAN'T PROMOTE TOP-LEVEL "+ str(pItem))
        elif countIndent(clickedItem) > countIndent(Item.objects.get(pk=clickedItem.follows)):
            logThis( "EXECUTING PROMOT 1 F "+str(clickedItem.id))
            clickedItem.parent=Item.objects.get(pk=clickedItem.follows).parent
            clickedItem.save()

        elif countIndent(clickedItem) <= countIndent(Item.objects.get(pk=clickedItem.follows)):
            logThis( "Executing promote 2 of id="+ str(pItem))
            indx=Item.objects.get(pk=clickedItem.follows)
            while countIndent(indx)>= countIndent(clickedItem):
                logThis( str(countIndent(indx))+"   "+str(countIndent(clickedItem))+"<==")
                indx=Item.objects.get(pk=indx.follows)
            logThis( str(countIndent(indx))+"  "+str(countIndent(clickedItem))+"<==++")
            clickedItem.parent=indx.parent
            clickedItem.save()
                                                        
        else:
            logThis( "====WARNING!=== COULDN'T PROMOTE, REASON UNKNOWN:" + str(pItem))

    ###MOVE UP##################################################################
    elif action=='moveup':

        if clickedItem.follows==0:
            logThis( "CAN'T MOVE UP TOP item "+ str(pItem))
        else:
            hasFollower=False             
            lastKid=findLastKid(clickedItem,lastItemID)

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
        lastKidofCI=findLastKid(clickedItem,lastItemID)
        if clickedItem.id == lastItemID or lastKidofCI == lastItemID:
            logThis( "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
        else:
            #ciFollower=Item.objects.get(follows=clickedItem.id)
            if lastKidofCI !=0:
                fciFollower=Item.objects.get(follows=lastKidofCI)
            else:
                fciFollower=Item.objects.get(follows=clickedItem.id)
            lastKidOfFollower=findLastKid(fciFollower, lastItemID)
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


    ###UNKNOWN ACTION###########################################################

    else:
        logThis( "===WARNING!=========== \nUnknown action=" + action)
        exit()

    ## let's restrict default view to the clicked item project
    logThis( "cp="+str(current_projs)+" cpn="+str(clickedProjNum))
    displayList = buildDisplayList(current_projs,clickedProjNum, 'follows',0,[])
    logThis( "+++DISPLAY LIST BUILT+++")
    t = loader.get_template('pim1_tmpl/items/index.html')

    c = Context({
        'current_items':displayList,
        'current_projs':current_projs, 
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb': "Action Item List"
    })
    return HttpResponse(t.render(c))

##################################################################

def findLastKid(itemx, lastItemID):
    ###   look for first item below you with =< level of indent
    if itemx.id == lastItemID:
        lastKid=0
    else:
        indx=Item.objects.get(follows=itemx.id)
        if itemx.parent==indx.parent  or countIndent(indx) < countIndent(itemx):
            ## if we both have same parent, or follow is low indent level 
            lastKid=0  ## special value for "no kids"
        else:
            prev_id=indx.id  ## need to define, in case we don't enter while block
            while (countIndent(indx) > countIndent(itemx)) and (indx.id != lastItemID):
                logThis("findLastKid =>"+ str(countIndent(indx))+"  "+str(countIndent(itemx))+"<=md=")
                prev_id=indx.id
                indx=Item.objects.get(follows=indx.id)

            lastKid=prev_id
            logThis( "indx.follows/ itemx.follows/ indx.id/  prev_id= " + str(indx.follows) +' '+ str(itemx.follows) +' '+ str(indx.id) +' '+ str(prev_id))
    logThis("findLastKid method: lastKid="+str(lastKid))
    return(lastKid)

##################################################################

def psd(request,pSort):
    current_projs = Project.objects.order_by('name')
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
        'pSort':pSort,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
    })
    return HttpResponse(t.render(c))

###################################################################

def gridview(request):
    current_projs = Project.objects.order_by('name')
    displayList =  buildDisplayList(current_projs,'0', 'follows',0,[])

    t = loader.get_template('pim1_tmpl/items/gridview.html')
    c = Context({
        'pagecrumb':'grid view',
        'current_items':displayList,
        'current_projs':current_projs,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
    })
    return HttpResponse(t.render(c))

##################################################################

def detailItem(request,pItem):
    current_projs = Project.objects.order_by('name')

    ix=Item.objects.get(pk=pItem)
    #get project to where it can be displayed; was project_s
    ###ix.project=ix.project 

    displayList=[ix]

    t = loader.get_template('pim1_tmpl/items/itemDetail.html')
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs, 
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'item detail'
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

    logThis( "gooTaskIdList="+str(gooTaskIdList))

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
    
    current_projs = Project.objects.order_by('name')
    displayList =  buildDisplayList(current_projs,'0','-date_gootask_display',0,[])
    
    t = loader.get_template('pim1_tmpl/items/psd.html')
    c = Context({
        'pSort':'-date_gootask_display',
        'current_items':displayList,
        'current_projs':current_projs, 
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
    logThis("Entering ssearch <====================")

    current_projs = Project.objects.order_by('name')
    c = {}
    c.update(csrf(request))
    error_message=''
     
    if request.method == 'GET':
        sform = ssearchForm(request.GET)
        if sform.is_valid():
            searchTerm=sform.cleaned_data['searchfx']
            logThis("Search term="+searchTerm)

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
                displayList=buildDisplayList(current_projs, 0, 'id', 0, totalHits)
                #buildDisplayList(projectx, projID, ordering, hoistID, useList):
            else:
                ## no hits
                displayList=[]

        else:
            error_message="Form was not valid, search term = "
            displayList=['Form not valid, no results to display']

    t = loader.get_template('pim1_tmpl/items/index.html')
    c = Context({
        'current_items':displayList,
        'current_projs':current_projs,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S"),
        'pagecrumb':'search result',
        'error_message':error_message,
        'is_search_result':'true'
    })
    return HttpResponse(t.render(c))
            
                                         
#############################################################################

def importfile(request):
    current_projs = Project.objects.order_by('name')
    c = {}
    c.update(csrf(request))	  
 
    if request.method == 'POST': # If the form has been posted...
        form = ImportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            fileToImport=form.cleaned_data['fileToImport']
            projectToAdd=form.cleaned_data['projectToAdd']
            logThis( "fileToImport="+fileToImport)
            logThis( "projectToAdd="+str(projectToAdd))

            logThis( "+++ departing to importISdata")
            importISdata(fileToImport,projectToAdd)

            # Redirect after POST
            return HttpResponseRedirect('/projdetail/'+str(projectToAdd)) 
    else:
        form = ImportForm() # An unbound form

    return render_to_response('pim1_tmpl/importIS.html', {
                'form':form,
                'pagecrumb':'import',
                'current_projs':current_projs,
                'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
                }, context_instance=RequestContext(request) )
  
#############################################################################

def importISdata(importFile,newProjectID):
#    import dircache
#    print "default level=",dircache.listdir('.')

    startdir='/home/bhadmin13/dx.bernardhecker.com/pim1/pengine/imports/'
    textAccumulator = ''
    logThis( "+++ b1 importISdata")
    INFILE=open(startdir+importFile,'r')
    allLines=INFILE.readlines()
    currentISid = 0
    previousNewItemBenkID=getLastItemID(newProjectID)
    firstRecord = 'yes'
    logThis( "+++ b2 importISdata")
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
                    newItem = Item(title=selectorTitle, priority='0', status='0', \
                              follows=previousNewItemBenkID, \
                              IS_import_ID = currentISid,     \
                              HTMLnoteBody = textAccumulator)

                    if ISparentFirst == 0:
                        newItem.parent = 0
                    else:
                        newItem.parent=Item.objects.get(IS_import_ID=ISparentFirst).id
                    newItem.project=Project.objects.get(pk=newProjectID)

                    ##added 12/22/2011
                    newItem.indentLevel=countIndent(newItem)

                    newItem.save()
                    ### PURGE PREVIOUS VALUES ###

                    textAccumulator = ''                   
                    previousNewItemBenkID = newItem.id
                    ISparentFirst = ''
                    selectorTitle = ''

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
                        ISparentFirst = splitter[0]
                    else:
                        ISparentFirst=0
                else:
                    ISparentFirst=0

            elif itemType=='SELECTOR':
                selectorTitle=data;

            elif itemType == 'NOTE':
                # nothing to do here. We're accumulating all row bodies that do not start
                # with the marker, and then dumping them when we hit a NEW_RECORD
                pass;

            else:
                logThis( "* * * * RECORD MISSED * * * *:"+ str(lx))
