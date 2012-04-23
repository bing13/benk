## POSSIBLE PROBLEM: I changed kidList as returned by getLastKid to not have
# CI and ci.follows in it's own array, which is then embedded in kidList.
# now it's just linear. Might mess up some other routines.

###
# modules that are shared between views.py and drag_actions.py
#
#################################
from pim1.pengine.models import Item, Project, ProjectSet
import datetime, os

LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'
LOCKFILEDIR = '/home/bhadmin13/dx.bernardhecker.com/pim1/locks/'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# validate_maint_membership

def validate_maint_membership(user):
    ### I have no idea where "user" is defined
    ### nor why I don't seem to be able to pass normal parameters to this function
    ### (although it is referenced from a decorator )
    
    groupx = 'maint user';
    if user.is_authenticated() and ( (user.groups.filter(name=groupx).count() > 0 or user.is_superuser)):
        isMaintUser = True
    else:
        isMaintUser = False
        user.message_set.create (message="You do not have permission to access that page.")
        
    return isMaintUser
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# validate_project

def validate_project(proj_id):
    allItems = Item.objects.filter(project=proj_id)
    ## find items that have duplicate followers
    allFollows=Item.objects.filter(project=proj_id).order_by('follows').values_list('follows', flat=True)
    # values_list doesn't return a normal array, consequently
    # .count() is buggy, so we trasfer to a normal array
    allFollowsArray = []
    allFollowsArray += allFollows
    followedByMultiples = []

    for x in allFollowsArray:
        allFollowsArray.remove(x); ## remove the first occurence of value x

        if x in allFollowsArray:
            followedByMultiples.append(x)

    if len(followedByMultiples) > 0:
        logThis('---', " * * * * * * * * VALIDATE ERROR * * * * * * * ");
        totalErrorMsg = ''

        for f in followedByMultiples:
            multiFollows= Item.objects.filter(follows=f)
            mfString='';
            for k in multiFollows:
                mfString += str(k.id) + ":" + k.title[:50] + ',';
            logThis('---', "[%s is followed by %s]" % (f, mfString[:-1]));
            totalErrorMsg += "[%s is followed by %s]" % (f, mfString[:-1]) + '\n';
        return(totalErrorMsg);
    else:
        return("No errors");
    


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
def logThis(userx, s):
    LX = open(LOGFILE, 'a')
    t = datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
    LX.write(t+"\t"+userx+"\t"+s+'\n')
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
        logThis('---',  "===== getLastItemID: BAD LAST ITEM IDs, should only be one. Instead: "+ str(lastItemIDs))
        logThis('---',  "===== BAILING getlastItemID=====" )

        validate_project(projID);

        exit()


    else:
        logThis('---',  "Last item ID:"+ str(lastItemIDs[0]))
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

    logThis('---', "sMDflk=> findLastKid lastKid="+str(lastKid))
    return(lastKid,kidList)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# createLock
def createLock(userx, message):
    LX = open(LOCKFILEDIR+userx+'.lock', 'a')
    lockMessage = "Locked:\t" + userx +'\t' + datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")+ " ::\t" + message
    LX.write(lockMessage)
    LX.close
    return("lock created")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# releaseLock
def releaseLock(userx):
    if os.path.exists(LOCKFILEDIR+userx+'.lock'):
        os.remove(LOCKFILEDIR+userx+'.lock')
        msg = "lock removed"
    else:
        msg = "no lock file, no action taken"

    logThis('---', msg)
    return(msg)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# testLock
def testLock(userx):
    if os.access(LOCKFILEDIR+userx+'.lock', os.F_OK):
        # hope this isn't a problem if the write op is still open
        LX = open(LOCKFILEDIR+userx+'.lock', 'r')
        msg=LX.readlines()
        LX.close
        return(msg)
    else:
        return("no lock")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# tailLog

def tailLog(nLines):
    LX = open(LOGFILE, 'r')
    #t = datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
    allLines=LX.readlines()
    lastLogLines=allLines[-nLines:]
    LX.close
    
    return(lastLogLines)
