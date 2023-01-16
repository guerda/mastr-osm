MaStR OSM
=========
This project aims to compare officially registered photovoltaic generators and how they are mapped in OpenStreetMap.
The goal is to map more photovoltaic generators in OpenStreetMap. Reports which should be updated frequently show the progress per zip code.

Furthermore, commercial generators contain a more detailed location, which helps to add these objects to OpenStreetMap.

Instructions
------------
Obtain a MaStR API key.

Check out this repository and install `pipenv`.

    git checkout https://github.com/guerda/mastr-osm.git
    pip install pipenv
    pipenv install

Copy the `env.default` to `env` and change `API_KEY` and `MASTR_NR`

Then run the report generator
    source env
    pipenv run python mastrosm.py

This will generate _all_ reports for a subset zip codes.


MaStR documentation
-------------------
* https://www.marktstammdatenregister.de/MaStRHilfe/subpages/webdienst.html
* https://www.marktstammdatenregister.de/MaStRHilfe/files/webdienst/2019-01_31%20Dokumentation%20MaStR%20Webdienste%20V1.2.0.pdf
* https://www.marktstammdatenregister.de/MaStRAPI/wsdl/mastr.wsdl


Report
------
The current report including history is available at [https://guerda.github.io/mastr-osm/](https://guerda.github.io/mastr-osm/).

* Count of OSM mapped solar generators
* count of MaStR registered solars generators
* missing commercial solar generators
* % of commercial generators
* registered capacity
* mapped capacity in OSM

Sources and copyright
---------------------
* Registration of photovoltaic generators - [Marktstammdatenregister](https://www.marktstammdatenregister.de/MaStR/), [Datenlizenz Deutschland – Namensnennung – Version 2.0](https://www.govdata.de/dl-de/by-2-0)
* Location of photovoltaic generators in OpenStreetMap - &copy; [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
