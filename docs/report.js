const userLocale = navigator.languages && navigator.languages.length
  ? navigator.languages[0]
  : navigator.language;


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
      // Set last update date
      
      var lastUpdateElement = document.getElementById("last-update");
      var lastUpdate = progressData["dates"][progressData["dates"].length-1];
      lastUpdateElement.innerHTML = lastUpdate.toLocaleString(userLocale);

      // Overall progress plot
      var progressPlotElement = document.getElementById("progress-plot");
      var data = [
        {
          x: progressData["dates"],
          y: progressData["solarGenerators"],
          name: "Registered in MaStR",
          fill: "tonexty",
          marker: { 
            color: "#FFC20A"
          }
        },
        {
          x: progressData["dates"],
          y: progressData["solarGeneratorsMapped"],
          name: "Mapped in OSM",
          fill: "tozeroy",
          marker: { 
            color: "#0C7BDC"
          }
        },
      ]
      var config = { responsive: true }
      var layout = {
        title: "Registered and mapped solar generators by time",
        showlegend: true,
        legend: {
          x: 0.01,
          y: 0.9
        }
      };
      var plot = Plotly.newPlot(
        progressPlotElement,
        data,
        layout,
        config
      );

      // Progress bars
      progressAll = document.getElementById("progress-all");
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

      // List missing commercial solar generators
      var missingGeneratorsElement = document.getElementById("missing-commercial-generators");
      missingGeneratorsElement.replaceChildren();
      var missingGenerators = progressData["missingCommercialGenerators"]
      for (i in missingGenerators) {
        var missingGenerator = missingGenerators[i];
        // MaStR Link
        var mastrReference = missingGenerator["mastrReference"];
        var mastrLink = document.createElement("a");
        mastrLink.target = "_blank";
        mastrLink.innerHTML = mastrReference;
        if (missingGenerator["mastrDetailUrl"]) {
          mastrLink.href = missingGenerator["mastrDetailUrl"];
        }
        
        // OSM Edit link
        var osmEditLink = document.createElement("a");
        var lat = missingGenerator["lat"];
        var lon = missingGenerator["lon"];
        osmEditLink.target = "_blank";
        if (lat != 0 && lon != 0) {
          osmEditLink.href = "https://www.openstreetmap.org/edit#map=19/"+lat+"/"+lon;
        }
        osmEditLink.classList = "btn btn-primary"
        osmEditLink.innerHTML = "Edit on OSM";
        
        var generatorListItem = document.createElement("li");
        generatorListItem.className = "fixed";
        generatorListItem.appendChild(mastrLink);
        generatorListItem.append(" ");
        generatorListItem.appendChild(osmEditLink);
        missingGeneratorsElement.appendChild(generatorListItem);
      }
    });
}

load_available_zip_codes();
load_zip_code_data(40667);

document
  .getElementById("zipCodeSelector")
  .addEventListener("input", function (event) {
    zipCodeSelect(event);
  });

