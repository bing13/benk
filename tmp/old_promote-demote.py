
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# OLDmoveDown

    def OLDmoveDown(self,clickedItem,  lastItemID):
        
        ### may wish to remodel so it looks like "moveup", which uses the findLastKid method

        lastKidofCI, kidList = sharedMD.findLastKid(clickedItem, lastItemID)
        
        if clickedItem.id == lastItemID or lastKidofCI == lastItemID:
            sharedMD.logThis('---',  "==> Clicked item is last item or last parent, no move:ci, lk, liID "+str(clickedItem.id) +"  " + str(lastKidofCI) + '  ' + str(lastItemID))
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
            sharedMD.logThis('---',  "CAN'T PROMOTE TOP-LEVEL "+ str(clickedItem.id))

        else:
            ### Deal with parent assignments first

            sharedMD.logThis('---', "Promoting: " +str(clickedItem.id))
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
                    sharedMD.logThis('---', "converting subsequent items to children...")
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
                    sharedMD.logThis('---', "k-promote: LastKidID="+str(lastKidID))
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
