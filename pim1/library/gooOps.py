class gooOps():
    '''General operations for interacting with Google app APIs'''

    def __init__(self):
        temp = None



    def WSAtaskAPIconnect(self, request):
        ##
        # if we decide to revive the gTask link-up, implement
        # OAuth 2 for Web Servers, and integrate it properly with Benk accounts.

        # ++ probably store OAuth credentials in the Django user object.
        
        # see https://code.google.com/p/google-api-python-client/wiki/OAuth2
        # https://developers.google.com/accounts/docs/OAuth2WebServer


        
        '''Build service object for interacting with Tasks API. Will refactor as other services
           are brought into use.'''

        from django.http import HttpResponse, HttpResponseRedirect

        import sys
        sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/pengine')



        import sharedMD
        import httplib2  #, gflags
        
        from apiclient.discovery import build
        from oauth2client.file import Storage
        from oauth2client.client import OAuth2WebServerFlow
        from oauth2client.tools import run

        sharedMD.logThis('gooOps','gooOps: imported modules')
        

        #FLAGS = gflags.FLAGS
    

        # check that creditionals are valid
        storage = Storage('tasks.dat')
        credentials = storage.get()
        sharedMD.logThis('gooOps','...credentials created')


        #userx = 'agent.x39'  ##users.get_current_user()
        #credentials = StorageByKeyName(Credentials, userx, 'credentials').get()

        
        if credentials is None or credentials.invalid == True:
            sharedMD.logThis('gooOps','...credentials invalid, running new flow')
            # Flow object for authentication (OAuth 2.0)
            # using a web auth flow, rather than the previous application workflow
            WEBFLOW = OAuth2WebServerFlow(
                client_id='979231898847-rkbun6eifu79anm57i45acbfghah9d81.apps.googleusercontent.com',
                client_secret='O7Vm-yRICLR2WyI8C5o7jUrg',
                scope='https://www.googleapis.com/auth/tasks',
                user_agent='Task2ss/0.01')

            sharedMD.logThis('gooOps','....WEBFLOW created' )

            
            #credentials = run(WEBFLOW, storage)
            #sharedMD.logThis('gooOps','...credentials created')

            callback = 'http://dx.bernardhecker.com/pim1/item/gooUpdate'
            authorize_url = WEBFLOW.step1_get_authorize_url(callback)
            sharedMD.logThis('gooOps','...authorize_url:'+authorize_url)
            
            return ('',HttpResponseRedirect(authorize_url) )


        else:
            sharedMD.logThis('gooOps','credentials OK...')


            # Create httplib2.Http object, authorize
            http = httplib2.Http()
            http = credentials.authorize(http)

            sharedMD.logThis('gooOps','...http authorized')
        
            # instantiate service object
            # developerKey seems deprecated, using application key 
            service = build(serviceName='tasks', version='v1', http=http, developerKey='AIzaSyCQb3rbzyEqshlSSAI4tko19ao0PPTVtro')


            sharedMD.logThis('gooOps','...service built')


            return(service,'')
    


    #######################################################
    # original, non-interactive
    def taskAPIconnect(self, request):
        # original, from Tasks doc's
        #   worked last year from PC-based implementation
        # .. https://developers.google.com/google-apps/tasks/instantiate
        
        '''Build service object for interacting with Tasks API. Will refactor as other services
           are brought into use.'''


        import sys
        sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/pengine')

        import sharedMD
        import httplib2, gflags
        
        from apiclient.discovery import build
        from oauth2client.file import Storage
        from oauth2client.client import OAuth2WebServerFlow
        from oauth2client.tools import run
    
        sharedMD.logThis('gooOps','gooOps: imported modules')
        

        FLAGS = gflags.FLAGS
    


        # Flow object for authentication (OAuth 2.0)
        FLOW = OAuth2WebServerFlow(
            client_id='979231898847.apps.googleusercontent.com',
            client_secret='p2XbOmu-Uu1YqBCci0cnCFwM',
            scope='https://www.googleapis.com/auth/tasks',
            user_agent='Task2ss/0.01')

        sharedMD.logThis('gooOps','FLOW created')

        # check that creditionals are valid
        storage = Storage('tasks.dat')
        credentials = storage.get()

        sharedMD.logThis('gooOps','credentials created...')

        ### HANGS here  now####
        if credentials is None or credentials.invalid == True:
          credentials = run(FLOW, storage)

        sharedMD.logThis('gooOps','flow run...')


        # Create httplib2.Http object, authorize
        http = httplib2.Http()
        http = credentials.authorize(http)

        sharedMD.logThis('gooOps','...http authorized')
        

        # instantiate service object
        # developerKey seems deprecated, using application key 
        service = build(serviceName='tasks', version='v1', http=http,
               developerKey='AIzaSyCQb3rbzyEqshlSSAI4tko19ao0PPTVtro')


        sharedMD.logThis('gooOps','...service built')


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










