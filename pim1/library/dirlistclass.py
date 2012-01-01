#!/usr/bin/python
###################################################################
##  quick directory lister
##  2011/12/30
###################################################################
''' directory lister, based upon bindex.cgi 2008/12/08 and before
'''
###################################################################

import sys,os,string


class dirList():
    '''general utility for rendering a file directory listing'''

    def listDir(self, targetDir):

        dirx=targetDir
        backgrnd=["blue-powder.gif", "orange-rings.gif","gray-dark-rock.gif", "brown-gray-pattern.gif","grey-satin1.jpeg","grey-brown-texture.gif"  ]


        ### get working directory
    #    cx = 'pwd'
    #    COMOUT=os.popen(cx,'r')
    #    raw_pwd = COMOUT.readlines()
    #    COMOUT.close()



        ## this one does recursive listing:
        ## cx = 'ls -orRA ' + dirx

        ### get dir list 
        cx= 'ls -la ' + dirx
        COMOUT=os.popen(cx,'r')
        ox = COMOUT.readlines()
        COMOUT.close()

        #print('Raw dir output:\n'+str(ox))

        pgtitle= "Directory of "+dirx

        ### for some reason a relative path works, an absolute path does not
        ### abs is needed b/c the directory you're looking at could be any number of
        ### directories below public_html. But the URL version works OK. So:
        #backgroundtile="http://highwire.stanford.edu/~bernard/images/bg/"+backgrnd[2]

        bx1 = "#ddddcc"
        bx2 = "#FFFFee"
        bx3 = "#FFCC66"
        bx = bx3

        #buildpage=standard_html.page_create()
        #buildpage.alt1_printhead(backgroundtile, pgtitle, 'no_form_needed')

        a=[]
        outx= "\n<font color='#ffffff'><p>"+pgtitle+"</p></font>"
        outx+= "\n<table>"

        for x in ox:

            a=x.split(None, 8)
            outx += '\n<tr bgcolor="'+ bx + '">'
            c=0 
            for y in a:
                if bx == bx1:
                    bx = bx2
                else:
                    bx = bx1

                if c != 8:
                    outx +=  '<td class="tab3">'+y+'</td>'
                else:
                    if y != 'index.cgi':
                        outx += '<td class="tab3"><a href="' +y+ '">' +y+ '</a>'
                c = c +1 
            outx += "</tr>"

        outx += "</table>"


        return(outx)

if __name__ == '__main__': # pragma: no cover
    ld=dirList()
    output=ld.listDir('/home/bhadmin13/dx.bernardhecker.com')
    print output
