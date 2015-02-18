$(function(){
	$('.destinations input').on('input', function(){

		ul = $(this).parent().find('ul')[0]
		
		if ($(this).val() !== ''){
			$(ul).css('display','block')
			search($(this).val(), ul)

		}else{
			$(ul).html('')
			$(ul).css('display','none')
		}
	})

})



var search = function(q, list){

	$.ajax({
	   	url: 'http://partners.api.skyscanner.net/apiservices/xd/autosuggest/v1.0/GB/GBP/en-GB',
	    contentType: "application/json",
	    dataType: 'jsonp',
	    jsonpCallback: 'callback',
	    data: {
	        query:q,
			apikey:''
	    },
	    success: function( response ) {
	    	var elements = ''

	    	$.each(response.Places, function(e){
	    		var name = this.PlaceName
	    		var id = this.PlaceId.replace('-sky', '')
	    		elements += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#">'+ name + ' (' + id +') </a></li>'	
	    	})

	    	$(list).html(elements)
	    	
	    	$(list).find('li').on('click', function(){
	    		selected = $(this).find('a')[0].text
	    		$(list).parent().find('input').val(selected)
	    		$(list).css('display', 'none')
	    	})
	    }
	});
}




var textChange = function(elements, target){

    $(elements).on("input", function(){
        addNewLink($(this), target);
    });
}

var addNewLink = function(element, target){
    
    var html = '<li><input type="text" class="form-control" placeholder="Username" aria-describedby="basic-addon1" use=false></li>'
    
    console.log('add link')
    console.log(element.val())
    console.log(element.attr("use"))


    if(element.val() !== "" && element.attr("use") !== 'true'){

        $(target).append(html);
        textChange($(target + ' li'))
        element.attr("use", true)

        console.log(element.attr("use"))
     }

     // else if ($(element).val() == ""){
    //     var num = $(target + 'li').length-1
    //     $(target + "li > div:nth-child(" + num + ")").remove();
    //     $(target + "li > div:nth-child(" + num-1 + ") input").focus();
        
    // }
}

