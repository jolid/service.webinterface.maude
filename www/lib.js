 $(document).ready(function() {
	$( "#subscriptionPanel" ).on({
		popupbeforeposition: function() {
			var h = $( window ).height();
			$( "#subscriptionPanel" ).css( "height", h );
			
		}
	});
	$( "#subscriptionPanel" ).off({
		popupbeforeposition: function() {
			$('#subscriptionList').listview("refresh");
		}
	});

 });

function notify(text) {
	
}


$(document).delegate('#tvshows', 'pageshow', function () {

});


$(document).delegate('#movies', 'pageshow', function () {


});
__showid__ = 0;
__subscriptions__ = [];

$(document).delegate('#tvshows', 'pageshow', function () {
	$(".subscriptionListItem").live("click", function(event, ui) {
		showid = this.value
		__showid__ = showid
		text = $(this).text();
		$("#SubscriptionNameInfo").html(text)
		enabled = __subscriptions__[showid][3];
		$("#EnabelSubscriptionCheckbox").attr("checked",enabled==1).checkboxradio("refresh");
		$.getJSON('/query/?method=getSubscriptionInfo&showid=' + showid, function(json) {
			html = ''
			$.each(json, function(index){
				row = json[index]
				html += row + '<br>'		
			});
			$("#SubscriptionProvidersInfo").html(html)	
		});	
	});

	$.getJSON('/query/?method=subscriptions', function(json) {
		html = ''
		$.each(json, function(index){
			row = json[index]
			__subscriptions__[row[1]] = row
			showname = row[2]
			if(row[3] == 0) {
				showname = '<span style="color: gray;">' + showname + '</span>'
			}
			html += '<li class="subscriptionListItem" value="'+row[1]+'" enabled="'+row[3]+'"><a href="#subscriptionPanel" data-rel="popup" data-transition="slide" data-position-to="window">'+showname+'</a></li>';
		}); 
		$('#subscriptionList').html(html);
		$('#subscriptionList').listview("refresh");

	});
	$("#DeleteSubscriptionButton").live("click", function(event, ui) {
		alert(__showid__);
	});
	$("#EnabelSubscriptionCheckbox").live("change", function(event, ui) {
		enabled = __subscriptions__[__showid__][3]
		enabled = Math.abs(1 - enabled)
		__subscriptions__[__showid__][3] = enabled
		$.ajax({
		        type: "GET",
		        url: "/query/?method=toggleShowSubscription&showid=" + __showid__,
		        cache: false,
		        success: function(response) {
				alert(response);
			}
		});
	});

});
$(document).delegate('#subscribeAZ', 'pageshow', function () {

});
$(document).delegate('#subscribeSearch', 'pageshow', function () {
	$("#subscriptionSearch").live("keyup", function(event, ui) {
		var text = $(this).val();
		if(text.length > 2)	{
			var url = '/query/?method=search&type=tvshows&s=' + encodeURIComponent(text);
			$.getJSON(url , function(json) {
				html = ''
				$.each(json, function(index){
					row = json[index]
					if(row[2]==1) {
						checked = 'checked';
					} else {
						checked = ''; 
					}
					html += '<li><input type="checkbox"  value="'+row[1]+'" class="subscriptionItem" '+checked+'/>'+row[0]+'</li>';
				}); 
				$('#subscriptionResults').html(html);
				$('#subscriptionResults').listview("refresh");
				$("#subscriptionResults").show('fast');	
			});
					
		} else {
			$("#subscriptionResults").hide('fast');		
		}
		
	});
	
});

$(document).delegate('#moviesSearch', 'pageshow', function () {
	$("#subscriptionSearchField").live("keyup", function(event, ui) {
		var text = $(this).val();
		if(text.length > 3)	{
			var url = '/query/?method=search&type=movies&s=' + encodeURIComponent(text);
			$.getJSON(url , function(json) {
				html = ''
				$.each(json, function(index){
					row = json[index]
					html += '<li><input type="checkbox"  value="'+row[1]+'" class="movieItem"/>'+row[0]+'</li>';
				}); 
				$('#subscriptionSearchResults').html(html);
				$('#subscriptionSearchResults').listview("refresh");
				$("#subscriptionSearchResults").show('fast');	
			});
					
		} else {
			$("#subscriptionSearchResults").hide('fast');		
		}
		
	});

	/*$(".subscriptionItem").live("change", function(event, ui) {
		
		value = $(this).val();
		data = {"showid" : value};		
		$.ajax({
		        type: "POST",
		        url: "/query/?method=toggleShowSubscription",
		        cache: false,
		        data: data,
		        success: function(response) {
				notify(response);
			}
		});	
	});*/
	
});

$(document).delegate('#log', 'pageshow', function () {
	$.ajax({
		        type: "GET",
		        url: "/query/?method=getLogContent",
		        cache: false,
		        success: function(response) {
				
				$('#logcontent').html('<pre>' + response + '</pre>');
			}
		});


});
