google.charts.load('current', {packages: ['corechart', 'line']});
//google.charts.setOnLoadCallback(drawBackgroundColor);

function drawBackgroundColor(RPiName, dataForLineGraph) {
      var data = new google.visualization.DataTable();
      data.addColumn('datetime', 'TimeStamp');
      data.addColumn('number', 'Foreground Size');

      data.addRows(dataForLineGraph);

      var options = {
        //curveType: 'function',
        title: 'Raspberry Pi - ' + RPiName + ' Camera: Foreground size',
        vAxis: {
          gridlines: {
            color: 'none'
          },
            logScale: true,
            viewWindowMode: 'pretty'
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
        backgroundColor: '#e3e3e3',
        legend: {
          position: 'none'
        }
      };

      // Creating and appending div
      var myDiv = document.createElement("div");
      var myBR = document.createElement("br");
      myDiv.id = RPiName;
      document.getElementById("chart_div").appendChild(myDiv);
      document.getElementById("chart_div").appendChild(myBR); 

      var chart = new google.visualization.LineChart(document.getElementById(RPiName));
      chart.draw(data, options);
      google.visualization.events.addListener(chart, 'select', selectHandler);

      function selectHandler() {
        var l = chart.getSelection();
        console.log(data.getValue(l[0].row, 0));
        // Generate S3 URL
        // Play video from the point in time
      }
    }

