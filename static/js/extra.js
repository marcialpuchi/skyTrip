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
	$.scrollTo('#map', {duration: 500,durationMode: 'all'})

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

	$('.best').css('display', 'none')

	if ($('.flex label.static').hasClass('active')){
		static_dates(data)
	}else{
		flex_dates(data)
	}

}


var static_dates = function(data){
	$.ajax({
		type: "POST",
		url: "/get_results",
    	data: JSON.stringify(data),
    	contentType: 'application/json; charset=utf-8',
    	dataType: 'json',
    	async: true,
		success: function(data){

			if (data.Routes == 0){
				alert("No Routes available :(")
				return true;
			}

			var list = ''

			$(function(){
				list = "<th>#</th>"
				var num_of_flights = data.Routes[0].Route.length
				console.log(num_of_flights)
				for (i = 1; i < num_of_flights; i++) { 
    				list += "<th>Flight #" + parseInt(i) + "</th>";
				}
				list += '<th>Return</th> <th>Total Cost</th>'
			})
			$('#results table thead').html(list)



			$.each(data.Routes, function(e){
				var cost = '<td>' + this.Cost + '</td>'
				var stops = ''
				var connect = []

				$.each(this.Route, function(e){
					stops += '<td>' +  this.Leg.Orig + ' &rarr; ' + this.Leg.Dest + '<br/>' + this.Leg.Date + '</td>'

					connect.push({
						trip: this.Leg.Orig + ' &rarr; ' + this.Leg.Dest,
						cost: this.LegPrice,
						airline: this.Carrier
					})

				})

				list += '<tr><td>'+ (e+1) + '</td>' + stops + cost + '</tr>'

				if (e < 3){

					$('#best-' + (e+1) + ' .pricing-rate').html('<sup>£</sup>' + cost)
					$('#best-' + (e+1) + ' .pricing-list ul').html('')

					$.each(connect, function(){
						$('#best-' + (e+1) + ' .pricing-list ul').append('<li><i class="fa fa-plane"></i>' + this.trip + '<span class="pull-right">' + this.cost + '</span></li>')

					})

					$('#best-' + (e+1)).css('display', 'inline-block')
				}

			})

			$('#results table tbody').html(list)
			$('.results').css('display', 'block')

		},
		error: function(data){
			console.log('Error!')
		}
	});
}

var flex_dates = function(data){
	$.ajax({
		type: "POST",
		url: "/get_results_flex",
    	data: JSON.stringify(data),
    	contentType: 'application/json; charset=utf-8',
    	dataType: 'json',
    	async: true,
		success: function(data){

			if (data.Routes == 0){
				alert("No Routes available :(")
				return true;
			}

			var list = ''

			$.each(data.Routes, function(e){
				var cost = '<td>' + this.Cost + '</td>'
				var stops = ''
				var connect = []

				$.each(this.Route, function(e){
					stops += '<td>' +  this.Leg.Orig + ' &rarr; ' + this.Leg.Dest + '<br/>' + this.Leg.Date + '</td>'

					connect.push({
						trip: this.Leg.Orig + ' &rarr; ' + this.Leg.Dest,
						cost: this.LegPrice,
						airline: this.Carrier
					})

				})

				list += '<tr><td>'+ (e+1) + '</td>' + stops + cost + '</tr>'

				if (e < 3){

					$('#best-' + (e+1) + ' .pricing-rate').html('<sup>£</sup>' + cost)
					$('#best-' + (e+1) + ' .pricing-list ul').html('')

					$.each(connect, function(){
						$('#best-' + (e+1) + ' .pricing-list ul').append('<li><i class="fa fa-plane"></i>' + this.trip + '<span class="pull-right">' + this.cost + '</span></li>')

					})

					$('#best-' + (e+1)).css('display', 'inline-block')
				}

			})

			$('#results table tbody').html(list)
			$('.results').css('display', 'block')

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

