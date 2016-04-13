//google.charts.load('current', {packages: ['corechart', 'line']});
//google.charts.setOnLoadCallback(drawBackgroundColor);

function drawBackgroundColor(RPiName, RPiDataType, dataForLineGraph) {
    var replacement = {'FOREGROUND': 'Foreground Size', 'FACE_COUNT_DTL': 'Face Count', 'FACE_COUN_UNIQ_DTL': 'Unique Face Count'};

    try {
        data = new google.visualization.DataTable();
    } catch(e) {
        return;
    }
    
    data.addColumn('datetime', 'TimeStamp');
    data.addColumn('number', 'Data');

    data.addRows(dataForLineGraph);

    var options = {
        height: 125,
        title: 'Raspberry Pi - ' + RPiName + ' Camera: ' + replacement[RPiDataType],
        vAxis: {
            gridlines: {
                color: 'none',
                count: 2
            }
        },
        hAxis: {
            gridlines: {
                color: 'none'
            }
        },
        crosshair: { 
            trigger: 'both',
            color: 'green',
            selected: {
                color: 'red'
            }
        },
        enableInteractivity: true,
        explorer: {
            axis: 'horizontal',
            actions: ['dragToZoom', 'rightClickToReset'],
            maxZoomIn: .00001
        },
        //backgroundColor: '#e3e3e3',
        backgroundColor: 'none',
        legend: {
            position: 'none'
        }
    };

    // Creating and appending div
    var clickedDivID = '';
    divID = RPiName + '_' + RPiDataType;
    var myDiv = document.createElement("div");
    var myBR = document.createElement("br");
    myDiv.id = divID;
    myDiv.onclick = function () {
        clickedDivID = myDiv.id;
    };
    document.getElementById("chart_div").appendChild(myDiv);
    document.getElementById("chart_div").appendChild(myBR); 

    var chart = new google.visualization.ColumnChart(document.getElementById(divID));
    chart.draw(data, options);
    google.visualization.events.addListener(chart, 'select', selectHandler);

    // Start Video play from start of day
    // Storing values
    document.getElementById("RPiName").innerHTML = RPiName;
    playNextVideo();

    function selectHandler() {
        var l = chart.getSelection();
        var selectedTimestamp = data.getValue(l[0].row, 0);
        var selectedTimestamp_N = Number(selectedTimestamp)/1000;
        //console.log(selectedTimestamp);
        //console.log(selectedTimestamp_N);
        //console.log("Inside google selector: " + RPiName);
        playSelectedVideo(RPiName, selectedTimestamp_N);
        // Generate S3 URL
        // Play video from the point in time
    }

}



