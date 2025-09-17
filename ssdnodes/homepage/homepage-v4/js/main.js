var X = 0, Y = 0;
var WinW = 0, WinH = 0;

var getWinSize = function()
{
    WinW = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    WinH = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
};
getWinSize();

function getNodePos(node)
{
    var top = left = 0;
    while (node) {  	
       if (node.tagName) {
           top = top + node.offsetTop;
           left = left + node.offsetLeft;   	
           node = node.offsetParent;
       } else {
           node = node.parentNode;
       }
    } 
    return [top, left];
}


function getNodePosInView(el)
{
    var viewportOffset = el.getBoundingClientRect();
    // these are relative to the viewport
    var top = viewportOffset.top;
    var left = viewportOffset.left;
    return [left, top];
}

function getNodeCenterInView(el)
{
    var Pos = getNodePosInView(el);
    Pos[0] += el.offsetWidth / 2;
    Pos[1] += el.offsetHeight / 2;
    return Pos;
}

// This is a NodeList.
var MsgBoard = document.querySelectorAll("section.HomeSection > h1.SecTitle");

document.onmousemove = function(e){
    X = e.clientX;
    Y = e.clientY;
    for(var i = 0; i < MsgBoard.length; i++)
    {
        // MsgBoard[i].innerHTML = getNodeCenterInView(MsgBoard[i]);
        var Center = getNodeCenterInView(MsgBoard[i]);
        MsgBoard[i].style.transform = "perspective(500px) rotateX(" +
            (-45 * (Y - Center[1])/WinH).toString() + "deg)";
    }
};
window.onresize = getWinSize;
