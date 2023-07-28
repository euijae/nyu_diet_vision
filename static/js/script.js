const ontologyMap = new Map(Object.entries(ontology))
let newFoodClassList = []

for (let [key, category] of ontologyMap.entries()) {
    for (let product of category) {
        newFoodClassList.push({ 'title': product })
    }
}

$('.ui.search').search({ source: newFoodClassList });

var color_choices = [
    "#FF00FF",
    "#8622FF",
    "#FE0056",
    "#00FFCE",
    "#FF8000",
    "#00B7EB",
    "#FFFF00",
    "#0E7AFE",
    "#FFABAB",
    "#0000FF",
    "#CCCCCC",
];

var canvas = document.getElementById('canvas');

var ctx = canvas.getContext('2d');
var img = new Image();
var img3 = new Image();
var rgb_color = color_choices[Math.floor(Math.random() * color_choices.length)] 
var opaque_color =  'rgba(0,0,0,0.5)';

var scaleFactor = 1;
var scaleSpeed = 0.01;

var points = [];
var regions = [];
var masterPoints = [];
var masterColors = [];

var showNormalized = false;
var drawMode = "polygon";
var imageReady = false;

var modeMessage = document.querySelector('#mode');
var coords = document.querySelector('#coords');

// if user presses L key, change draw mode to line and change cursor to cross hair
// document.addEventListener('keydown', function(e) {
//     if (e.key == 'l') {
//         drawMode = "line";
//         canvas.style.cursor = 'pointer';
//         modeMessage.innerHTML = "Draw Mode: Line (press <kbd>p</kbd> to change to polygon drawing)";
//     }
//     if (e.key == 'p') {
//         drawMode = "polygon";
//         canvas.style.cursor = 'pointer';
//         modeMessage.innerHTML = 'Draw Mode: Polygon (press <kbd>l</kbd> to change to line drawing)';
//     }
// });

function clipboard(selector) {
    var copyText = document.querySelector(selector).innerText;
    navigator.clipboard.writeText(copyText);
}

function zoom(clicks) {
    // if w > 60em, stop
    if ((scaleFactor + clicks * scaleSpeed) * img.width > 40 * 16) {
        return;
    }
    scaleFactor += clicks * scaleSpeed;
    scaleFactor = Math.max(0.1, Math.min(scaleFactor, 0.8));
    var w = img.width * scaleFactor;
    var h = img.height * scaleFactor;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
}

// placeholder image
img.src = '../../static/images/empty.png'; // 'https://assets.website-files.com/5f6bc60e665f54545a1e52a5/63d3f236a6f0dae14cdf0063_drag-image-here.png';
img.onload = function() {
    scaleFactor = 0.5;
    canvas.style.width = img.width * scaleFactor + 'px';
    canvas.style.height = img.height * scaleFactor + 'px';
    canvas.width = img.width;
    canvas.height = img.height;
    canvas.style.borderRadius = '10px';
    ctx.drawImage(img, 0, 0);
};

function drawLine(x1, y1, x2, y2) {
    // EUIJAE ctx.beginPath();
    // set widht
    // EUIJAE ctx.lineWidth = 5;
    // EUIJAE ctx.moveTo(x1, y1);
    // EUIJAE ctx.lineTo(x2, y2);
    // EUIJAE ctx.stroke();
}

function getScaledCoords(e) {
    var rect = canvas.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    return [x / scaleFactor, y / scaleFactor];
}

function clearall() {
    img.src = '../../static/images/empty.png';
    img.onload = function() {
        scaleFactor = 0.5;
        canvas.style.width = img.width * scaleFactor + 'px';
        canvas.style.height = img.height * scaleFactor + 'px';
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.borderRadius = '10px';
        ctx.drawImage(img, 0, 0);
    };
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    points = [];
    masterPoints = [];
    // document.querySelector('#python').innerHTML = '';

    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState === xmlHttp.DONE && xmlHttp.status === 200) {
            $('#cover-spin').hide()
            imageReady = false;
            isUpdateFoodClass = false;
        }
    }

    xmlHttp.open("GET", 'http://127.0.0.1:8000/clear', true);
    xmlHttp.onprogress = function() {
        $('#cover-spin').show(0)
        console.log('/clear >> onprogress');
        console.log("LOADING: ", xmlHttp.status);
    };
    xmlHttp.send(null)

    $('#selectFoodClass').removeClass('green');
    $('#modifyFoodClass').removeClass('green');
    $('#tableBody3 tr').remove();
    $('#tableBody1').css('display', '');
}

