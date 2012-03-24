## drag_actions.py ###################################################
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
                sharedMD.logThis( "  deco for: "+ str(id))
                thisItem=Item.objects.get(pk=id)
                decoratedItems.append([thisItem.id, thisItem.follows, thisItem.title, thisItem.parent, thisItem.indentLevel, thisItem.priority, thisItem.status, thisItem.HTMLnoteBody, sharedMD.returnMarker(self, thisItem), thisItem.statusText()])

                ## am concerned that other places where this list is build won't have statusText()
                
        return(decoratedItems)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# moveUpEveryItem

    def moveUpEveryItem(self,clickedItem, lastItemID):

        lastKid, kidList = sharedMD.findLastKid(clickedItem, lastItemID)
        originalCIindentLevel = clickedItem.indentLevel
        
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
            sharedMD.logThis("updateListIDs: "+str(updateListIDs))
            #sharedMD.logThis("updateListIDs deco: "+str(self.updateIDsDecorate(updateListIDs)))
            return(self.updateIDsDecorate(updateListIDs))



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# drag_peer

    def drag_peer(self,clickedItemID,targetItemID):

        clickedItem = Item.objects.get(pk=clickedItemID)
        targetItem = Item.objects.get(pk=targetItemID)

        CIfollowed = clickedItem.follows

  
        if clickedItem.follows == targetItem.id:
            ## invalid move
            sharedMD.logThis('== WARNING: drag_peer of item onto item it follows is invalid. Not executing.')
            updateThese = self.updateIDsDecorate([clickedItem.id, targetItem.id])
            sharedMD.logThis('    updating:'+str(updateThese))
       
            return(updateThese) 


    
        lastItemID=sharedMD.getLastItemID(clickedItem.project_id)
        lastKidofCI, CIkidList = sharedMD.findLastKid(clickedItem, lastItemID)
        lastKidofTI, TIkidList = sharedMD.findLastKid(targetItem, lastItemID)

        if lastKidofCI != lastItemID:
            if lastKidofCI != 0:
                lastCIkidFollower = Item.objects.get(follows=lastKidofCI).id
            else:
                lastCIkidFollower = Item.objects.get(follows=clickedItem.id).id
        else:
            lastCIkidFollower = -999

        sharedMD.logThis( "==> drag_Peer, CI / TI:"+str(clickedItem.id)+"/"+str(targetItem.id))
 

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
            sharedMD.logThis( "==> Clicked item first item, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
            return([])

        ## Locate the previous item with the same parent as me
        ## stop completely if you hit an item with the same grandparent as me
        if clickedItem.parent == 0:
            grandParent = 99999
        else:
            grandParent = Item.objects.get(pk=clickedItem.parent).parent

        sharedMD.logThis( "  moving among children of "+str(clickedItem.parent))

        haveFoundItem = 'no'
        indx=Item.objects.get(pk=clickedItem.follows)
        while (indx.follows != 0 ) and (indx.parent != grandParent) and (haveFoundItem == 'no'):
            if (indx.parent != clickedItem.parent):
                indx = Item.objects.get(pk=indx.follows)
            else:
                haveFoundItem = 'yes'
                targetItem = indx

        if haveFoundItem == 'no':
            sharedMD.logThis( "  no valid moveUp found ")
            return([])

        sharedMD.logThis( "  TI:  "+str(targetItem.id))
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
            sharedMD.logThis( "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
            return([])

        ## Locate the next following item with the same parent as me
        ## stop completely if you hit an item with the same grandparent as me
        if clickedItem.parent == 0:
            grandParent = 99999
        else:
            grandParent = Item.objects.get(pk=clickedItem.parent).parent
            
        sharedMD.logThis( "  moving among children of "+str(clickedItem.parent))

        haveFoundItem = 'no'
        indx=Item.objects.get(follows = clickedItem.id)
        while (indx.id != lastItemID) and (indx.parent != grandParent) and (haveFoundItem == 'no'):
            if (indx.parent != clickedItem.parent):
                indx = Item.objects.get(follows = indx.id)
            else:
                haveFoundItem = 'yes'
                targetItem = indx

        if haveFoundItem == 'no':
            sharedMD.logThis( "  no valid moveDown found ")
            return([])


        sharedMD.logThis( "  TI:  "+str(targetItem.id))
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
# OLDmoveDown

    def OLDmoveDown(self,clickedItem,  lastItemID):
        
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



            clickedItem.indentLevel = sharedMD.countIndent(clickedItem)


            clickedItem.save()
            fciFollower.save()

            updateListIDs=[clickedItem.id, clickedItem.follows, bottomToSwap.id, bottomFollower.id ] + kidList
            return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# OLDpromote

    def OLDpromote(self,clickedItem,  lastItemID):

        runKids='no'
        lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)
        CIoriginalParent=clickedItem.parent

        if clickedItem.parent ==  0:
            sharedMD.logThis( "CAN'T PROMOTE TOP-LEVEL "+ str(clickedItem.id))

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

        ciKidCount = Item.objects.filter(parent=clickedItem.id).count()
        kidsIDs = []
        if (ciKidCount > 0):
            kidsIDva = Item.objects.filter(parent=clickedItem.id).values_list('id',flat=True)

        kidsIDs += kidsIDva
        ## now for refresh

        updateListIDs=[clickedItem.id, clickedItem.follows ] + kidsIDs
        return(self.updateIDsDecorate(updateListIDs))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# promote

    def promote(self,clickedItem,  lastItemID):

        lastKidID,kidList=sharedMD.findLastKid(clickedItem, lastItemID)
        CIoriginalParent=clickedItem.parent

        if clickedItem.parent ==  0:
            sharedMD.logThis( "CAN'T PROMOTE TOP-LEVEL "+ str(clickedItem.id))
            return([])
        
        else:
            sharedMD.logThis("Promoting: " +str(clickedItem.id))

            clickedItem.parent = Item.objects.get(pk=CIoriginalParent).parent
            clickedItem.indentLevel = sharedMD.countIndent(clickedItem)
            clickedItem.save()

            ## fix my kids:
            for k in kidList:
                ko=Item.objects.get(pk=k)
                ko.indentLevel = sharedMD.countIndent(ko)
                ko.save()

            if lastKidID != lastItemID and lastKidID != 0:
                kidnapStart = lastKidID
            else:
                kidnapStart = clickedItem.id

            indx =  Item.objects.get(follows = kidnapStart)

            ######################KIDNAP####################################################
            ## if items following the promotee have CI's original parent, AND we haven't
            ## hit an item with the same parent as the CI's NEW parent, then kidnap it
            ## (i.e., the CI is it's new parent)
            ## No need to fix indent level, kidnapped items remain as before

            sharedMD.logThis("converting subsequent items to children starting at: "+str(kidnapStart))
               
            while (indx.id != lastItemID) and (indx.parent != clickedItem.parent):
                sharedMD.logThis("converting subsequent items to children...")
                if (indx.parent == CIoriginalParent):
                    indx.parent = clickedItem.id
                    
                    indx.save()
                    kidList.append(indx.id)
                indx = Item.objects.get(follows = indx.id)
            #    
            ##############################################################################
                

        #ciKidCount = Item.objects.filter(parent=clickedItem.id).count()
        #kidsIDs = []
        #if (ciKidCount > 0):
        #    kidsIDva = Item.objects.filter(parent=clickedItem.id).values_list('id',flat=True)

        #kidsIDs += kidsIDva
        ## now for refresh

        updateListIDs=[clickedItem.id, clickedItem.follows ] + kidList
        return(self.updateIDsDecorate(updateListIDs))



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# demote
    def demote(self,  clickedItem,  lastItemID):

        if clickedItem.parent==clickedItem.follows:
            sharedMD.logThis( "Can't demote further, item "+str(clickedItem.id))
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
        sharedMD.logThis( "==> archivePair moved item "+str(clickedItem.id)+"  to proj: " +str(clickedItem.project.id)    )
        
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

    def fastAdd(self,  clickedItem, FADtitle, FADstatus, FADpriority, FADhtmlBody):

        #clickedItem=Item.objects.get(pk=clickedItemID)

        sharedMD.logThis("fastAdd for "+str(clickedItem.id)+"  "+FADtitle)

        ##sharedMD.getLastItemID(clickedItem.project.id)
        
        ## find the item that was following clickedItem
        try:
            oldFollower = Item.objects.get(follows=clickedItem.id)
            follower=True
        except:
            sharedMD.logThis( "Item has no follower: ID" + str(clickedItem.id))
            follower=False


        newItem = Item(title=FADtitle,priority=FADpriority, status=FADstatus, \
           follows=clickedItem.id, \
           HTMLnoteBody=FADhtmlBody )
        newItem.project=clickedItem.project


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

        updateListIDs=[newItem.id, clickedItem.id, clickedItem.follows  ] 

        if follower:
            oldFollower.follows = newItem.id
            oldFollower.save()
            updateListIDs.append(oldFollower.id)

            
        newItemTemplate= '''

       <div class="itemsdrag bhdraggable dropx selectedItem"  id="xxxID"  onclick="selectMe(this)">
     
       <span class="itemDragWidgetBlock">

	    <span class="itemdrag actionArrows simpleDisappear"><a class="ilid simpleDisappear" href="/pim1/list-items/hoist/xxxID">xxxID&nbsp;://:</a><span class="simpleDisappear arrowItems">&nbsp;<a href="/pim1/item/add/xxxID">&harr;</a><a href="#" onClick='actionJax(xxxID,0,"promote")' >&larr;</a><a href="#"  onClick='actionJax(xxxID,0,"demote")'>&rarr;</a><a href="#xxxID" onClick='actionJax(xxxID,0,"moveUp")'>&uarr;</a><a href="#xxxID" onClick='actionJax(xxxID,0,"moveDown")'>&darr;</a></span></span>



            <span class="prio_stat_btns">

	      <a href="#" class="fastAddLink" onClick='showFastAddDialog(xxxID)'>&loz;</a>
	      <a href="#" class="archiveLink simpleDisappear" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"archiveThisItem")'>a</a>

              <span class="js_statprio simpleDisappear" onClick='actionJax( xxxID,0,"incPriority")'>+</span>
              <span  class="js_statprio simpleDisappear"onClick='actionJax( xxxID,0,"decPriority")'>-</span>

           <span class="prio priority_xxx"></span>

               <span class="js_statprio simpleDisappear" onClick='actionJax( xxxID,0,"incStatus")'>+</span>
               <span class="js_statprio simpleDisappear" onClick='actionJax( xxxID,0,"decStatus")'>-</span>

	     
           </span>

        </span><!-- itemdragWidgetBlock  -->

   <span class="itemDragContentBlock">
        <span class="itemdrag ti">
	     <a href="/pim1/item/edititem/xxxID" class="xxxstatusText titlelink">
	      <span  class="indentHolder indent_xxxIndentLevel xxxParentItem ">
		 <span class="marker"></span>
		 <span class="titletext">xxxItemTitle</span> 
 
	      </span> 
	     </a> 

<span class="noteExpandWidget"> <a onClick="toggleNoteBody('notebody_xxxID');" class="noteplus">&oplus;</a>&nbsp;<a onClick='detailpop("xxxID")' class="notearr">&rArr;</a> </span>

	</span>


    </span>  <!-- itemDragContentBlock -->


 

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
