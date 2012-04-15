###########################################################################
# repairChain
#               repairs un-linked segments. naively.


def repairChain(proj_id):

    # CHANGES HERE MUST BE INCORPORATED INTO SHOWCHAINS and vice versa,
    # until we re-factor

    ix = anchor
    tableID = 0
    tables = []
    for endPoint in noFollowers:

        chainEnd = False;
        ix = endPoint
        outputRows = []

        thisRun = []
        while not chainEnd:
            thisRun.append(ix.id)
            try:
                ix = Item.objects.get(id=ix.follows);
                
            except:
                chainEnd = True;

        thisRun.reverse()
        tables.append(thisRun)
        

    recommendedResult = []
    for cx in range(0, len(tables)-1):
        
        ##select each value in the first table
        for j in tables[cx]:
            for k in range(cx+1, len(tables)):
                if j in tables[k]:
                    tables[k].remove(j)
                
    sharedMD.logThis("repairChain: tables w/dupes removed:" + str(tables))

    ###ANCHOR MUST GO FIRST####
    for x in range(0,len(tables)):
        if Item.objects.get(id=tables[x][0]).parent == 0:
            anchorIn=x ## anchor is first item of this array

    if anchorIn != 0:
        tables.insert(0,tables[anchorIn])
        tables.pop(anchorIn)

    if len(tables) > 1:
        for i in (0, len(tables)-1):
            recommendedResult += tables[i];





    #######################################################
    t = loader.get_template('pim1_tmpl/showchains.html')
    c = Context({
        'displayTables':displayTables, 
        'current_projs':current_projs,
        'current_sets':current_sets,
        'noFollowers':noFollowers,
        'recommendedList':str(recommendedResult)[1:-1],
        'titleCrumbBlurb':'showchain proj:'+str(proj_id),
        'proj_id':proj_id,
        'nowx':datetime.datetime.now().strftime("%Y/%m/%d  %H:%M:%S")
    })
    return HttpResponse(t.render(c))