document.querySelector('#clear').addEventListener('click', function(e) {
    e.preventDefault();
    clearall();
});

// document.querySelector('#clipboard').addEventListener('click', function(e) {
//     e.preventDefault();
//     clipboard("#clipboard");
// });

canvas.addEventListener('click', function(e) {
    // set cursor to pointer
    // canvas.style.cursor = 'pointer';
    // if line mode and two points have been drawn, add to masterPoints
    if (drawMode == 'line' && points.length == 2) {
        masterPoints.push(points);
        points = [];
    }
    var x = getScaledCoords(e)[0];
    var y = getScaledCoords(e)[1];
    // EUIJAE console.log(`(x, y) = (${x}, ${y}) / click`);
    x = Math.round(x);
    y = Math.round(y);

    points.push([x, y]);
    ctx.beginPath();
    ctx.strokeStyle = rgb_color;
    // add rgb_color to masterColors
    
    if (masterColors.length == 0) {
        masterColors.push(rgb_color);
    }

    ctx.arc(x, y, 155, 0, 2 * Math.PI);
    // concat all points into one array
    var parentPoints = [];

    for (var i = 0; i < masterPoints.length; i++) {
        parentPoints.push(masterPoints[i]);
    }
    // add "points"
    parentPoints.push(points);

    // writePoints(parentPoints);
});

document.querySelector('#saveImage').addEventListener('click', function(e) {
    e.preventDefault();

    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == xmlHttp.OPENED) {
            console.log('/upload/image >> xmlHttp.readyState == xmlHttp.OPENED')
            $('#cover-spin').show(0)
        }
        if (xmlHttp.readyState === xmlHttp.DONE && xmlHttp.status === 200) {
            img.src = '../../static/images/fish_chips.jpg'
            img.onload = function() {
                scaleFactor = 0.25;
                canvas.style.width = img.width * scaleFactor + 'px';
                canvas.style.height = img.height * scaleFactor + 'px';
                canvas.width = img.width;
                canvas.height = img.height;
                canvas.style.borderRadius = '10px';
                ctx.drawImage(img, 0, 0);
            };
            // show coords
            // document.getElementById('coords').style.display = 'inline-block';
            // EUIJAE
            canvas.style.cursor = 'pointer';
            $('#cover-spin').hide()
            imageReady = true

            e.preventDefault();
            $('#selectFoodClass').addClass('green');
            $('#tableBody1').css('display', 'none');
            $('#tableBody3').css('display', '');
        }
    }

    xmlHttp.open("GET", 'http://127.0.0.1:8000/upload/image', true);
    xmlHttp.onprogress = function() {
        $('#cover-spin').show(0)
        console.log('/upload/image >> onprogress')
        console.log("LOADING: ", xmlHttp.status);
    };
    xmlHttp.send(null)
});

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
    if(imageReady) {
        x2 = getScaledCoords(e)[0];
        y2 = getScaledCoords(e)[1];

        console.log(`(x1, y1, x2, y2) = (${x1}, ${y1}, ${x2}, ${y2}) / mouseup`)

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
        const xmlHttp = new XMLHttpRequest();

        if ($("#modifyFoodClass").hasClass('green')) {
            xmlHttp.onreadystatechange = function() { 
                if (xmlHttp.readyState === xmlHttp.OPENED) {
                    $('#cover-spin').show(0)
                }
                if (xmlHttp.readyState === xmlHttp.DONE && xmlHttp.status === 200) {
                    const responseObject = JSON.parse(xmlHttp.responseText);
                    const file_image_name = responseObject.path
                    
                    img.src = '../../static/images/fish_chips.jpg'
                    img.onload = function() {
                        scaleFactor = 0.25;
                        canvas.style.width = img.width * scaleFactor + 'px';
                        canvas.style.height = img.height * scaleFactor + 'px';
                        canvas.width = img.width;
                        canvas.height = img.height;
                        canvas.style.borderRadius = '10px';
                        ctx.drawImage(img, 0, 0);
                        var img4 = new Image();
                        img4.src = `../../static/images/${file_image_name}`;
                        img4.onload = function() {
                            ctx.drawImage(img4, 0, 0)
                        }
                    };
                    $('#cover-spin').hide();
                }

                if (xmlHttp.status >= 400) {
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
                if (xmlHttp.readyState === xmlHttp.OPENED) {
                    $('#cover-spin').show(0)
                }
                if (xmlHttp.readyState === xmlHttp.DONE && xmlHttp.status === 200) {
                    const responseObject = JSON.parse(xmlHttp.responseText);
                    const food_class = responseObject.class;
                    const food_area = responseObject.volume;
                    const food_calories = responseObject.calories;
                    const file_image_name = responseObject.path;

                    // var code_template = `food_class: ${food_class} || food_area: ${food_area} || file_image_name: ${file_image_name}` ;
                    // document.querySelector('#python').innerHTML = code_template;
                    
                    img.src = '../../static/images/fish_chips.jpg'
                    img.onload = function() {
                        scaleFactor = 0.25;
                        canvas.style.width = img.width * scaleFactor + 'px';
                        canvas.style.height = img.height * scaleFactor + 'px';
                        canvas.width = img.width;
                        canvas.height = img.height;
                        canvas.style.borderRadius = '10px';
                        ctx.drawImage(img, 0, 0);

                        var img4 = new Image();
                        img4.src = `../../static/images/${file_image_name}`;
                        img4.onload = function() {
                            ctx.drawImage(img4, 0, 0)
                        }
                    };
                    $('#cover-spin').hide();
                    $('#tableBody3 tr').remove();
                    $('#tableBody3').append(`
                        <tr>
                            <td>${food_class}</td>
                            <td>${food_area}</td>
                            <td>${food_calories.calories}</td>
                        </tr>
                    `);
                }

                if (xmlHttp.status >= 400) {
                    $('#cover-spin').hide();
                }
            }
            xmlHttp.open("POST", 'http://127.0.0.1:8000/segment/data', true);
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
        }
    }
});

