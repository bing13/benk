###
# healthcheck.py
#    modules that return various bits of diagnostic output
#
#################################
from pim1.pengine.models import Item, Project
import datetime, sys

sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/library');

import sharedMD; 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# projectList

def projectList(proj_id):
    if proj_id == 0:
        projList = Project.objects.all().order_by('name')
        totalCount = Item.objects.all().count()
    else:
        projList = Project.objects.filter(pk=proj_id)
        totalCount=Item.objects.filter(pk=proj_id).count()

    tableBody='<tr class="health_row"><th class="health_cell" colspan=7>project list</th></tr>'

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">set </th>
        <th class="health_cell">name</th>
        <th class="health_cell">color </th>
        <th class="health_cell">projType </th>
        <th class="health_cell">archivePair </th>
        <th class="health_cell"># of items </th>
        </tr>'''

    for p in projList:
        tableBody += '''<tr class="health_row">
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell" style="background:%s;">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell health_cell_total">%s </td>
        </tr>''' % (p.id, p.set, p.name, p.color, p.color, p.projType, p.archivePair, Item.objects.filter(project=p.id).count())

    tableBody += '''<tr class="health_row">
    <td class="health_cell" colspan="5"></td>
    <td class="health_cell">grand total</td>
    <td class="health_cell health_cell_total">%s </td>
    </tr>''' % ( totalCount )

        
    
    return(tableBody)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# projectlessItems

def projectlessItems():

    unprojectedItems = Item.objects.filter(project__isnull=True)

    tableBody='<tr class="health_row"><th class="health_cell" colspan=6>items without projects</th></tr>'

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        </tr>'''

    
    for p in unprojectedItems:
        tableBody += '''<tr class="health_row">
        <td class="health_cell"><a href="/pim1/admin/pengine/item/%s">%s</a> </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        </tr>''' % (p.id, p.id, p.parent, p.follows, p.title, p.priority, p.status)
    
    return(tableBody)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# followerCheck 

