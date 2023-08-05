const usdaFoodsMap = new Map(Object.entries(usdaFoods))
let newFoodClassList = []

for (let [key, category] of usdaFoodsMap.entries()) {
    for (let product of category) {
        newFoodClassList.push({ 'title': product })
    }
}

$('.ui.search').search({ source: newFoodClassList });

var color_choices = [ "#FF00FF", "#8622FF", "#FE0056", "#00FFCE", "#FF8000", "#00B7EB", "#FFFF00", "#0E7AFE", "#FFABAB", "#0000FF", "#CCCCCC" ];
var canvas = document.getElementById('canvas');

var ctx = canvas.getContext('2d');
var img = new Image();

var lastOverlayImageName = null;
var annotatorImageName = null;

var rgb_color = color_choices[Math.floor(Math.random() * color_choices.length)] 
var opaque_color =  'rgba(0,0,0,0.5)';

var scaleFactor = 1;
var imageReady = false;

var modeMessage = document.querySelector('#mode');

// placeholder image
createImage(true);

if (!imageReady) {
    $('#introMessage').show();
}

function getScaledCoords(e) {
    var rect = canvas.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    return [x / scaleFactor, y / scaleFactor];
}

document.querySelector('#clear').addEventListener('click', function(e) {
    e.preventDefault();
    clearCanvas();
    createImage(true)

    if (imageReady) {
        const xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState === xmlHttp.DONE) {
                if (xmlHttp.status === 200) {
                    imageReady = false;
                    annotatorImageName = null;
                    lastOverlayImageName = null;
                }

                $('#cover-spin').hide()
            }
        }
        xmlHttp.open("GET", 'http://127.0.0.1:8000/clear', true);
        xmlHttp.onprogress = function() {
            $('#cover-spin').show(0)
        };
        xmlHttp.send(null)

        $('#selectFoodClass').removeClass('green');
        $('#modifyFoodClass').removeClass('green');
        $('#tableBody2 tr').remove();
        $('#tableBody1').css('display', '');
    }
});

document.querySelector('#saveImage').addEventListener('click', function(e) {
    e.preventDefault();
    $('#fileContainer').trigger('click');
});

$('input#fileContainer').on('change', function (e) {
    e.preventDefault();

    imageName = this.files[0].name;
    var reader = new FileReader();
    reader.onload = function (e) {
        var thisImage = reader.result;
        localStorage.setItem("originalImageData", thisImage);
        uploadFile(imageName, thisImage.replace("data:", "").replace(/^.+,/, ""));
    };

    if (this.files[0])
        reader.readAsDataURL(this.files[0]);
});

function uploadFile(filename, filedata) {
    $('#cover-spin').show(0);
    var formData = new FormData();
    console.log(`filename: ${filename}`);
    formData.append('filename', filename);
    formData.append('filedata', filedata);

    fetch('http://127.0.0.1:8000/upload/image', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(response => {
        console.log(`[uploadFile] ${JSON.stringify(response)}`);
        annotatorImageName = response.file_name;
        imageReady = true;
        canvas.style.cursor = 'pointer';

        createImage(false);
        toggleSelectModfiy(true);

        $('#tableBody1').css('display', 'none');
        $('#tableBody2').css('display', '');
    }).catch(error => {
        console.log(error);
    }).finally(() => {
        $('#cover-spin').hide();
        $('#introMessage').hide();
    });
}

let x1;
let y1;
let x2;
let y2;

canvas.addEventListener('mousedown', function(e) {
    if (imageReady) {
        x1 = getScaledCoords(e)[0];
        y1 = getScaledCoords(e)[1];

        console.log(`(x1, y1) = (${x1}, ${y1}) / mousedown`)
    }
});

canvas.addEventListener('mouseup', function(e) {
    if (!imageReady) {
        return;
    }

    const xmlHttp = new XMLHttpRequest();

    if ($("#modifyFoodClass").hasClass('green')) {
        x2 = getScaledCoords(e)[0];
        y2 = getScaledCoords(e)[1];

        console.log(`(x1, y1, x2, y2) = (${x1}, ${y1}, ${x2}, ${y2}) / mouseup / modifyFoodClass`)

        if (y1 > y2) [y1, y2] = [y2, y1]
        if (x1 > x2) [x1, x2] = [x2, x1]

        let width  = Math.abs(x1-x2);
        let height = Math.abs(y1-y2);
        
        ctx.beginPath();
        ctx.strokeStyle = rgb_color;
        ctx.lineWidth = 4;
        ctx.fill();
        ctx.rect(x1, y1, width, height);
        ctx.stroke();

        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState === xmlHttp.OPENED) {
                $('#cover-spin').show(0)
            }
            if (xmlHttp.readyState === xmlHttp.DONE) {
                if (xmlHttp.status === 200) {
                    const responseObject = JSON.parse(xmlHttp.responseText);
                    const file_image_name = responseObject.file_name;
                    lastOverlayImageName = file_image_name;
                    createImage(false, false);
                }

                $('#cover-spin').hide();
            }
        }
        xmlHttp.open("POST", 'http://127.0.0.1:8000/segment/group', true);
        xmlHttp.onprogress = function() {
            console.log("LOADING: ", xmlHttp.status);
            if (xmlHttp.status < 400) {
                $('#cover-spin').show(0)
            } else {
                $('#cover-spin').hide()
            }
        };
        xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xmlHttp.send(JSON.stringify({ 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2 }))
    } else {
        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState === xmlHttp.DONE) { 
                if (xmlHttp.status === 200) {
                    const responseObject = JSON.parse(xmlHttp.responseText);
                    const food_class = responseObject.class;
                    const food_area = responseObject.volume;

                    console.log(`food_class = ${food_class}, food_area = ${food_area}`);
                    console.log(`(x1, y1) = (${x1}, ${y1}) / mouseup / selectFoodClass`)

                    $('#tableBody2 tr').remove();
                    $('#tableBody2').append(`
                        <tr>
                            <td>${food_class}</td>
                            <td>${food_area}</td>
                        </tr>
                    `);
                }

                $('#cover-spin').hide();
            }
        }
        xmlHttp.open("POST", 'http://127.0.0.1:8000/segment/data', true);
        xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xmlHttp.send(JSON.stringify({ 'x1': x1, 'y1': y1, 'x2': x1, 'y2': y1 }))
    }
});

