#
# POSSIBLE PROBLEM: I changed kidList as returned by getLastKid to not have
# CI and ci.follows in it's own array, which is then embedded in kidList.
# now it's just linear. Might mess up some other routines.
#


###
# modules that are shared between views.py and drag_actions.py
#
#################################
from pim1.pengine.models import Item, Project
import datetime

LOGFILE = '/home/bhadmin13/dx.bernardhecker.com/pim1/benklog1.log'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# logThis
def logThis(s):
    LX = open(LOGFILE, 'a')
    t = datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
    LX.write(t+":: "+s+'\n')
    LX.close
    return()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  findLastKid
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
                kidList += [indx.id, indx.follows]
                prev_id=indx.id
                if indx.id == lastItemID:
                    lastItemFlag='yes'
                else:
                    indx=Item.objects.get(follows=indx.id)

            lastKid=prev_id

    logThis("=> findLastKid lastKid="+str(lastKid))
    return(lastKid,kidList)