def followerCheck(proj_id):

    if proj_id == 0:
        zeroFollowers=Item.objects.filter(follows=0)

    else:
        zeroFollowers=Item.objects.filter(follows=0, project=proj_id)


    tableBody='<tr class="health_row"><th class="health_cell" colspan=6>items that follow item Zero</th></tr>'

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        </tr>'''

    
    for p in zeroFollowers:
        tableBody += '''<tr class="health_row">
        <td class="health_cell"><a href="/pim1/item/edititem/%s">%s</a> </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        </tr>''' % (p.id, p.id, p.parent, p.follows, p.title, p.priority, p.status)

    zeroFollowersOutput = tableBody

    ##########################################################################
    # multiFollowers


    if proj_id == 0:
        # get a list of item IDs
        allIDs=Item.objects.all().order_by('id').values_list('id', flat=True)
        # get a list of all followers (includes dupes)
        allFollows=Item.objects.all().order_by('follows').values_list('follows', flat=True)
    else:
        allIDs=Item.objects.filter(project=proj_id).order_by('id').values_list('id', flat=True)
        allFollows=Item.objects.filter(project=proj_id).order_by('follows').values_list('follows', flat=True)

        
    # values_list doesn't return a normal array, consequently
    # .count() is buggy, so we trasfer to a normal array
    
    allFollowsArray = []
    allFollowsArray += allFollows

    multiFollowersIDs = [];

    for i in allIDs:
        if ( allFollowsArray.count(i) != 1):
            ix = Item.objects.get(pk=i)

            try:
                lastID = sharedMD.getLastItemID(ix.project.id);
            except:
                lastID = 999999;  ## for the bogus item that has no project
            
            if ( ix.id != lastID ):
                
                #sharedMD.logThis("     multi: ix.id:"+str(ix.id)+"  afA.c:"+str(allFollowsArray.count(i))+"  xx:"+str(Item.objects.get(pk=i).follows))

                multiFollowersIDs.append(i)



    uniqueMFids=set(multiFollowersIDs)
    sharedMD.logThis("checkhealth uniqueMFids:" + str(uniqueMFids))
    multiFollowersObjs=Item.objects.filter(id__in = uniqueMFids).order_by('id')
    
    tableBody='<tr class="health_row"><th class="health_cell" colspan="8">%s items with multiple followers or no followers</th></tr>' % len(multiFollowersObjs)

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">project </th>
        
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        <th class="health_cell">following items</th>
        </tr>'''

    if (0 in uniqueMFids ):
        tableBody +='''<tr class="health_row">
        <td class="health_cell" colspan="8"> item 0 has multiple followers </td>
        </tr>''' 
    else:

        for p in multiFollowersObjs:
            pFollowers = ''
            try:
                projx = p.project.id;
            except:
                projx = "none";

            followerObjs = Item.objects.filter(follows=p.id)
            if followerObjs.count() == 0:
                pFollowers = "---"
            else:
                for f in followerObjs:
                    pFollowers += str(f.id)+','

        
            tableBody += '''<tr class="health_row">
            <td class="health_cell"><a href="/pim1/admin/pengine/item/%s">%s</a> </td>
 
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            </tr>''' % (p.id, p.id, projx, p.parent, p.follows, p.title, p.priority, p.status, pFollowers[:-1])


    multiFollowersOutput = tableBody




    ##########################################################################
    # parent Not in Tree
    crazyParentTry = 'newModel'
    if crazyParentTry == 'oldModel':
        # create dictionary where index is an item ID, and value is array of
        # *all* items in it's "follow tree", back to an item ID=0

        parentTree = {}
        #[5577, 5572, 5571] :
        sharedMD.logThis("Crazy parent build1 ...")


        for anID in allIDs:    
            sharedMD.logThis(" Crazy Parent tree building for ID = " + str(anID))
            followx = -999
            thisID=anID
            while followx != 0:
                followx = Item.objects.get(pk=thisID).follows
                if not parentTree.has_key(anID):
                    parentTree[anID]=[]
                parentTree[anID].append(followx)
                thisID=followx


        crazyParentObjects = []
        for ik in allIDs:
            #[5577, 5572, 5571] :

            ikObj = Item.objects.get(pk=ik)
            if ikObj.parent not in parentTree[ik]:
                crazyParentObjects.append(ikObj)

        tableBody='<tr class="health_row"><th class="health_cell" colspan="8">%s items with parents not in their follow tree</th></tr>' % len(crazyParentObjects)

        tableBody += '''<tr class="health_row">
            <th class="health_cell">id </th>
            <th class="health_cell">project </th>

            <th class="health_cell">parent </th>
            <th class="health_cell">follows</th>
            <th class="health_cell">title</th>
            <th class="health_cell">priority</th>
            <th class="health_cell">status</th>
            <th class="health_cell">following items</th>
            </tr>'''

        tableBody +='''<tr class="health_row">
            <td class="health_cell" colspan="8">  </td>
            </tr>''' 

        for p in crazyParentObjects:

            #try:
            #    projx = p.project.id;
            #except:
            #    projx = "none";

            tableBody += '''<tr class="health_row">
                <td class="health_cell"><a href="/pim1/admin/pengine/item/%s">%s</a> </td>

                <td class="health_cell">%s </td>
                <td class="health_cell">%s </td>
                <td class="health_cell">%s </td>
                <td class="health_cell">%s </td>
                <td class="health_cell">%s </td>
                <td class="health_cell">%s </td>

                </tr>''' % (p.id, p.id, p.project.id, p.parent, p.follows, p.title, p.priority, p.status)

            
        crazyParents = tableBody

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    elif crazyParentTry == 'newModel':
        ## build a complete tree of the data

        projList = Project.objects.all().order_by('name')


        tableBody='<tr class="health_row"><th class="health_cell" colspan="8">items with parents not in their follow tree, or in a different project</th></tr>' 

        tableBody += '''<tr class="health_row">
            <th class="health_cell">id </th>
            <th class="health_cell">seq / parent seq </th>
            <th class="health_cell">project /<br/> parent&nbsp;project </th>

            <th class="health_cell">parent </th>
            <th class="health_cell">follows</th>
            <th class="health_cell">title</th>
            <th class="health_cell">priority</th>
            <th class="health_cell">status</th>
  
            </tr>'''

        
        for projx in projList:
            if projx.id != 3:
                #items2List=Item.objects.filter(project__id=projx.id).order_by( 'follows' )
                thisItem = Item.objects.filter(project__id=projx.id).get(follows=0)
                followOrder = [thisItem]
                contx = True
                while contx:
                    try:
                        nextItem = Item.objects.get(follows = thisItem.id)
                        followOrder.append(nextItem)
                        thisItem = nextItem
                    except:
                        contx=False


                ## project-item lookup
                PIL = {}
                seq = 0
                for item in followOrder:
                    PIL[item.id]={ 'seq':seq, 'parent':item.parent, 'follows':item.follows, 'project':item.project }
                    seq += 1;
                sharedMD.logThis("   ... PIL built, proj:"+str(projx.id))


                for ix in followOrder:
                    #sharedMD.logThis("   ...ix.id="+str(ix.id)+"  =>"+str(PIL[ix.id]))
                    if (ix.parent != 0) and ((PIL[ix.id]['seq'] < PIL[ix.parent]['seq']) or PIL[ix.id]['project'] != PIL[ix.parent]['project']):

                        tableBody += '''<tr class="health_row">
                            <td class="health_cell"><a href="/pim1/admin/pengine/item/%s">%s</a> </td>
                            <td class="health_cell">%s / %s</td>
                            <td class="health_cell">%s / <br/> %s</td>
                            <td class="health_cell">%s </td>
                            <td class="health_cell">%s </td>
                            <td class="health_cell">%s </td>
                            <td class="health_cell">%s </td>
                            <td class="health_cell">%s </td>
                            </tr>''' % (ix.id, ix.id, PIL[ix.id]['seq'], PIL[ix.parent]['seq'], ix.project.name,  PIL[ix.parent]['project'],  ix.parent, ix.follows, ix.title, ix.priority, ix.status )


        crazyParents = tableBody

    else:
        
        crazyParents='''<tr class="health_row"><th class="health_cell">crazy parents </th></tr><tr class="health_row"><td colspan=7>crazy parents under performance review</td></tr>'''




    ##########################################################################
    # selfFollowers / lostFollowers

    selfFollowersObjs=[]
    lostFollowersObjs=[]

    if proj_id == 0:
        allItems = Item.objects.all().order_by('project')
    else:
        allItems = Item.objects.filter(project=proj_id)

    

    
    for x in allItems:
        if (x.id == x.follows):
            selfFollowersObjs.append(x)
    
        if (x.follows not in allIDs and x.follows != 0):
            lostFollowersObjs.append(x)
            
    #####################################
    # self followers draw

    tableBody='<tr class="health_row"><th class="health_cell" colspan="7">%s items that follow themselves</th></tr>' % len(selfFollowersObjs)

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">project </th>
        
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        </tr>'''


    for p in selfFollowersObjs:
        try:
            projx = p.project.id;
        except:
            projx = "none";

        tableBody += '''<tr class="health_row">
        <td class="health_cell"><a href="/pim1/item/edititem/%s">%s</a> </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        </tr>''' % (p.id, p.id, projx, p.parent, p.follows, p.title, p.priority, p.status)


    selfFollowersOutput = tableBody

    ##############################
    # lostFollowers draw


    tableBody='<tr class="health_row"><th class="health_cell" colspan="7">%s items that follow missing item</th></tr>' % len(lostFollowersObjs)

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">project </th>
        
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        </tr>'''


    for p in lostFollowersObjs:
        try:
            projx = p.project.id;
        except:
            projx = "none";

        tableBody += '''<tr class="health_row">
        <td class="health_cell"><a href="/pim1/item/edititem/%s">%s</a> </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        </tr>''' % (p.id, p.id, projx, p.parent, p.follows, p.title, p.priority, p.status)


    lostFollowersOutput = tableBody






    #############################################################################

    return([zeroFollowersOutput, multiFollowersOutput, selfFollowersOutput, lostFollowersOutput, crazyParents ])
