$(function(){

	$('.origin input').on('input', function(){

		ul = $(this).parent().find('ul')[0]
		
		if ($(this).val() !== ''){
			$(ul).css('display','block')
			search($(this).val(), ul , 1)

		}else{
			$(ul).html('')
			$(ul).css('display','none')
		}
	})

	$('.destinations input').on('input', function(){

		ul = $(this).parent().find('ul')[0]
		
		if ($(this).val() !== ''){
			$(ul).css('display','block')
			search($(this).val(), ul , 0 )

		}else{
			$(ul).html('')
			$(ul).css('display','none')
		}
	})
})



var search = function(q, list, first ){

	$.ajax({
	   	url: 'http://partners.api.skyscanner.net/apiservices/xd/autosuggest/v1.0/GB/GBP/en-GB',
	    contentType: "application/json",
	    dataType: 'jsonp',
	    jsonpCallback: 'callback',
	    data: {
	        query:q,
			apikey:'ilw02375360823411197864901011420'
	    },
	    success: function( response ) {
	    	var elements = ''

	    	$.each(response.Places, function(e){
	    		var name = this.PlaceName
	    		var id = this.PlaceId.replace('-sky', '')
	    		elements += '<li role="presentation"><a role="menuitem" tabindex="-1">'+ name + ' (' + id +') </a></li>'	
	    	})

	    	$(list).html(elements)
	    	
	    	$(list).find('li').on('click', function(e){
	    		selected = $(this).find('a')[0].text
	    		$(list).parent().find('input').val(selected)
	    		$(list).css('display', 'none')
	    		
	    		if(first == 1){
	    			dropPin(map,selected,50)
	    		}else{
	    			dropPin(map,selected,$(list).parent().index())
				}

	    	})
	    }
	});
}



var route = function(){
	var data = {}

	origin = $('.origin input[name=origin]').val();
	date = $('.origin input[name=date]').val();
	destinations = []
	
	$.each($('.destinations>ul>li'), function(e){
		destinations.push({
			name: $(this).find('input').val(),
			days: parseInt($(this).find('select').val())
		})
	});

	data =  {
		'origin': origin,
		'date': date,
		'destinations': destinations
	}

	$.ajax({
		type: "POST",
		url: "/get_results",
		data: data,
		success: function(data){
			var list = ''

			$.each(data.Routes, function(e){
				var cost = '<td>' + e.Price + '</td>'
				var stops = ''

				$.each(e.Route, function(a){
					stops += '<td>' + a.Orig + ' -> ' + a.Dest + '</td>'

				})

				list += '<tr>' + stops + cost + '</tr>'

			})

			$('#results table tbody').html(list)

		},
		error: function(data){
			console.log('Error!')
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

