
//document.getElementById("myV").src = "video1.mp4";

document.getElementById("myV").currentTime = 30;
//document.getElementById("myV").play();

RPiNameList = ['Garage', 'Kitchen'];

function queryDynamoDB(rangeStr) {
	var rangeStrSplit = rangeStr.split(' - ');
	var startTimestamp = Date.parse(rangeStrSplit[0]) / 1000;	// divide by 1000 to get seconds
	var endTimestamp = Date.parse(rangeStrSplit[1]) / 1000;
	endTimestamp += 10; 
	console.log(startTimestamp);
	console.log(endTimestamp);

	// Setting AWS Dynamo Credentials
	AWS.config.update({accessKeyId: 'AKIAIHWPHJLJ5PYV3VRQ', secretAccessKey: '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'});
	AWS.config.region = 'us-west-2';

	var table = new AWS.DynamoDB({params: {TableName: 'RPiForeground'}});

	// Running for every RPiName for this one customer
	for (k=0; k<RPiNameList.length; k++) {

		var params = {
		'ExpressionAttributeValues' : {
			':NA': {'S': RPiNameList[k]},
			':ST': {'N': startTimestamp.toString()},
			':ET': {'N': endTimestamp.toString()}
		},
		'KeyConditionExpression': 'RPiName = :NA AND StartTime BETWEEN :ST AND :ET',
		'ProjectionExpression': 'RPiName, StartTime, VideoData'
		};
		table.query(params, function(err, data) {
			console.log(err);
		    [RPiName, dataForLineGraph] = processDynamoDBData(data.Items);
		    drawBackgroundColor(RPiName, dataForLineGraph);
		});
	}
}

function processDynamoDBData(data) {
	var RPiName = '';
	var dataForLineGraph = [];
	// Looping through all rows returned by DynamoDB
	for (i=0; i<data.length; i++ ) {
		RPiName = data[i].RPiName.S;
		videoData = data[i].VideoData;
		console.log(videoData);
		videoTimestamp = data[i].StartTime.N;
		videoTimestamp = parseInt(videoTimestamp * 1000);
		// Looping through each item of VideoData of each row
		for (j=0; j<videoData.L.length; j++) {
			ts = new Date(videoTimestamp);		// Time of each second
			di = Number(videoData.L[j].N);				// Data item i.e. each foreground size for each second
			dataForLineGraph.push([ts, di]);
			videoTimestamp += 1000;
		}
		// Adding NULL for break in graph
		videoTimestamp += 500;
		ts = new Date(videoTimestamp);
		dataForLineGraph.push([ts, null]);

	}
	return [RPiName, dataForLineGraph];
}