$('#submitFoodClassInput').on('click', function(e) {
    e.preventDefault();

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState === xmlHttp.OPENED) {
            $('#cover-spin').show(0)
        }

        if (xmlHttp.readyState === xmlHttp.DONE) {
            if (xmlHttp.status === 200) {
                const responseObject = JSON.parse(xmlHttp.responseText);
                const file_name = responseObject.file_name;
                annotatorImageName = file_name;
                
                createImage(false, true);
                toggleSelectModfiy(true);
                turnOnSearch(false);
                $('#cover-spin').hide();
            }

            $('#cover-spin').hide();
        }
    }
    xmlHttp.open("POST", 'http://127.0.0.1:8000/classify/modify', true);
    xmlHttp.onprogress = function() {
        console.log("LOADING: ", xmlHttp.status);
        if (xmlHttp.status < 400) {
            $('#cover-spin').show(0)
        } else {
            $('#cover-spin').hide()
        }
    };
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    let modified_food_class = $('#myFoodClassInput').val();
    xmlHttp.send(JSON.stringify({ 'food_class': modified_food_class }))
})

$('#selectFoodClass').on('click', function(e) {
    e.preventDefault();
    turnOnSearch(false);
    toggleSelectModfiy(true);

    if (imageReady) {
        createImage(false);
    }
});

$('#modifyFoodClass').on('click', function(e) {
    e.preventDefault();
    turnOnSearch(true);
    toggleSelectModfiy(false);

    $('#tableBody1').css('display', 'none');
    $('#tableBody2 tr').remove();

    if (imageReady) {
        img.src = localStorage.getItem("originalImageData");
        img.onload = function() {
            scaleFactor = 0.25;
            canvas.style.width = img.width * scaleFactor + 'px';
            canvas.style.height = img.height * scaleFactor + 'px';
            canvas.width = img.width;
            canvas.height = img.height;
            canvas.style.borderRadius = '10px';
            ctx.clearRect(0, 0, img.width * scaleFactor + 'px', img.height * scaleFactor + 'px');
            ctx.drawImage(img, 0, 0);
        };
    }
});

function toggleSelectModfiy(isSelect) {
    if (isSelect) {
        $('#selectFoodClass').addClass('green');
        $('#modifyFoodClass').removeClass('green');
        $('#myFoodClassInput').val('')
    } else {
        $('#selectFoodClass').removeClass('green');
        $('#modifyFoodClass').addClass('green');
    }
}

function turnOnSearch(isOn) {
    if (isOn) {
        $('#searchFoodClassInput').addClass('focus');
        $('#searchFoodClassInput').removeClass('disabled');
        $('#submitFoodClassInput').addClass('primary');
        $('#submitFoodClassInput').removeClass('disabled');
    } else {
        $('#searchFoodClassInput').removeClass('focus');
        $('#searchFoodClassInput').addClass('disabled');
        $('#submitFoodClassInput').removeClass('primary');
        $('#submitFoodClassInput').addClass('disabled');
    }
}

function createImage(isEmptyFile, isAnnotator = true) {
    var scaleFactor = isEmptyFile ? 0.5 : 0.25;

    if (isEmptyFile) {
        img.src = '../../static/images/empty.png';
        img.onload = function() {
            canvas.style.width = img.width * scaleFactor + 'px';
            canvas.style.height = img.height * scaleFactor + 'px';
            canvas.width = img.width;
            canvas.height = img.height;
            canvas.style.borderRadius = '10px';
            clearCanvas();
            ctx.drawImage(img, 0, 0);
        }
    } else {
        img.src = localStorage.getItem('originalImageData');
        img.onload = function() {
            canvas.style.width = img.width * scaleFactor + 'px';
            canvas.style.height = img.height * scaleFactor + 'px';
            canvas.width = img.width;
            canvas.height = img.height;
            canvas.style.borderRadius = '10px';
            ctx.clearRect(0, 0, img.width * scaleFactor + 'px', img.height * scaleFactor + 'px');
            ctx.drawImage(img, 0, 0);
            var overlayImage = new Image();
            overlayImage.src = `../../static/images/overlays/${isAnnotator ? annotatorImageName : lastOverlayImageName}`;
            overlayImage.onload = function() {
                ctx.drawImage(overlayImage, 0, 0)
            }
        }
    }
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}