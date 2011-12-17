class gooOps():
    import gflags
    import httplib2
    
    from apiclient.discovery import build
    from oauth2client.file import Storage
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run
    
    FLAGS = gflags.FLAGS
    
    def __init__(self):
        temp = None

    def taskAPIconnect(self):

        # Flow object for authentication (OAuth 2.0)
        FLOW = OAuth2WebServerFlow(
            client_id='979231898847.apps.googleusercontent.com',
            client_secret='p2XbOmu-Uu1YqBCci0cnCFwM',
            scope='https://www.googleapis.com/auth/tasks',
            user_agent='Task2ss/0.01')

        # check that creditionals are valid
        storage = Storage('tasks.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid == True:
          credentials = run(FLOW, storage)

        # Create httplib2.Http object, authorize
        http = httplib2.Http()
        http = credentials.authorize(http)

        # instantiate service object
        # developerKey seems deprecated, using application key 
        service = build(serviceName='tasks', version='v1', http=http,
               developerKey='AIzaSyCQb3rbzyEqshlSSAI4tko19ao0PPTVtro')

        return(service)
    

    ##############################################################################
    def pullGooTasks (self):

        ## removed setup info to top of module

        ## This isn't a part of benk. Just stashing a copy here for now. 
        
        def recursiveList (pHash, kid, tasksx, seqIDx, tabLevel):        
                for child in pHash[kid]: 
                    print tabLevel*'\t',tasksx['items'][seqIDx[child]]['title']
                    if child in pHash.keys():
                        recursiveList(pHash, child, tasksx, seqIDx, tabLevel+1)

        ##############################################################################


        BHtasklists = service.tasklists().list().execute()

        for tasklist in BHtasklists['items']:
            print '============================================================='
            print tasklist['title']
            tasks = service.tasks().list(tasklist=tasklist['id']).execute()

            # tasks['items'][3]['position']
            # for top level item, make parent =0
            # make hash of parents, where key is parent ID, value is *array* of child IDs
            # make seqID table, where key is item ID, and value is "c", i.e., sequence of item in tasks['items'] array

            seqID = {}        ## seqID   task ID => tasks['items'] array index
                              ## enables quick referral back to where
                              ## in the tasks['items'][??] array a particular task is

            # build parent hash and seqID hash
            parentHash = {}   ## parent ID => list of child IDs for that parent

            for task in tasks['items']:
                if not task.has_key('parent'):
                    task['parent']='0'  ## top-level items are given parent=0
                if not parentHash.has_key(task['parent']):
                    parentHash[task['parent']]=[]
                parentHash[task['parent']].append(task['id'])

                seqID[task['id']]=tasks['items'].index(task)

            ## start with hash of top-level items (i.e., which have no parents),
            ##    and walk through those
            ## need to start iteration with the top level item that has lowest position
            topOrder={}  # position => id, for items with parent = 0 (top-level items)
            for tln in parentHash['0']:
                topOrder[tasks['items'][seqID[tln]]['position']]=tasks['items'][seqID[tln]]['id']
                # ouch

            topOrderKeys=topOrder.keys()
            topOrderKeys.sort()

            for topKey in topOrderKeys:
                print "*", tasks['items'][seqID[topOrder[topKey]]]['title']
                # IF there are children, print them
                if topOrder[topKey] in parentHash.keys():
                    recursiveList(parentHash, topOrder[topKey],tasks,seqID, 1)










