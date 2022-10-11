fetch("data/40667.json")
  .then((response) => response.json())
  .then((progressData) => {
    // Overall progress plot
    progressPlotElement = document.getElementById("progress-plot");
    layout = {
      title: "Registered and mapped solar generators by time"
    };
    plot = Plotly.newPlot(
      progressPlotElement,
      [
        {
          x: progressData["dates"],
          y: progressData["solarGenerators"],
          name: "Registered in MaStR",
          fill: "tozeroy"
        },
        {
          x: progressData["dates"],
          y: progressData["solarGeneratorsMapped"],
          name: "Mapped in OSM",
          fill: "tozeroy"
        },
        
      ],
      
      layout
    );
    
    // Progress bars
    progressAll = document.getElementById("progress-all");
    console.log(progressData["solarGeneratorsMapped"][progressData["solarGeneratorsMapped"].length-1])
    console.log(progressData["solarGenerators"][progressData["solarGenerators"].length-1])

    progress = progressData["solarGeneratorsMapped"][progressData["solarGeneratorsMapped"].length-1] /  progressData["solarGenerators"][progressData["solarGenerators"].length-1]
    progress = (progress*100).toFixed(1) + "%"
    progressAll.childNodes[1].style.width = progress
    progressAll.childNodes[1].innerHTML = progress
    // TODO set aria-valuenow

    progressCommercial = document.getElementById("progress-commercial");
    progressPrivate = document.getElementById("progress-private");
  });
