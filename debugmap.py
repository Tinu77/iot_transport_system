import folium

m = folium.Map(location=[7.16, 3.36], zoom_start=13)

folium.Marker(
    [7.16, 3.36],
    popup="TEST BUS"
).add_to(m)

m.save("debugmap.html")