$('#submitFoodClassInput').on('click', function(e) {
    e.preventDefault();

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState === xmlHttp.OPENED) {
            $('#cover-spin').show(0)
        }
        if (xmlHttp.readyState === xmlHttp.DONE && xmlHttp.status === 200) {
            const responseObject = JSON.parse(xmlHttp.responseText);
            const message = responseObject.message;

            // var code_template = `message: ${message}` ;
            // document.querySelector('#python').innerHTML = code_template;
            console.log('/classify/modify/good');
            $('#myFoodClassInput').val('')
            $('#cover-spin').hide();

            $('#selectFoodClass').addClass('green');

            // turn off
            $('#searchFoodClassInput').removeClass('focus');
            $('#searchFoodClassInput').addClass('disabled');

            // turn off
            $('#submitFoodClassInput').removeClass('primary');
            $('#submitFoodClassInput').addClass('disabled');

            // turn off
            $('#modifyFoodClass').removeClass('green');
            img.src = '../../static/images/fish_chips.jpg'
            img.onload = function() {
                scaleFactor = 0.25;
                canvas.style.width = img.width * scaleFactor + 'px';
                canvas.style.height = img.height * scaleFactor + 'px';
                canvas.width = img.width;
                canvas.height = img.height;
                canvas.style.borderRadius = '10px';
                ctx.drawImage(img, 0, 0);
            };
        }

        if (xmlHttp.status >= 400) {
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

// on canvas hover, if cursor is pointer, draw line from last point to cursor
canvas.addEventListener('mousemove', function(e) {
    var x = getScaledCoords(e)[0];
    var y = getScaledCoords(e)[1];
    // round
    x = Math.round(x);
    y = Math.round(y);

    // update x y coords
    // var xcoord = document.querySelector('#x');
    // var ycoord = document.querySelector('#y');
    // xcoord.innerHTML = x;
    // ycoord.innerHTML = y;

    if (canvas.style.cursor == 'pointer2') {
        //ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        for (var i = 0; i < points.length - 1; i++) {
            // draw arc around each point
            ctx.beginPath();
            ctx.strokeStyle = rgb_color;
            ctx.arc(points[i][0], points[i][1], 5, 0, 2 * Math.PI);
            // fill with white
            ctx.fillStyle = 'white';
            ctx.fill();
            ctx.stroke();
            drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]);
        }
        if ((points.length > 0 && drawMode == "polygon") || (points.length > 0 && points.length < 2 && drawMode == "line")) {
            ctx.beginPath();
            ctx.strokeStyle = rgb_color;
            ctx.arc(points[i][0], points[i][1], 5, 0, 2 * Math.PI);
            // fill with white
            ctx.fillStyle = 'white';
            ctx.fill();
            ctx.stroke();
            drawLine(points[points.length - 1][0], points[points.length - 1][1], x, y);

            if (points.length == 2 && drawMode == "line") {
                console.log("line");
                // draw arc around each point
                ctx.beginPath();
                ctx.strokeStyle = rgb_color;
                ctx.arc(points[0][0], points[0][1], 5, 0, 2 * Math.PI);
                // fill with white
                ctx.fillStyle = 'white';
                ctx.fill();
                ctx.stroke();
                masterPoints.push(points);
                points = [];
            }
        }
        var parentPoints = [];

        for (var i = 0; i < masterPoints.length; i++) {
            parentPoints.push(masterPoints[i]);
        }
        parentPoints.push(points);

        // drawAllPolygons();
    }
});

