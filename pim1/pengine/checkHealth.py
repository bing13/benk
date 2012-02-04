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

def projectList():

    projList = Project.objects.all().order_by('name')

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
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell">%s </td>
        <td class="health_cell health_cell_total">%s </td>
        </tr>''' % (p.id, p.set, p.name, p.color, p.projType, p.archivePair, Item.objects.filter(project=p.id).count())

    tableBody += '''<tr class="health_row">
    <td class="health_cell" colspan="5"></td>
    <td class="health_cell">grand total</td>
    <td class="health_cell health_cell_total">%s </td>
    </tr>''' % ( Item.objects.all().count())

        
    
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

def followerCheck():
    zeroFollowers=Item.objects.filter(follows=0)

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

    # get a list of item IDs
    allIDs=Item.objects.all().order_by('id').values_list('id', flat=True)

    # get a list of all followers
    allFollows=Item.objects.all().order_by('follows').values_list('follows', flat=True)
    
    # values_list doesn't return a normal array, consequently
    # .count() is buggy, so we trasfer to a normal array
    
    allFollowsArray = []
    allFollowsArray += allFollows

    multiFollowersIDs = [];

    for i in allIDs:
        #sharedMD.logThis("trying, ID:" +  str(i) + " follows count:"+str( allFollowsArray.count(i)) )
        #for f in allFollows:
        if ( allFollowsArray.count(i) != 1):
            ix = Item.objects.get(pk=i)

            try:
                lastID = sharedMD.getLastItemID(ix.project.id);
            except:
                lastID = 999999;  ## for the bogus item that has no project
            
            if ( ix.id != lastID ):
                multiFollowersIDs.append(Item.objects.get(pk=i).follows);
                ##sharedMD.logThis("dup follower, ID:" + str(i))


    uniqueMFids=set(multiFollowersIDs)
    sharedMD.logThis("checkhealth uniqueMFids:" + str(uniqueMFids))
    multiFollowersObjs=Item.objects.filter(id__in = uniqueMFids).order_by('id')
    
    tableBody='<tr class="health_row"><th class="health_cell" colspan="7">%s items with multiple followers</th></tr>' % len(multiFollowersObjs)

    tableBody += '''<tr class="health_row">
        <th class="health_cell">id </th>
        <th class="health_cell">project </th>
        
        <th class="health_cell">parent </th>
        <th class="health_cell">follows</th>
        <th class="health_cell">title</th>
        <th class="health_cell">priority</th>
        <th class="health_cell">status</th>
        </tr>'''

    if (0 in uniqueMFids ):
        tableBody +='''<tr class="health_row">
        <td class="health_cell" colspan="7"> item 0 has multiple followers </td>
        </tr>''' 
    else:
    
        for p in multiFollowersObjs:
            try:
                projx = p.project.id;
            except:
                projx = "none";
            
            tableBody += '''<tr class="health_row">
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            <td class="health_cell">%s </td>
            </tr>''' % (p.id, projx, p.parent, p.follows, p.title, p.priority, p.status)


    multiFollowersOutput = tableBody


    ##########################################################################
    # selfFollowers / lostFollowers

    selfFollowersObjs=[]
    lostFollowersObjs=[]
    
    allItems = Item.objects.all().order_by('project')
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

    return([zeroFollowersOutput, multiFollowersOutput, selfFollowersOutput, lostFollowersOutput ])
