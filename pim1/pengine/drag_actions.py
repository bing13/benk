## drag_actions.py ###################################################
#
# actions that work with xhr requests
#

from django.contrib.auth.decorators import login_required

from pim1.pengine.models import Item, Project, ProjectSet
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
                #sharedMD.logThis('---',  "  deco for: "+ str(id))
                thisItem=Item.objects.get(pk=id)
                decoratedItems.append([thisItem.id, thisItem.follows, thisItem.title, thisItem.parent, thisItem.indentLevel, thisItem.priority, thisItem.status, thisItem.HTMLnoteBody, sharedMD.returnMarker(thisItem), thisItem.statusText()])

                ## am concerned that other places where this list is build won't have statusText()
                
        return(decoratedItems)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveUpEveryItem

    def moveUpEveryItem(self,clickedItem, lastItemID):

        lastKid, kidList = sharedMD.findLastKid(clickedItem, lastItemID)
        originalCIindentLevel = clickedItem.indentLevel
        
        if clickedItem.follows==0:
            sharedMD.logThis('---',  "CAN'T MOVE UP TOP item "+ str(pItem))
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

            clickedItem.indentLevel = sharedMD.countIndent(clickedItem)
            
            clickedItem.save()
            targetToSwap.save()

            ## the kids need their indent level changed in some instances.
            if (originalCIindentLevel != clickedItem.indentLevel):
                for k in kidList:
                    kObj = Item.objects.get(pk=k)
                    kObj.indentLevel = sharedMD.countIndent(kObj)
                    kObj.save()

           
            updateListIDs=[ clickedItem.id, tts_follows,bts_follows ] + kidList
            sharedMD.logThis('---', "updateListIDs: "+str(updateListIDs))
            #sharedMD.logThis("updateListIDs deco: "+str(self.updateIDsDecorate(updateListIDs)))
            return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# drag_move
 
    #@login_required
    def drag_move(self, request, CIid, TIid):
        sharedMD.logThis(request.user.username, "VIEW: drag_move")
        request.session['viewmode'] = 'drag_move'
    


        CI=Item.objects.get(pk=CIid)
        TI=Item.objects.get(pk=TIid)
        sharedMD.logThis(request.user.username, "     ====dragMove=> CIid:TIid    "+str(CIid)+":"+str(TIid))

        #### check for valid owner ##############
        if CI.owner != request.user.username:
            sharedMD.logThis(request.user.username, '     == WARNING: drag_move of item not belonging to this user.')
            #request.user.message_set.create (message="You don't own that item.")
            updateThese = self.updateIDsDecorate([CI.id, TI.id])
            return(updateThese) 


        #### check for invalid actions ####################

        moveWarning = ''

        #### can't drag CI onto item it followers
        if CI.follows == TI.id:
            moveWarning = '== WARNING: drag_move of item onto item it follows is invalid. Not executing.'

        #### CAN drag CI onto item that follows it (if TI is not also a kid)
        #if CI.id == TI.follows:
        #    moveWarning = '== WARNING: drag_move of item onto item following it is invalid. Not executing.'

        #### can't drag onto self 
        if CI.id == TI.id:
            moveWarning = '== WARNING: drag_move of item onto SELF is invalid.  Not executing.'


        #### can't drag onto your kid
        if TI.parent == CI.id:
            moveWarning = '== WARNING: drag_move of item onto CHILD is invalid.  Not executing.'



        if moveWarning != '':
            ###ABORT
            sharedMD.logThis(request.user.username, '     ' + moveWarning)
            updateThese = self.updateIDsDecorate([CI.id, TI.id])
            return(updateThese) 


        #############################################


        lastItemID=sharedMD.getLastItemID(CI.project_id)

        origCIparent=CI.parent
        origCIfollow=CI.follows

        origTIparent=TI.parent
        origTIfollow=TI.follows

        ### if TI is lastItem, don't try to find its follower
        if TI.id != lastItemID:
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

        #sharedMD.logThis(request.user.username, "DragMove=> stitch around CI done")
        ## now insert the moved item into it's new position
        CI.parent = TIid;  ## was origTIparent
        CI.follows = TIid;
        CI.indentLevel = TI.indentLevel+1
        CI.save()
        sharedMD.logThis(request.user.username, "     DragMove=> CI saved")

        ## item that followed the target now must follow the CI, or the CI's last child (if any)

        if TI.id != lastItemID:
            if lastKidID == 0:
                targetFollower.follows=CI.id
                targetFollower.save()
            else:
                targetFollower.follows=lastKidID
                targetFollower.save()

            sharedMD.logThis(request.user.username, '     dragmove=> targetFollowerID:'+str(targetFollower.id)+'  targetFollower.follows:'+str(targetFollower.follows) + '  lastkid:'+str(lastKidID))

        ##  correct indentLevel, since parent indent might have changed
        sharedMD.logThis(request.user.username, '      dm=>kidList = '+str(kidList))

        kidItems=[]
        for kidx in kidList:
            #kidx used to be kidpair[]
            thisKid=Item.objects.get(pk=kidx)
            thisKid.indentLevel = sharedMD.countIndent(thisKid)
            thisKid.save()
            sharedMD.logThis(request.user.username, '      dm=>kidx / indentL = '+str(thisKid.id)+"/"+str(thisKid.indentLevel))


            #### extend kidItems (formerly kidPair( -- add the info JS refreshItem function will need

            kidItems.append([thisKid.id, thisKid.follows, thisKid.title, thisKid.parent, thisKid.indentLevel, thisKid.priority, thisKid.status, thisKid.HTMLnoteBody, sharedMD.returnMarker(thisKid), thisKid.statusText()])

        parentKidUpdate = []

        parentKidUpdate.append([CI.id, CI.follows, CI.title, CI.parent, CI.indentLevel,CI.priority, CI.status, CI.HTMLnoteBody,sharedMD.returnMarker(CI),CI.statusText() ] )

        ## when drag-moving in CLOSE QUARTERS, an item like TI might go stale, b/c
        ## it was changed by, ex., b/c it was ALSO CI follower or some such. SO for
        ## now, let's get a fresh TI to write out.

        newTI=Item.objects.get(pk=TI.id)

        parentKidUpdate.append([newTI.id, newTI.follows, newTI.title, newTI.parent, newTI.indentLevel,newTI.priority, newTI.status,  newTI.HTMLnoteBody, sharedMD.returnMarker(newTI), newTI.statusText() ] )

        ## have to refresh the CI's parent, in case it's marker has changed w/ the move
        ## IF the parent != 0

        if origCIparent != 0:
            CIparent=Item.objects.get(pk=origCIparent)
            parentKidUpdate.append([CIparent.id, CIparent.follows, CIparent.title, CIparent.parent, CIparent.indentLevel, CIparent.priority, CIparent.status, CIparent.HTMLnoteBody, sharedMD.returnMarker(CIparent), CIparent.statusText()] )

        parentKidUpdate += kidItems

        return(parentKidUpdate)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# drag_peer

    def drag_peer(self,request, clickedItemID,targetItemID):

        clickedItem = Item.objects.get(pk=clickedItemID)
        targetItem = Item.objects.get(pk=targetItemID)
        sharedMD.logThis(request.user.username, "     ====dragPeer=> CIid:TIid    "+str(clickedItemID)+":"+str(targetItemID))
        
        CIfollowed = clickedItem.follows

        #### check for valid owner ##############
        if clickedItem.owner != request.user.username:
            sharedMD.logThis(request.user.username, '     == WARNING: drag_peer of item not belonging to this user.')
            updateThese = self.updateIDsDecorate([clickedItem.id, targetItem.id])
            return(updateThese) 


        #### check for invalid actions ####################

        moveWarning = ''

        #### can't drag CI onto item it followers
        if clickedItem.follows == targetItem.id:
            moveWarning = '== WARNING: drag_peer of item onto item it follows is invalid. Not executing.'

        ### TEMPORARILY INVALIDATED DRAG_PEER ONTO OWN PARENT  #######
        ### peer-drag to own parent should be possible
        ### but it's erroring: TI ends up following itself
        ##
        ### probably b/c the parent and the CI both could have kids,
        ### and establishing lastkids etc might get confused.
        ### NEEDS UNCOMMENTING + DEBUGGING
        #### CAN drag CI onto item that follows it (if TI is not also a kid)
        if clickedItem.parent == targetItem.id:
            moveWarning = '== WARNING: drag_peer of item onto its parent is temporarily invalid. Not executing, sorry.'

        #### can't drag onto self 
        if clickedItem.id == targetItem.id:
            moveWarning = '== WARNING: drag_peer of item onto SELF is invalid.  Not executing.'


        #### can't drag onto your kid
        if targetItem.parent == clickedItem.id:
            moveWarning = '== WARNING: drag_peer of item onto CHILD is invalid.  Not executing.'



        if moveWarning != '':
            ###ABORT
            sharedMD.logThis(request.user.username, '     ' + moveWarning)
            updateThese = self.updateIDsDecorate([clickedItem.id, targetItem.id])
            return(updateThese) 


        #############################################
        
    
        lastItemID = sharedMD.getLastItemID(clickedItem.project_id)
        lastKidofCI, CIkidList = sharedMD.findLastKid(clickedItem, lastItemID)
        lastKidofTI, TIkidList = sharedMD.findLastKid(targetItem, lastItemID)

        if lastKidofCI != lastItemID:
            if lastKidofCI != 0:
                lastCIkidFollower = Item.objects.get(follows=lastKidofCI).id
            else:
                lastCIkidFollower = Item.objects.get(follows=clickedItem.id).id
        else:
            lastCIkidFollower = -999

        sharedMD.logThis(request.user.username,  "    ==> drag_Peer, CI / TI:"+str(clickedItem.id)+"/"+str(targetItem.id))
 

        followOK = False 
        updateListIDs = []
        
        # move CI: follows; note the TI follower for later
        if lastKidofTI == 0:
            if targetItem.id != lastItemID:
                wasFollowingTI = Item.objects.get(follows=targetItem.id)
                followOK = True
            clickedItem.follows = targetItem.id
            
        else:
            if lastKidofTI != lastItemID:
                wasFollowingTI = Item.objects.get(follows=lastKidofTI)
                followOK = True
            clickedItem.follows = lastKidofTI

        # move CI: parent
        clickedItem.parent = targetItem.parent

        # fix CI indentLevel
        clickedItem.indentLevel = sharedMD.countIndent(clickedItem)


        if lastKidofCI == 0:
            lastCIitem = clickedItem.id
            
        else:
            lastCIitem = lastKidofCI

        # fix the item that followed TI so it follows CI
        if followOK:
            wasFollowingTI.follows = lastCIitem
            wasFollowingTI.save()

        
        #reset item that originally followed lastCIitem, by stitching to item
        # that original was followed by CI
        if lastCIkidFollower != -999:
            LCIFobj = Item.objects.get(pk=lastCIkidFollower)
            LCIFobj.follows = CIfollowed
            updateListIDs =  [ LCIFobj.id ]
            LCIFobj.save()
        
            
        clickedItem.save()
        targetItem.save()

        ## fix my kids:
        for k in CIkidList:
            ko=Item.objects.get(pk=k)
            ko.indentLevel = sharedMD.countIndent(ko)
            ko.save()
        
        ## try to list in follow order, so JavaScript correctly does the DOM inserts
        updateListIDs += [targetItem.follows, targetItem.id] + TIkidList + [clickedItemID, clickedItem.follows] + CIkidList 

                
        return(self.updateIDsDecorate(updateListIDs))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveUp (via peers only)

    def moveUp(self,clickedItem,  lastItemID):
        
        lastKidofCI, CIkidList = sharedMD.findLastKid(clickedItem, lastItemID)
        
        if Item.objects.get(pk=clickedItem.follows).follows == 0:
            sharedMD.logThis('---',  "==> Clicked item first item, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
            return([])

        ## Locate the previous item with the same parent as me
        ## stop completely if you hit an item with the same grandparent as me
        if clickedItem.parent == 0:
            grandParent = 99999
        else:
            grandParent = Item.objects.get(pk=clickedItem.parent).parent

        sharedMD.logThis('---',  "  moving among children of "+str(clickedItem.parent))

        haveFoundItem = 'no'
        indx=Item.objects.get(pk=clickedItem.follows)
        while (indx.follows != 0 ) and (indx.parent != grandParent) and (haveFoundItem == 'no'):
            if (indx.parent != clickedItem.parent):
                indx = Item.objects.get(pk=indx.follows)
            else:
                haveFoundItem = 'yes'
                targetItem = indx

        if haveFoundItem == 'no':
            sharedMD.logThis('---',  "  no valid moveUp found ")
            return([])

        sharedMD.logThis('---',  "  TI:  "+str(targetItem.id))
        # targetItem is the item we aim to move CI and its kids before    


        lastKidofTI, TIkidList = sharedMD.findLastKid(targetItem, lastItemID)
 
        #CIfollowed = clickedItem.follows
        #targetItemFollowedThis = targetItem.follows

        followOK = False 
        updateListIDs = []
        
        # move CI
        clickedItem.follows = targetItem.follows

        # move TI
        if lastKidofCI == 0:
            if clickedItem.id != lastItemID:
                CILastItemWasFollowedBy = Item.objects.get(follows=clickedItem.id)
                followOK = True
                
            targetItem.follows = clickedItem.id
        else:
            if lastKidofCI != lastItemID:
                CILastItemWasFollowedBy = Item.objects.get(follows=lastKidofCI)
                followOK = True

            targetItem.follows = lastKidofCI
        
        # reset CI's last follower
        if followOK:
            if lastKidofTI == 0:
                CILastItemWasFollowedBy.follows = targetItem.id
            else:
                CILastItemWasFollowedBy.follows = lastKidofTI
            CILastItemWasFollowedBy.save()

            
        clickedItem.save()
        targetItem.save()

        
        ## try to list in follow order, so JavaScript correctly does the DOM inserts
        updateListIDs += [targetItem.follows, targetItem.id] + TIkidList + [clickedItem.follows, clickedItem.id] + CIkidList 
        if followOK:
            updateListIDs +=  [ CILastItemWasFollowedBy.id ]
                
        return(self.updateIDsDecorate(updateListIDs))



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveDown  (via peers only)

    def moveDown(self,clickedItem,  lastItemID):
        
        lastKidofCI, CIkidList = sharedMD.findLastKid(clickedItem, lastItemID)
        
        if clickedItem.id == lastItemID or lastKidofCI == lastItemID:
            sharedMD.logThis('---',  "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
            return([])

        ## Locate the next following item with the same parent as me
        ## stop completely if you hit an item with the same grandparent as me
        if clickedItem.parent == 0:
            grandParent = 99999
        else:
            grandParent = Item.objects.get(pk=clickedItem.parent).parent
            
        sharedMD.logThis('---',  "  moving among children of "+str(clickedItem.parent))

        haveFoundItem = 'no'
        indx=Item.objects.get(follows = clickedItem.id)
        while (indx.id != lastItemID) and (indx.parent != grandParent) and (haveFoundItem == 'no'):
            if (indx.parent != clickedItem.parent):
                indx = Item.objects.get(follows = indx.id)
            else:
                haveFoundItem = 'yes'
                targetItem = indx

        if haveFoundItem == 'no':
            sharedMD.logThis('---',  "  no valid moveDown found ")
            return([])


        sharedMD.logThis('---',  "  TI:  "+str(targetItem.id))
        # targetItem is the item we aim to move CI and its kids after    


        lastKidofTI, TIkidList = sharedMD.findLastKid(targetItem, lastItemID)
 
        #CIfollowed = clickedItem.follows
        #targetItemFollowedThis = targetItem.follows
        
        # move TI
        targetItem.follows = clickedItem.follows

        # move CI
        TLIWFBok = False
        
        if lastKidofTI == 0:
            clickedItem.follows = targetItem.id

            if targetItem.id != lastItemID:
                targetLastItemWasFollowedBy = Item.objects.get(follows=targetItem.id)
                TLIWFBok = True

        else:
            clickedItem.follows = lastKidofTI
            if lastKidofTI != lastItemID:
                targetLastItemWasFollowedBy = Item.objects.get(follows=lastKidofTI)
                TLIWFBok = True

        
        # reset CI's last follower
        if TLIWFBok:
            if lastKidofCI == 0:
                targetLastItemWasFollowedBy.follows = clickedItem.id
            else:
                targetLastItemWasFollowedBy.follows = lastKidofCI
            targetLastItemWasFollowedBy.save()
        
        clickedItem.save()
        targetItem.save()

        
        ## try to list in follow order, so JavaScript correctly does the DOM inserts
        updateListIDs = [clickedItem.follows, clickedItem.id] + CIkidList + [targetItem.follows, targetItem.id] + TIkidList

        if TLIWFBok:
            updateListIDs += [targetLastItemWasFollowedBy.id ] 
        
        return(self.updateIDsDecorate(updateListIDs))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# promote

    def promote(self,clickedItem,  lastItemID):

        lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)
        CIoriginalParent=clickedItem.parent

        if clickedItem.parent ==  0:
            sharedMD.logThis('---',  "CAN'T PROMOTE TOP-LEVEL "+ str(clickedItem.id))
            return([])
        
        else:
            sharedMD.logThis('---', "Promoting: " +str(clickedItem.id))

            clickedItem.parent = Item.objects.get(pk=CIoriginalParent).parent
            clickedItem.indentLevel = sharedMD.countIndent(clickedItem)
            clickedItem.save()

            ## fix CI's kids indentLevel:
            for k in kidList:
                ko=Item.objects.get(pk=k)
                ko.indentLevel = sharedMD.countIndent(ko)
                ko.save()

            if clickedItem.id != lastItemID:

                ######################KIDNAP####################################################
                ## if items following the promotee have CI's original parent, AND we haven't
                ## hit an item with the same parent as the CI's NEW parent, then kidnap it
                ## (i.e., the CI is it's new parent)
                ## No need to fix indent level, kidnapped items remain as before

                if lastKidID != lastItemID and lastKidID != 0:
                    kidnapStart = lastKidID
                else:
                    kidnapStart = clickedItem.id

                indx =  Item.objects.get(follows = kidnapStart)


                sharedMD.logThis('---', "converting subsequent items to children starting at: "+str(kidnapStart))

                while (indx.id != lastItemID) and (indx.parent != clickedItem.parent):
                    sharedMD.logThis('---', "converting subsequent items to children...")
                    if (indx.parent == CIoriginalParent):
                        indx.parent = clickedItem.id

                        indx.save()
                        kidList.append(indx.id)
                    indx = Item.objects.get(follows = indx.id)
 

        ## now for refresh

        updateListIDs=[clickedItem.id, clickedItem.follows ] + kidList
        return(self.updateIDsDecorate(updateListIDs))



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# demote
    def demote(self,  clickedItem,  lastItemID):

        if clickedItem.parent==clickedItem.follows:
            sharedMD.logThis('---',  "Can't demote further, item "+str(clickedItem.id))
            return([])
        else:
            ## if CI and the item following it have same parent, just shift CI parent, and indent CI
            lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)

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
            sharedMD.logThis('---',  "Item has no follower: ID" + str(clickedItem.id))
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
        sharedMD.logThis('---',  "==> deleting "+str(clickedItem.id))
        # remove item
        clickedItem.delete()
        
        return(toUpdate)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# swapWithArchivePair ##
    
    def swapWithArchivePair(self, clickedItem, lastItemID):

        ghostsID = clickedItem.id
        ghostFollowsID = clickedItem.follows
        ghostsParentID = clickedItem.parent

        lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)


        updateThese = [ghostsParentID, ghostFollowsID]
        
        if clickedItem.id != lastItemID:
            
            followingMe = Item.objects.get(follows=clickedItem.id)
            updateThese.append(followingMe.id)
            followingMe.follows=clickedItem.follows
            followingMe.save()
               
            if kidList != []:
                ## fix my kids:
                for k in kidList:
                    
                    ko=Item.objects.get(pk=k)
                    if ko.parent == clickedItem.id:
                        ko.parent = clickedItem.parent
                    ko.indentLevel = sharedMD.countIndent(ko)
                    ko.save()
                    
                    updateThese.append(ko.id)
            else:
                followingMe.parent=clickedItem.parent
 
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
        sharedMD.logThis('---',  "==> archivePair moved item "+str(clickedItem.id)+"  to proj: " +str(clickedItem.project.id)    )
        
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# fastAdd
    #@login_required - uh oh, no request context
    def fastAdd(self,  clickedItem, FADtitle, FADstatus, FADpriority, FADhtmlBody):
        sharedMD.logThis('---', "VIEW: drag_actions => fastAdd")

        #clickedItem=Item.objects.get(pk=clickedItemID)

        sharedMD.logThis('---', "fastAdd for "+str(clickedItem.id)+"  "+FADtitle)

        ##sharedMD.getLastItemID(clickedItem.project.id)
        
        ## find the item that was following clickedItem
        try:
            oldFollower = Item.objects.get(follows=clickedItem.id)
            follower=True
        except:
            sharedMD.logThis('---',  "Item has no follower: ID" + str(clickedItem.id))
            follower = False
        
        newItem = Item(title=FADtitle,priority=FADpriority, status=FADstatus, \
                       follows=clickedItem.id, \
                       HTMLnoteBody=FADhtmlBody )


        newItem.owner = clickedItem.project.owner
        
        newItem.project = clickedItem.project

        
        sharedMD.logThis('---', "NEW FA item ID=" + str(newItem.id))


        ## if clickedItem has kids, the fastAdded item should be a kid.
        ##   if not, it should be a peer
        ciKidCount = Item.objects.filter(parent=clickedItem.id).count()
        if (ciKidCount) == 0:
            newItem.parent = clickedItem.parent
            newItem.indentLevel=clickedItem.indentLevel
        else:
            newItem.parent = clickedItem.id
            newItem.indentLevel = clickedItem.indentLevel+1

        newItem.save()
        sharedMD.logThis('---', "   fastadded item ID = " + str(newItem.id));
        updateListIDs=[newItem.id, clickedItem.id]
        if clickedItem.follows != 0:
            updateListIDs.append(clickedItem.follows) 

        if follower:
            oldFollower.follows = newItem.id
            oldFollower.save()
            updateListIDs.append(oldFollower.id)

            
        newItemTemplate= '''

        <div class="itemsdrag bhdraggable dropx"  id="xxxID"  onclick="selectMe(this)">
     
       <span class="itemDragWidgetBlock">

<form>
            <span class="prio_stat_btns"> 

<select class="prioritySelect" onChange="prioritySelected(xxxID);"  >
  <option value="1" >TODAY</option>
  <option value="2" >Urgent</option>
  <option value="3" >Important</option>
  <option value="4" >Normal</option>
  <option value="5" >Low</option>
  <option value="0"selected="selected" ></option>
</select>

<select class="statusSelect" onChange="statusSelected(xxxID);"   >
  <option value="1" >WIP</option>
  <option value="2" >Next</option>
  <option value="3" >Cold</option>
  <option value="4" >Ongoing</option>
  <option value="5" >Hold</option>
  <option value="6" >Cancelled</option>
  <option value="8" >Ref</option>
  <option value="9" >Done</option>
  <option value="0" selected="selected"></option>
</select>

	      <a href="#" class="fastAddLink simpleDisappear" onClick='showFastAddDialog(xxxID)'>&plus;</a>
	      <a href="#" class="archiveLink simpleDisappear" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"archiveThisItem")'>a</a>
</form>


         <a class="itemControlWidget" id="itemControl_xxxID" onMouseover="itemControlWidget('xxxID')">&raquo;</a>
	     
           </span>


        </span><!-- itemdragWidgetBlock  -->




   <span class="itemDragContentBlock">
   <span class="print_prioStat">xxxPriority:xxxStatus</span>
        <div class="itemdrag titleContainer">
	     
	      <div  class="indentHolder indent_xxxIndentLevel xxxParentItem }} ">
		
		 <a href="/pim1/item/edititem/xxxID" class="titlelink" >
                     <span class="marker"></span>
                     <span class="titletext">xxxItemTitle</span></a> 
	      </div> 
	   


	      <span class="noteExpandWidget"> 
                
                  <a onClick="toggleNoteBody('notebody_xxxID');" class="noteplus">&oplus;</a>&nbsp;<a onClick='detailpop("xxxID")' class="notearr">&rArr;</a> 
               
              </span>

	</div> 

     

    </span> 




          <div id="notebody_xxxID" class="noteBody">
            <div class="noteWrapper">xxxNoteBody</div>
          </div>       

  </div>      <!--  .itemsdrag -->

   <div class="itemDivider" id="itemDivider_xxxID" >xxxID</div>

        '''

        newItemTemplate=newItemTemplate.replace('xxxID',str(newItem.id))
        newItemTemplate=newItemTemplate.replace('xxxItemTitle',newItem.title)
        newItemTemplate=newItemTemplate.replace('xxxNoteBody',newItem.HTMLnoteBody)
        newItemTemplate=newItemTemplate.replace('xxxIndentLevel',"indent_"+str(sharedMD.countIndent(newItem)))
        newItemTemplate=newItemTemplate.replace('xxxPriority',newItem.priorityText())
        newItemTemplate=newItemTemplate.replace('xxxStatus',newItem.statusText())


        return(self.updateIDsDecorate(updateListIDs), newItemTemplate)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# prioritySelected   ## for the pop-up boxes

    def prioritySelected(self,  CI,  pValue):

        #choices=CI.PRIORITY_CHOICES; ## (('1', "urgent"),("2", "Important),(...
        
        CI.priority = pValue;

        CI.save()

 
        return(self.updateIDsDecorate([CI.id]))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# statusSelected   ## for the pop-up boxes

    def statusSelected(self,  CI,  sValue):

        #choices=CI.STATUS_CHOICES; ## (('1', "urgent"),("2", "Important),(...
        
        CI.status = sValue;

        CI.save()

 
        return(self.updateIDsDecorate([CI.id]))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# doOrderSelected   ## for the pop-up boxes

    def doOrderSelected(self,  CI,  dValue):

        CI.doOrder = dValue;

        CI.save()

 
        return(self.updateIDsDecorate([CI.id]))
