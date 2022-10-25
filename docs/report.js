function zipCodeSelect(event) {
  var zipCode = event.target.value;
  var city = event.target.selectedOptions[0].innerHTML;

  var headline = document.getElementById("cityHeadline");
  headline.innerHTML = city;

  load_zip_code_data(zipCode);
}

function load_available_zip_codes() {
  fetch("data/available-zip-codes.json")
    .then((response) => response.json())
    .then((availableZipCodes) => {
      var zipCodeSelector = document.getElementById("zipCodeSelector");
      for (i in availableZipCodes) {
        zipCode = availableZipCodes[i];
        var zipOption = document.createElement("option");
        zipOption.value = zipCode.zipCode;
        zipOption.innerHTML = zipCode.city + " (" + zipCode.zipCode + ")";
        zipCodeSelector.appendChild(zipOption);
      }
    });
}

function load_zip_code_data(zip_code) {
  fetch("data/" + zip_code + ".json")
    .then((response) => response.json())
    .then((progressData) => {
      // Overall progress plot
      var progressPlotElement = document.getElementById("progress-plot");
      var data = [
        {
          x: progressData["dates"],
          y: progressData["solarGenerators"],
          name: "Registered in MaStR",
          fill: "tozeroy",
        },
        {
          x: progressData["dates"],
          y: progressData["solarGeneratorsMapped"],
          name: "Mapped in OSM",
          fill: "tozeroy",
        },
      ]
      var config = { responsive: true }
      var layout = {
        title: "Registered and mapped solar generators by time",
      };
      var plot = Plotly.newPlot(
        progressPlotElement,
        data,
        layout,
        config
      );

      // Progress bars
      progressAll = document.getElementById("progress-all");
      console.log(
        progressData["solarGeneratorsMapped"][
          progressData["solarGeneratorsMapped"].length - 1
        ]
      );
      console.log(
        progressData["solarGenerators"][
          progressData["solarGenerators"].length - 1
        ]
      );

      progress =
        progressData["solarGeneratorsMapped"][
          progressData["solarGeneratorsMapped"].length - 1
        ] /
        progressData["solarGenerators"][
          progressData["solarGenerators"].length - 1
        ];
      progress = (progress * 100).toFixed(1) + "%";
      progressAll.childNodes[1].style.width = progress;
      progressAll.childNodes[1].innerHTML = progress;
      // TODO set aria-valuenow

      progressCommercial = document.getElementById("progress-commercial");
      progressPrivate = document.getElementById("progress-private");
    });
}

load_available_zip_codes();
load_zip_code_data(40667);

document
  .getElementById("zipCodeSelector")
  .addEventListener("input", function (event) {
    zipCodeSelect(event);
  });
