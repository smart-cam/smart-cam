
function queryDynamoDB(rangeStr) {
	var fullData = {'FrontDoor': {'FOREGROUND': [], 'FACE_COUNT_DTL': [], 'FACE_COUN_UNIQ_DTL': []}};
	var dataLength = 10000;			// Number of records to fetch from DynamoDB
	
	var rangeStrSplit = rangeStr.split(' - ');
	var startTimestamp = Date.parse(rangeStrSplit[0]) / 1000;	// divide by 1000 to get seconds
	//var startTimestamp = 0;
	var endTimestamp = Date.parse(rangeStrSplit[1]) / 1000; 
	//var endTimestamp = 91462071610;
	endTimestamp += 10; 
	//console.log(startTimestamp);
	//console.log(endTimestamp);
	// Storing startTimestamp for default video play
	document.getElementById("currentVideoTimestamp").innerHTML = startTimestamp-1;  // minus 1 so that playNextVideo calls Dynamo appropriately

	// Running for every RPiName and Processed data type for this one customer
	for (RPiName in fullData) {
		for (RPiDataType in fullData[RPiName]) {
			
			getDataFromDynamoDB(RPiName, RPiDataType, startTimestamp, endTimestamp, table);

			function getDataFromDynamoDB(RPiName, RPiDataType, start, end, table, fullData) {
				var params = {
					'ExpressionAttributeValues' : {
						':RN': {'S': RPiName},
						':ST': {'N': start.toString()},
						':ET': {'N': end.toString()}
					},
					'ExpressionAttributeNames': {
						'#FIELD': RPiDataType,
					},
					'KeyConditionExpression': 'RASP_NAME = :RN AND START_TIME BETWEEN :ST AND :ET',
					//'Limit': 10,
					'ProjectionExpression': 'RASP_NAME, START_TIME, #FIELD',
				};

				table.query(params, function(err, data) {
					console.log(err);
					//console.log(data.Items);
					//console.log(data.LastEvaluatedKey);
					var l = concatData(data.Items, RPiName, RPiDataType);
					if (data.LastEvaluatedKey && l == true) {
						getDataFromDynamoDB(RPiName, RPiDataType, data.LastEvaluatedKey.START_TIME.N, end, table)
						//console.log(data.LastEvaluatedKey.START_TIME.N);
						//console.log(data.LastEvaluatedKey.RASP_NAME.S);
					} else {
						done(RPiName, RPiDataType);
					}
				});
			}
		}
	}

	function concatData(data, RPiName, RPiDataType) {
		//console.log(RPiDataType);
		if (fullData[RPiName][RPiDataType].length > 0) {
			data.shift();	// To remove data duplicate due to LastEvaluatedKey
		}
		
		fullData[RPiName][RPiDataType] = fullData[RPiName][RPiDataType].concat(data);

		if (fullData[RPiName][RPiDataType].length < dataLength) {
			return true;
		} else {
			return false;
		}
	}

	function done(RPiName, RPiDataType) {
		
		for (RPiName in fullData) {
			for (RPiDataType in fullData[RPiName]) {
				//console.log(RPiName, RPiDataType);
				data = fullData[RPiName][RPiDataType];
				var dataForLineGraph = [];			// Array for Google charts
				for (i=0; i < data.length; i++) {
					//console.log(data[i].START_TIME.N);
					var videoTimestamp = data[i].START_TIME.N * 1000;
					videoTimestamp = parseInt(videoTimestamp) + 1;
					//console.log(videoTimestamp);
					dataArray = data[i][RPiDataType].M.data.L;
					//dataArray = data[i][RPiDataType].L;

					for (j=0; j < dataArray.length; j++) {
						var ts = new Date(videoTimestamp);
						var di = Number(dataArray[j].S);
						dataForLineGraph.push([ts, di]);
						videoTimestamp += 1000;
					}
					// Adding NULL for break in graph
					videoTimestamp += 500;
					ts = new Date(videoTimestamp);
					dataForLineGraph.push([ts, null]);
				}
				//console.log(dataForLineGraph);
				if (dataForLineGraph.length > 0) {
					drawBackgroundColor(RPiName, RPiDataType, dataForLineGraph);
				}
			}
		}
	}
}


