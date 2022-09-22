fetch("data/40667.json")
  .then((response) => response.json())
  .then((progressData) => {
    progressPlotElement = document.getElementById("progress-plot");
    layout = {
      title: "Registered and mapped solar generators by time",
    };
    plot = Plotly.newPlot(
      progressPlotElement,
      [
        {
          x: progressData["dates"],
          y: progressData["solarGenerators"],
          name: "Registered in MaStR",
        },
        {
          x: progressData["dates"],
          y: progressData["solarGeneratorsMapped"],
          name: "Mapped in OSM",
        },
      ],
      layout
    );
  });
