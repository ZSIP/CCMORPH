const config = {
    paths: {
        input: {
            geojson: "data/web/geojson",
            clip: "data/web/geotiff",
            names: "data/web/names/names.json",
            shaper: "data/web/results/finder.csv",
        },
        output: {
            manual: "data/web/results/manual.csv"
        }
    },
    csv: {
        shaper: {
            sep: ","
        },
        manual: {
            sep: ","
        }
    },
    map: {
        options: {
            center: [54.35879939795, 19.32297962655],
            zoom: 12
        },
        base: {
            url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        }  
    },
    elevation: {
        options: {
            theme: "lightblue-theme",
            collapsed: false,
            autohide: false,
            autofitBounds: true,
            position: "bottomleft",
            detached: true,
            summary: "inline",
            imperial: false,
            slope: false,
            speed: false,
            acceleration: false,
            time: false,
            legend: true,
            followMarker: false,
            almostOver: false,
            distanceMarkers: true,
            downloadLink: false,
        }
    },
    image: {
        options: {
            "crossOrigin": false,
            "interactive": true,
            "opacity": 0,
            "zindex": 1
        }
    },
    draw: {
        options: {
            position: "topleft",
            draw: {
                polygon: false,
                polyline: false,
                rectangle: false,
                circlemarker: {
                    repeatMode: true
                },
                marker: false,
                circle: false
            },
            edit: {},
        },
        maxDistance: 3 // buffer around profile polygon
    }
}

const state = {

};
