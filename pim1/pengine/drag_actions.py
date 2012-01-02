## drag_actions.py
#
# actions that work with xhr requests
#

class dragOps():
    '''actions on benk display rows, suitable for xhr requests'''

    def __init__(self):
        temp = None

    def moveUp(self,clickedItem, lastKid, kidList):
        
        if clickedItem.follows==0:
            logThis( "CAN'T MOVE UP TOP item "+ str(pItem))
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
            return(updateIDsDecorate(updateListIDs))
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# updateIDsDecorate

    def updateIDsDecorate(self, IDlist):
        decoratedItems=[]
        for id in IDlist:
            thisItem=Item.objects.get(pk=id)
            decoratedItems.append([thisItem.title, thisItem.parent, thisItem.indentLevel, thisItem.priority, thisItem.status, thisItem.HTMLnoteBody, DAreturnMarker(thisItem)])
        return(decoratedItems)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# DAreturnMarker

    def DAreturnMarker(self,itemx):
        ## returns a plus or bullet, depending upon if Item has kids or not
        if len( Item.objects.filter(parent=Itemx.id) ) > 0:
            return("+")
        else:
            return("&bull;")
        
