
function playSelectedVideo(RPiName, selectedTimestamp) {
  // This function gets current video timestamp from the selected data item in the UI
  var params = {
    'ExpressionAttributeValues' : {
      ':RN': {'S': RPiName},
      ':ST': {'N': selectedTimestamp.toString()}
    },
    'KeyConditionExpression': 'RASP_NAME = :RN AND START_TIME <= :ST',
    'ScanIndexForward': false,    // To get descending order
    'Limit': 1,
    'ProjectionExpression': 'START_TIME, S3_BUCKET, S3_KEY'
  };
  table.query(params, function(err, data) {
    console.log(err);
    currentVideoTimestamp = data.Items[0].START_TIME.N;
    //console.log(currentVideoTimestamp);
    var forwardVideoSec = parseInt(selectedTimestamp - currentVideoTimestamp);
    //console.log(forwardVideoSec);
    //console.log(data.Items[0].S3_KEY.S);
    // Storing values
    document.getElementById("RPiName").innerHTML = RPiName;
    document.getElementById("currentVideoTimestamp").innerHTML = currentVideoTimestamp;
    // Playing video
    var params = {Bucket: data.Items[0].S3_BUCKET.S, Key: data.Items[0].S3_KEY.S};
    var url = s3.getSignedUrl('getObject', params);
    //console.log(url);
    document.getElementById("myV").src = url;
    document.getElementById("myV").currentTime = forwardVideoSec;
    document.getElementById("myV").play();
  });
}

function playNextVideo() {
	// function to get next video filename
	var params = {
		'ExpressionAttributeValues' : {
			':RN': {'S': document.getElementById("RPiName").innerHTML},
			':ST': {'N': document.getElementById("currentVideoTimestamp").innerHTML}
		},
		'KeyConditionExpression': 'RASP_NAME = :RN AND START_TIME > :ST',
		'Limit': 1,
		'ProjectionExpression': 'START_TIME, S3_BUCKET, S3_KEY'
	};
	table.query(params, function(err, data) {
		console.log(err);
		currentVideoTimestamp = data.Items[0].START_TIME.N;
		// Storing data
		document.getElementById("RPiName").innerHTML = RPiName;
    	document.getElementById("currentVideoTimestamp").innerHTML = currentVideoTimestamp;
    	// Playing video
	    var params = {Bucket: data.Items[0].S3_BUCKET.S, Key: data.Items[0].S3_KEY.S};
	    var url = s3.getSignedUrl('getObject', params);
	    document.getElementById("myV").src = url;
	    document.getElementById("myV").play();
	});
}

function test() {

	console.log("Video ended" + document.getElementById("RPiName").innerHTML + document.getElementById("currentVideoTimestamp").innerHTML);
}