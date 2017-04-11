var keyword = null;
var markers = [];
var map = null;
var xmlhttp = new XMLHttpRequest();

var bludMarker = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png";
var redMarker = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
var yellowMarker = "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png";

var newTweets = 0;

/*
 * Modified based off of code found at: https://github.com/keyu-lai/TwitterMap2
 */

function attachMessage(marker, meg) {
	var infowindow = new google.maps.InfoWindow({
		content: meg
	});

	marker.addListener('click', function() {
		infowindow.open(map, marker);
	});
}

/*
 * Listen to the http request 
 */

xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
		if(JSON.parse(xmlhttp.responseText)['tweets']){
			// clear the existing markers
		while (markers.length != 0)
			markers.pop().setMap(null);
		// add new markers
		var tweets = JSON.parse(xmlhttp.responseText)['tweets'];
		for (var i = 0; i < tweets.length; ++i) {
			var tweet = tweets[i];
			var loc = new google.maps.LatLng(parseInt(tweet["coordinates"][1]), parseInt(tweet["coordinates"][0]));
			var icon = bludMarker;

			if (parseFloat(tweet['sen']) > 0.0)
				icon = redMarker;
			else if (parseFloat(tweet['sen']) < 0.0)
				icon = yellowMarker;
			else
				icon = bludMarker;

			var text = tweet['text'];
			var marker = new google.maps.Marker({
				icon: icon,
				position: loc,
				map: map,
				title: text
			});
			marker.setMap(map);
			markers.push(marker);
			attachMessage(marker, text);
			}
		} else {
			var num_new_tweets = JSON.parse(xmlhttp.responseText)['new_tweets'];
			newTweets = newTweets + num_new_tweets;
			document.getElementById("newTweets").innerHTML = "New Tweets: " + newTweets;
		}
	}
};

function initMap() {

	/* 
	 * Initilize the Google Map
	 */
	map = new google.maps.Map(document.getElementById('map'), {
		center: {lat: 0, lng: 0},
		zoom: 3,
		styles: [{
			featureType: 'poi',
			stylers: [{ visibility: 'off' }]  // Turn off points of interest.
		}, {
			featureType: 'transit.station',
			stylers: [{ visibility: 'off' }]  // Turn off bus stations, train stations, etc.
		}],
		disableDoubleClickZoom: true
	});
}

/* 
 * Change the keyword of dropdown
 */
$(".dropdown").on("click", "li a", function() {
	keyword = $(this).text();
	$(".dropdown-toggle").html(keyword + ' <span class="caret"></span>');
}); 

/*
 * When clicking the sumbit button, send a POST request
 */
$("button").on("click", function() {
	newTweets = 0;
	document.getElementById("newTweets").innerHTML = "New Tweets: " + newTweets;
	sendHttp();
});

function sendHttp() {

	/*
	 * Remind the user to pick a location and a keyword
	 */
	if (keyword == null) {
		alert("Please pick a keyword");
		return;
	}

	/*
	 * HTTP request sent
	 */
	xmlhttp.open("POST", "/global?kw=" + keyword, true);
	xmlhttp.send();
}



