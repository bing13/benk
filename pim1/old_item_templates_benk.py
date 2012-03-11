 RETIREDnewItemTemplate= ''' <div class="itemsdrag bhdraggable dropx ui-draggable ui-droppable"  id="xxxID"  onclick="selectMe(this)" style="position: relative; "     >

 	  <span class="itemdrag actionArrows"><a class="ilid" href="/pim1/list-items/hoist/xxxID">xxxID</a>&nbsp;<a href="/pim1/item/add/xxxID">&harr;</a><a href="#" onClick='actionJax(xxxID,0,"promote")' >&larr;</a><a href="#"  onClick='actionJax(xxxID,0,"demote")'>&rarr;</a><a href="#" onClick='actionJax(xxxID,0,"moveUp")'>&uarr;</a><a href="#" onClick='actionJax(xxxID,0,"moveDown")'>&darr;</a><a href="#" class="archiveLink" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"archiveThisItem")'>a</a><a href="#" class="fastAddLink" onClick='showFastAddDialog(xxxID)'>f</a></span>

<span class="prio_stat_btns">
<span class="js_statprio" onClick='actionJax( xxxID,0,"incPriority")'>+</span><span class="js_statprio" onClick='actionJax( xxxID,0,"decPriority")'>-</span></span><span class="prio"></span><span class="prio_stat_btns"><span class="js_statprio"  onClick='actionJax( xxxID,0,"incStatus")'>+</span><span class="js_statprio"  onClick='actionJax( xxxID,0,"decStatus")'>-</span></span><span class="itemdrag ti"><span class="indent_0 ">
<span class="marker">&bull; </span><a href="/pim1/item/edititem/xxxID" class="Next titlelink">xxxitemtitle</a></span></span>


          <span class="itemdrag notecell">

 	    <a onClick="toggleNoteBody('notebody_xxxID');" class="noteplus">&oplus;</a>
	    <a onClick='detailpop("xxxID")' class="notearr">&rArr;</a> </span>
	   

          </span>
       	  <span class="itemdrag id pfi"></span>
          <div id="notebody_xxxID" class="noteBody"><div class="noteWrapper"> xxxNoteBody </div></div>
     </div>'''


        AlsoRetiredItemTemplate= '''

        <div class="itemsdrag bhdraggable dropx"  id="xxxID"  onclick="selectMe(this)">


 	  <span class="itemdrag actionArrows"><a class="ilid" href="/pim1/list-items/hoist/xxxID">xxxID&nbsp;/::</a>&nbsp;<a href="/pim1/item/add/xxxID">&harr;</a><a href="#" onClick='actionJax(xxxID,0,"promote")' >&larr;</a><a href="#"  onClick='actionJax(xxxID,0,"demote")'>&rarr;</a><a href="#{{ xxxID }}" onClick='actionJax(xxxID,0,"moveUp")'>&uarr;</a><a href="#{{ xxxID }}" onClick='actionJax(xxxID,0,"moveDown")'>&darr;</a><a href="#" class="archiveLink" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"archiveThisItem")'>a</a><a href="#" class="fastAddLink" onClick='showFastAddDialog(xxxID)'>&plus;</a></span>


<!--a href="#" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"delete")'>&otimes;</a -->

<span class="prio_stat_btns"><span class="js_statprio" onClick='actionJax( xxxID,0,"incPriority")'>+</span><span  class="js_statprio"onClick='actionJax( xxxID,0,"decPriority")'>-</span></span>
<span class="prio priority_"></span><span class="prio_stat_btns"><span class="js_statprio" onClick='actionJax( xxxID,0,"incStatus")'>+</span><span class="js_statprio" onClick='actionJax( xxxID,0,"decStatus")'>-</span></span>
<span class="itemdrag ti"><span class="indent_0">
<span class="marker"> </span>
<a href="/pim1/item/edititem/xxxID" class="Next titlelink">xxxitemtitle</a>
</span>

          <span class="xxitemdrag xxnotecell">

 	    [<a onClick="toggleNoteBody('notebody_xxxID');" class="noteplus">&oplus;</a>
	    <a onClick='detailpop("xxxID")' class="notearr">&rArr;</a>] 
          </span>
	   

    </div>

          <div id="notebody_xxxID" class="noteBody">
            <div class="noteWrapper">xxxNoteBody</div>
         </div>       

</span>


</div>

        '''

        newItemTemplate= '''
 <div class="itemsdrag bhdraggable dropx"  id="xxxID"  onclick="selectMe(this)">

  
    <span class="itemDragWidgetBlock">

 	  <span class="itemdrag actionArrows"><a class="ilid" href="/pim1/list-items/hoist/xxxID">xxxID&nbsp;/::</a>&nbsp;<a href="/pim1/item/add/xxxID">&harr;</a><a href="#" onClick='actionJax(xxxID,0,"promote")' >&larr;</a><a href="#"  onClick='actionJax(xxxID,0,"demote")'>&rarr;</a><a href="#xxxID" onClick='actionJax(xxxID,0,"moveUp")'>&uarr;</a><a href="#xxxID" onClick='actionJax(xxxID,0,"moveDown")'>&darr;</a><a href="#" class="archiveLink" onClick='deleteMeFromDOM(xxxID);actionJax(xxxID,0,"archiveThisItem")'>a</a><a href="#" class="fastAddLink" onClick='showFastAddDialog(xxxID)'>&plus;</a></span>


          <span class="prio_stat_btns"><span class="js_statprio" onClick='actionJax( xxxID,0,"incPriority")'>+</span><span  class="js_statprio" onClick='actionJax( xxxID,0,"decPriority")'>-</span></span>
	  <span class="prio priority_"></span><span class="prio_stat_btns"><span class="js_statprio" onClick='actionJax( xxxID,0,"incStatus")'>+</span><span class="js_statprio" onClick='actionJax( xxxID,0,"decStatus")'>-</span></span></span>

<span class="itemDragContentBlock">
<span class="itemdrag ti"><a href="/pim1/item/edititem/xxxID" class="titlelink"><span class="xxxindent"><span class="marker">&bull;</span><span class="titletext">xxxitemtitle</span></a></span>

<span class="noteExpandWidget">
	     
	       [<a onClick="toggleNoteBody('notebody_xxxID');" class="noteplus">&oplus;</a>&nbsp;<a onClick='detailpop("xxxID")' class="notearr">&rArr;</a>] 
	       </span>

    </span>
<div>
          <div id="notebody_xxxID" class="noteBody">
            <div class="noteWrapper">xxxNoteBody</div>
         </div>       
</div>
 </div>      
<div class="itemDivider"> </div>

 

        '''