canvas.addEventListener('drop', function(e) {
    e.preventDefault();
    var file = e.dataTransfer.files[0];
    var reader = new FileReader();
    
    reader.onload = function(event) {
        img.src = event.target.result; // only allow image files
    };
    reader.readAsDataURL(file);

    var mime_type = file.type;

    if (mime_type != 'image/png' && mime_type != 'image/jpeg' && mime_type != 'image/jpg') {
        alert('Only PNG, JPEG, and JPG files are allowed.');
        return;
    }

    img.onload = function() {
        scaleFactor = 0.25;
        canvas.style.width = img.width * scaleFactor + 'px';
        canvas.style.height = img.height * scaleFactor + 'px';
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.borderRadius = '10px';
        ctx.drawImage(img, 0, 0);
    };
    // show coords
    // document.getElementById('coords').style.display = 'inline-block';
    canvas.style.cursor = 'pointer';
});

// $('#saveImageTest').on('click', function(e) {
//     e.preventDefault();
//     $('#selectFoodClass').addClass('green');
//     $('#tableBody1').css('display', 'none');
//     $('#tableBody3').css('display', '');
// });
    
// $('#submitFoodClassInput').on('click', function(e) {
//     e.preventDefault();
//     let value = $('#myFoodClassInput').val();
// })

$('#selectFoodClass').on('click', function(e) {
    e.preventDefault();
    $('#selectFoodClass').addClass('green');

    // turn off
    $('#searchFoodClassInput').removeClass('focus');
    $('#searchFoodClassInput').addClass('disabled');

    // turn off
    $('#submitFoodClassInput').removeClass('primary');
    $('#submitFoodClassInput').addClass('disabled');
    
    // turn off
    $('#modifyFoodClass').removeClass('green');

    $('#myFoodClassInput').val('')
});

$('#modifyFoodClass').on('click', function(e) {
    e.preventDefault();

    // turn on
    $('#searchFoodClassInput').addClass('focus');
    $('#searchFoodClassInput').removeClass('disabled');

    // turn on
    $('#submitFoodClassInput').addClass('primary');
    $('#submitFoodClassInput').removeClass('disabled');
    
    // turn on
    $('#modifyFoodClass').addClass('green');

    // turn off
    $('#selectFoodClass').removeClass('green');

    $('#tableBody1').css('display', 'none');

    img.src = '../../static/images/fish_chips.jpg'
    img.onload = function() {
        scaleFactor = 0.25;
        canvas.style.width = img.width * scaleFactor + 'px';
        canvas.style.height = img.height * scaleFactor + 'px';
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.borderRadius = '10px';
        ctx.drawImage(img, 0, 0);
    };

    $('#tableBody3 tr').remove();
});

function isButtonActive(selector) {
    return $("#" + selector).hasClass('green');
}