import overpy

api = overpy.Overpass()

r = api.query("""(
  rel[postal_code="40667"];
  map_to_area;
  node["power"="generator"]["generator:method"="photovoltaic"](area);
  way["power"="generator"]["generator:method"="photovoltaic"](area);
  relation["power"="generator"]["generator:method"="photovoltaic"](area);
);
(._;>;);
out;""")

print(r)

for w in r.ways:
    print(w)


for n in r.nodes:
    print(n)