## drag_actions.py
#
# actions that work with xhr requests
#


from pim1.pengine.models import Item, Project
import sharedMD



class dragOps():
    '''actions on benk display rows, suitable for xhr requests'''

    def __init__(self):
        temp = None



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# updateIDsDecorate

    def updateIDsDecorate(self, IDlist):
        decoratedItems=[]
        for id in IDlist:
            if id != 0 :
                thisItem=Item.objects.get(pk=id)
                decoratedItems.append([thisItem.id, thisItem.follows, thisItem.title, thisItem.parent, thisItem.indentLevel, thisItem.priority, thisItem.status, thisItem.HTMLnoteBody, sharedMD.returnMarker(self, thisItem), thisItem.statusText()])

                ## am concerned that other places where this list is build won't have statusText()
                
        return(decoratedItems)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveUp

    def moveUp(self,clickedItem, lastItemID):

        lastKid, kidList = sharedMD.findLastKid(clickedItem, lastItemID)

        
        if clickedItem.follows==0:
            sharedMD.logThis( "CAN'T MOVE UP TOP item "+ str(pItem))
            return([])
        else:
            hasFollower=False             

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

            updateListIDs=[clickedItem.id, tts_follows,bts_follows ] + kidList
            sharedMD.logThis("updateListIDs: "+str(updateListIDs))
            sharedMD.logThis("updateListIDs deco: "+str(self.updateIDsDecorate(updateListIDs)))
            return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveDown

    def moveDown(self,clickedItem,  lastItemID):
        
        ### may wish to remodel so it looks like "moveup", which uses the findLastKid method

        lastKidofCI, kidList = sharedMD.findLastKid(clickedItem, lastItemID)
        
        if clickedItem.id == lastItemID or lastKidofCI == lastItemID:
            sharedMD.logThis( "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
        else:
            #ciFollower=Item.objects.get(follows=clickedItem.id)
            if lastKidofCI !=0:
                fciFollower=Item.objects.get(follows=lastKidofCI)
            else:
                fciFollower=Item.objects.get(follows=clickedItem.id)
                
            lastKidOfFollower,kidList = sharedMD.findLastKid(fciFollower, lastItemID)
            
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

            updateListIDs=[clickedItem.id, clickedItem.follows, bottomToSwap.id, bottomFollower.id ] + kidList
            return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# promote

    def promote(self,clickedItem,  lastItemID):

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
                # not sure this works right at the moment
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

        ## now for refresh

        updateListIDs=[clickedItem.id, clickedItem.follows ] + kidList
        return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# demote
    def demote(self,  clickedItem,  lastItemID):

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

        updateListIDs=[clickedItem.id, clickedItem.follows ] + kidList
        return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# newItem

    def addItem(self,  clickedItem,  lastItemID):

        ## find the item that was following clickedItem
        try:
            oldFollower = Item.objects.get(follows=clickedItem.id)
            follower=True
        except:
            sharedMD.logThis( "Item has no follower: ID" + str(clickedItem.id))
            follower=False

        newItem = Item(title="",priority='0', status='0', \
           follows=clickedItem.id, parent=clickedItem.parent, indentLevel=clickedItem.indentLevel)
        newItem.project=clickedItem.project

        newItem.save()

        if follower:
            oldFollower.follows = newItem.id
            oldFollower.save()

        return(newItem)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# delete ##
    
    def delete(self, clickedItem, lastItemID):

        ghostsID = clickedItem.id
        ghostFollowsID = clickedItem.follows
        ghostsParentID = clickedItem.parent
        
        if clickedItem.id != lastItemID:
             
            followingMe = Item.objects.get(follows=clickedItem.id)
            
            followingMe.follows=clickedItem.follows
            if followingMe.parent==clickedItem.id:
                followingMe.parent=clickedItem.parent
            followingMe.save()

        # remove entry from Projects
        # clickedItem.project is a project object, another dot to get id
        projObjc=Project.objects.get(pk=clickedItem.project.id)
        projObjc.item_set.remove(clickedItem)

        # pull this before the item is deleted
        toUpdate = self.updateIDsDecorate([ghostsParentID, ghostFollowsID, followingMe.id] ) 
        sharedMD.logThis( "==> deleting "+str(clickedItem.id))
        # remove item
        clickedItem.delete()
        
        return(toUpdate)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# swapWithArchivePair ##
    
    def swapWithArchivePair(self, clickedItem, lastItemID):

        # routine may work for unarchiving an item as well... perhaps messily...



        ghostsID = clickedItem.id
        ghostFollowsID = clickedItem.follows
        ghostsParentID = clickedItem.parent

        updateThese = [ghostsParentID, ghostFollowsID]
        
        if clickedItem.id != lastItemID:
            
            followingMe = Item.objects.get(follows=clickedItem.id)
            updateThese.append(followingMe.id)
            
            followingMe.follows=clickedItem.follows
            if followingMe.parent==clickedItem.id:
                followingMe.parent=clickedItem.parent
            followingMe.save()

        # remove entry from Projects, MOVE to archive project
        # clickedItem.project is a project object, another dot to get id
        projObjc=Project.objects.get(pk=clickedItem.project.id)
        projObjc.item_set.remove(clickedItem)


        clickedItem.project = projObjc.archivePair
        clickedItem.follows = sharedMD.getLastItemID(clickedItem.project.id)
        clickedItem.parent = 0
        clickedItem.indentLevel = 0

        clickedItem.save()

        # pull this before the item is deleted
        toUpdate = self.updateIDsDecorate(updateThese ) 
        sharedMD.logThis( "==> archivePair moved item "+str(clickedItem.id)+"  to proj: " +str(clickedItem.project.id)    )
        # remove item
        # clickedItem.delete()
        
        return(toUpdate)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# priorityChange

    def priorityChange(self,  CI,  direction):

        choices=CI.PRIORITY_CHOICES; ## (('1', "urgent"),("2", "Important),(...
        
        if direction == 'up': increment = -1;
        else:
            increment = +1;


        currentChoice=len(choices)-1; ## i.e., the lowest priority
        for i in range(0,len(choices)):
            if choices[i][0] == CI.priority: 
                currentChoice=i

        newChoice=currentChoice + increment; 
        
        if newChoice == -1 : newChoice = 0
        if newChoice == len(choices): newChoice -= 1;



        CI.priority = choices[newChoice][0]

        CI.save()

 
        return(self.updateIDsDecorate([CI.id]))
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# statusChange

    def statusChange(self,  CI,  direction):

        choices=CI.STATUS_CHOICES; ## (('1', "urgent"),("2", "Important),(...
        
        if direction == 'up': increment = -1;
        else:
            increment = +1;


        currentChoice=len(choices)-1; ## i.e., default to the lowest priority
        for i in range(0,len(choices)):
            if choices[i][0] == CI.status: 
                currentChoice=i

        newChoice=currentChoice + increment; 
        
        if newChoice == -1 : newChoice = 0
        if newChoice == len(choices): newChoice -= 1;



        CI.status = choices[newChoice][0]

        CI.save()

 
        return(self.updateIDsDecorate([CI.id]))
