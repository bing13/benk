function detailpop(id)
{
  window.open("/item/detail/"+id)
}

function toggleLI(Bx)
      {
        if (document.getElementById(Bx).style.display != 'none') {
          document.getElementById(Bx).style.display = 'none';
        } else {
          document.getElementById(Bx).style.display = 'inline';
        }
      }

function hideClass(hx)
{
   for(var i=0;i<document.getElementsByTagName('*').length;i++){
     if(document.getElementsByTagName('*')[i].className == hx){
        document.getElementsByTagName('*')[i].style.display = 'none';
     }
   }
}
