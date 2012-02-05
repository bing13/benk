## POSSIBLE PROBLEM: I changed kidList as returned by getLastKid to not have
# CI and ci.follows in it's own array, which is then embedded in kidList.
# now it's just linear. Might mess up some other routines.

###
# modules that are shared between views.py and drag_actions.py
#
#################################
from pim1.pengine.models import Item, Project
import datetime

LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# countIndent

def countIndent(anItem):
    
    indentCount=0
    
    while anItem.parent != 0: 
        indentCount+=1
        #if anItem.parent !=0:
        anItem=Item.objects.get(pk=anItem.parent)
            
    return(indentCount)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# returnMarker

def returnMarker(self,itemx):
        ## returns a plus or bullet, depending upon if Item has kids or not
        if len( Item.objects.filter(parent=itemx.id) ) > 0:
            return("+")
        else:
            return("&bull;")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# logThis
def logThis(s):
    LX = open(LOGFILE, 'a')
    t = datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
    LX.write(t+":: "+s+'\n')
    LX.close
    return()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# getLastItemID


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
        logThis( "===== getLastItemID: BAD LAST ITEM IDs, should only be one. Instead: "+ str(lastItemIDs))
        logThis( "===== BAILING getlastItemID=====" )
        exit()
    else:
        logThis( "Last item ID:"+ str(lastItemIDs[0]))
        return(lastItemIDs[0])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  findLastKid  (includes grandkids)

def findLastKid(itemx, lastItemID):
    ###   look for first item below you with =< level of indent
    kidList=[]
    if itemx.id == lastItemID:
        lastKid=0
    else:
        indx=Item.objects.get(follows=itemx.id)
        if itemx.parent==indx.parent  or indx.indentLevel < itemx.indentLevel:
            ## if we both have same parent, or follow is low indent level 
            lastKid=0  ## special value for "no kids"
        else:
            prev_id=indx.id  ## need to define, in case we don't enter while block
            lastItemFlag='no'
            while (indx.indentLevel > itemx.indentLevel) and lastItemFlag == 'no':
                # 'til 2/4 was: kidList += [indx.id, indx.follows]
                kidList += [indx.id]
                prev_id=indx.id
                if indx.id == lastItemID:
                    lastItemFlag='yes'
                else:
                    indx=Item.objects.get(follows=indx.id)

            lastKid=prev_id

    logThis("sMDflk=> findLastKid lastKid="+str(lastKid))
    return(lastKid,kidList)

