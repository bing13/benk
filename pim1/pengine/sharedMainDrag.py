###
# modules that are shared between views.py and drag_actions.py
#
#################################

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# logThis
    def logThis(self, s, LOGFILE):
        LX = open(LOGFILE, 'a')
        t = datetime.datetime.now().strftime("%Y:%m:%d  %H:%M:%S")
        LX.write(t+":DA: "+s+'\n')
        LX.close
        return()


