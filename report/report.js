progressData = fetch('data/40667.json').then((response) => response.json()).then((json) => console.log(json));
progressPlotElement = document.getElementById("progress-plot")
Plotly.newPlot(progressPlotElement, [{x: progressData['dates'], y: progressData['solarGenerators']}])