

var imgarr=$('img')
for (var i = 0; i < imgarr.length; i++) {
    $(".img").eq(i).on('mouseover', function(){
        $(this).animate({
         width: "30%",
         opacity: 0.4,
         fontSize: "1.5em",
       }, 500 )})
       $(".img").eq(i).on('mouseout', function(){
           $(this).animate({
            width: "20%",
            opacity: 1,
            fontSize: "1em",
          }, 500 )
     })
}
