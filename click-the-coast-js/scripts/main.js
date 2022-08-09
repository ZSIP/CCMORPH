const startToInfo = function () {
    $('#rightPanel').addClass('d-none');
    $('#rightPanel').addClass('col-sm-1');
    $('#rightPanel').removeClass('col-sm-6');
    $('#infoPanel').removeClass('d-none');
    $('input').attr('readonly', 'true');

    $('.form-check-input').prop( "disabled", true );
    $('#seriesSelect').prop( "disabled", true);
}

const infoToTest = function () {
    $('#leftPanel').addClass('d-none');
    $('#infoPanel').addClass('d-none');
    $('#rightPanel').addClass('col-sm-1');
    $('#rightPanel').removeClass('col-sm-6');
    $('#infoPanel').addClass('d-none');
    $('#mainPanel').removeClass('d-none');

    initMap();
}

const testToTest = function () {
    const next = state.data.tests.shift();
    if (next) {
        showProfile(next);
    } else {
        testToEnd();
    }
}

const testToEnd = function () {
    $('#leftPanel').removeClass('d-none');
    $('#mainPanel').addClass('d-none');
    $('#rightPanel').removeClass('col-sm-1');
    $('#rightPanel').addClass('col-sm-6');

    $('.login-title').text('Dziękujemy');
    $('#next').addClass('d-none');
}

const setMapTitle = function (name) {
    $('#name').html(name);
}

const prepareData = function (email, id) {
    const retVal = {
        email,
        id,
        tests: []
    };
    // retVal.tests = getProfileNames();
    getProfileNames();
    return retVal;
}

const isEmail = function (email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

const isIdText = function (idText) {
    return idText && idText.length;
}

const correctInput = function (element, alertText) {
    const alert = `<div class="alert alert-danger" role="alert">\
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">\
            <span aria-hidden="true">&times;</span>\
        </button>\
        ${alertText}\
    </div>`;

    element.parent().prepend($(alert));
    element.focus();
}

const resetMap = function () {
    console.log('reset map');
    if (state.imageOverlay) {
        state.controlElevation.clear();
        // state.imageOverlay.removeFrom(state.map);
        state.imageOverlay = false;
        state.drawnItems.clearLayers();
    }
}

const initMap = function () {
    state.map = L.map('map', config.map.options);
    L.control.scale().addTo(state.map);

    L.tileLayer(config.map.base.url, {
        attribution: config.map.base.attribution,
    }).addTo(state.map);

    state.controlElevation = L.control.elevation(config.elevation.options);
    state.controlElevation.addTo(state.map);

    state.drawnItems = new L.featureGroup().addTo(state.map);
    config.draw.options.edit.featureGroup = state.drawnItems;

    state.controlDraw = new L.Control.Draw(config.draw.options).addTo(state.map);
    state.map.on('draw:created', function (e) {
        let center = [e.layer._latlng.lat, e.layer._latlng.lng];
        // prevent more then 2 points
        if (Object.keys(state.drawnItems._layers).length < 2) {
            // prevent points outside profile
            if(!state.polygon || !state.polygon.length) {
                state.polygon = state.controlElevation._data.map(point => [point.x, point.y]);
            }
            if(turf.pointToLineDistance(center, state.polygon, {units: "meters"}) < config.draw.maxDistance) {
                state.drawnItems.addLayer(e.layer);
            } else {
                let line = $('.elevation-polyline');
                line.removeClass('lightblue-theme');
                line.addClass('red-theme');
                setTimeout(() => {
                    line.removeClass('lightred-theme');
                    line.addClass('lightblue-theme');
                }, 300);

            }
        }
    });

    // \/ hack !!!!
    // there's a problem with 'mousemove' propagation with almostOver disabled
    let fn = function (e){
        if($(state.controlDraw._toolbars.draw._modes.circlemarker.button).attr('class').indexOf('enabled') != -1) {
            state.controlElevation._mousemoveLayerHandler(e);
        }
    }
    state.map.on('mousemove', _.throttle(fn, 100));
    // /\ hack !!!!

}

const getProfileNames = function () {
    let retVal = [];
    let isRandomChoice = $('#randomRadio').is(':checked');
    let seriesSize = Number($('#seriesSize').val()) || 1;
    let firstProfile = Number($('#firstProfile').val()) || 1;
    // get full list of profiles
    $.getJSON(`${config.paths.names}`, function(json){
        let fullArray = json.names || [];
        if(isRandomChoice) {
            if(seriesSize >= fullArray.length) {
                retVal = fullArray;
            } else {
                let indexes = new Set();
                while (indexes.size < seriesSize) {
                    indexes.add(Math.floor(Math.random() * fullArray.length)); //!!!
                }
                [...indexes].sort((a,b) => a-b).forEach(a => retVal.push(fullArray[a]));
            }
        } else {
            retVal = fullArray.slice(firstProfile - 1, firstProfile - 1 + seriesSize);
        }
        // remove .geojson extensions
        state.data.tests = retVal.map(name => name.replace('.geojson', ''));
    });
}

const showProfile = function (name) {
    if (name) {
        resetMap();
        state.polygon = [];
        state.controlElevation.load(`${config.paths.geojson}/${name}.geojson`);
        $.getJSON(`${config.paths.clip}/${name}_bbox.json`, function (json) {
            state.bbox = json['bbox'];
            // state.imageOverlay = L.imageOverlay(`${config.paths.clip}/${name}.tif`, state.bbox, config.image.options).addTo(state.map);
            state.imageOverlay = true;
            state.data.name = name;
            setMapTitle(name);
        });
    } else {
        testToEnd();
    }
}


$(() => {
    $('#next').on('click', e => {
        if ($('#infoPanel').hasClass('d-none')) {
            const email = $('#email').val();
            const idText = $('#idText').val();

            $('.alert').alert('close');
            if (!isEmail(email)) {
                correctInput($('#email'), 'Enter a valid email address!');
            } else if (!isIdText(idText)) {
                correctInput($('#idText'), 'Enter the ID!');
            } else {
                state.data = prepareData($('#email').val(), $('#idText').val());
                startToInfo();
            }
        } else {
            infoToTest();
            showProfile(state.data.tests.shift());
        }
    })

    $('.export').on('click', (e) => {
        if (Object.keys(state.drawnItems._layers).length < 2) {
            correctInput($('.row    '), 'Mark two points (base and top)');
        } else {
            let points = state.drawnItems.toGeoJSON();

            let xhr = new XMLHttpRequest();
            xhr.addEventListener("load", () => {
                window.parent.postMessage('next', '*');
            });
            xhr.open("POST", "./scripts/main.php", true);
            xhr.send(JSON.stringify({
                points: points.features.map(f => f.geometry.coordinates),
                profile: state.data.name,
                email: state.data.email,
                id: state.data.id
            }));

            testToTest();
        }
    })

    $('.form-check-input').change(function(){
        if(!$('#seriesRadio').is(':checked')) {
            $('#firstProfileForm').hide();
        } else {
            $('#firstProfileForm').show();
        }
    });
});