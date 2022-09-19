fetch('data/40667.json')
    .then((response) => response.json())
    .then((progressData) => {         
        progressPlotElement = document.getElementById("progress-plot")
        Plotly.newPlot(progressPlotElement, [
                {
                    x: progressData["dates"], 
                    y: progressData["solarGenerators"]
                }
            ], { 
                margin: {
                    t: 0 
                }
            });
});