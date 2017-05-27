    "use strict";

    var canvas, gl, program;

    var NumVertices = 36; //(6 faces)(2 triangles/face)(3 vertices/triangle)
    var points = [];
    var colors = [];

    function scale4(a, b, c) {
        var result = mat4();
        result[0][0] = a;
        result[1][1] = b;
        result[2][2] = c;
        return result;
    }


    var vertices = [
        vec4(-0.5, -0.5, 0.5, 1.0),
        vec4(-0.5, 0.5, 0.5, 1.0),
        vec4(0.5, 0.5, 0.5, 1.0),
        vec4(0.5, -0.5, 0.5, 1.0),
        vec4(-0.5, -0.5, -0.5, 1.0),
        vec4(-0.5, 0.5, -0.5, 1.0),
        vec4(0.5, 0.5, -0.5, 1.0),
        vec4(0.5, -0.5, -0.5, 1.0)
    ];

    // RGBA colors
    var vertexColors = [
        vec4(1.0, 0.0, 0.0, 1.0), // red
        vec4(0.5, 0.5, 0.5, 1.0), // gray
        vec4(0.0, 1.0, 0.0, 1.0), // green
        vec4(0.0, 0.0, 1.0, 1.0), // blue
        vec4(1.0, 1.0, 0.0, 1.0), // magenta
        vec4(0.0, 0.0, 0.0, 1.0), // black
        vec4(0.0, 0.0, 1.0, 1.0), // blue
        vec4(0.0, 1.0, 1.0, 1.0) // cyan
    ];


    // Parameters controlling the size of the Robot's arm
    var modelViewMatrix, projectionMatrix;
    function createNode(transform, render, sibling, child, name){
        var node = {
            transform: transform,
            render: render,
            sibling: sibling,
            child: child,
            name: name,
        }
        return node;
    }
    var Base = 0;

    var angle = 0;
    var phi_angle = 0;
    var MOVEMENT_OVERRIDE = false;

    var modelViewMatrixLoc;

    var vBuffer, cBuffer;
    function quad(a, b, c, d) {
        colors.push(vertexColors[a]);
        points.push(vertices[a]);
        colors.push(vertexColors[a]);
        points.push(vertices[b]);
        colors.push(vertexColors[a]);
        points.push(vertices[c]);
        colors.push(vertexColors[a]);
        points.push(vertices[a]);
        colors.push(vertexColors[a]);
        points.push(vertices[c]);
        colors.push(vertexColors[a]);
        points.push(vertices[d]);
    }
    function colorCube() {
        quad(1, 0, 3, 2);
        quad(2, 3, 7, 6);
        quad(3, 0, 4, 7);
        quad(6, 5, 1, 2);
        quad(4, 5, 6, 7);
        quad(5, 4, 0, 1);
    }
    function traverse(Id) {
        if (Id == null) return;
        var fig = figure[Id];

        stack.push(modelViewMatrix);
        modelViewMatrix = mult(modelViewMatrix, fig.transform);
        fig.render();
        if (fig.child != null) traverse(fig.child);
        modelViewMatrix = stack.pop();
        if (fig.sibling != null) traverse(fig.sibling);
    }
    var HAND_SCALE = 1;
    var PALM_HEIGHT = 4.0 * HAND_SCALE;
    var PALM_WIDTH = 4.0 * HAND_SCALE;
    var PALM_DEPTH = 1.0 * HAND_SCALE;
    var LOWER_ARM_HEIGHT = 3.0 * HAND_SCALE;
    var LOWER_ARM_WIDTH = 0.5;
    var MIDDLE_ARM_HEIGHT = 2.0 * HAND_SCALE;
    var MIDDLE_ARM_WIDTH = 0.5;
    var UPPER_ARM_HEIGHT = 1.0 * HAND_SCALE;
    var UPPER_ARM_WIDTH = 0.5;
    var FINGER_SPACING = (PALM_WIDTH/4 - LOWER_ARM_WIDTH)+0.15;
    var FINGER_RADIAL_SPACING = -4;

    var i = 0;
    var palmId = i++;

    var lowerThumbId = i++;
    var upperThumbId = i++;

    var lowerIndexId = i++;
    var middleIndexId = i++;
    var upperIndexId = i++;

    var lowerMiddleId = i++;
    var middleMiddleId = i++;
    var upperMiddleId = i++;

    var lowerRingId = i++;
    var middleRingId = i++;
    var upperRingId = i++;

    var lowerPinkyId = i++;
    var middlePinkyId = i++;
    var upperPinkyId = i++;

    var numNodes = i;
    var stack = [];
    var figure = [];
    var theta = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

    for (var i = 0; i < numNodes; i++){
        figure[i] = createNode(null, null, null, null, null);
    }
    window.onload = function init() {
            canvas = document.getElementById("gl-canvas");
            gl = WebGLUtils.setupWebGL(canvas);
            if (!gl) { alert("WebGL isn't available"); }
            gl.viewport(0, 0, canvas.width, canvas.height);

            gl.clearColor(1.0, 1.0, 1.0, 1.0);
            gl.enable(gl.DEPTH_TEST);
            program = initShaders(gl, "vertex-shader", "fragment-shader");
            gl.useProgram(program);
            modelViewMatrix = mat4();
            colorCube();

            vBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, vBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, flatten(points), gl.STATIC_DRAW);

            var vPosition = gl.getAttribLocation(program, "vPosition");
            gl.vertexAttribPointer(vPosition, 4, gl.FLOAT, false, 0, 0);
            gl.enableVertexAttribArray(vPosition);

            cBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, cBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, flatten(colors), gl.STATIC_DRAW);

            var vColor = gl.getAttribLocation(program, "vColor");
            gl.vertexAttribPointer(vColor, 4, gl.FLOAT, false, 0, 0);
            gl.enableVertexAttribArray(vColor);

            modelViewMatrixLoc = gl.getUniformLocation(program, "modelViewMatrix");

            projectionMatrix = ortho(-10, 10, -10, 10, -10, 10);
            gl.uniformMatrix4fv(gl.getUniformLocation(program, "projectionMatrix"), false, flatten(projectionMatrix));
        for(i=0; i<numNodes; i++) initNodes(i);
        render();
        relax();
        hover();
        // var angles = [];
        // angles[palmId]= 10;
        // angles[lowerThumbId]=12;
        // angles[lowerPinkyId]=31;
        // angles[lowerRingId]=-100;
        // angles[lowerMiddleId]=2;
        // angles[lowerIndexId]=90;
        // angles[1337]=90;
        // go_to(angles);
    }

for (var i = 0; i < numNodes; i++){
    theta[i] = 0; // Math.random()*15;
}
theta[palmId] = -39;
theta[lowerThumbId] = 80;
theta[upperThumbId] = 10;
var limits = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
limits[palmId] = 40;
limits[lowerThumbId] = 30;
limits[upperThumbId] = 90;

for(i=upperThumbId+1; i<upperPinkyId; i=i+3){
    limits[i] = 90
    limits[i+1] = 70
    limits[i+2] = 45
}

function initNodes(Id) {
    var m = mat4();
    var draw_finger_lower = function(){ drawFinger(0, 0.5 * LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT) };
    var draw_finger_middle = function(){ drawFinger(0, 0.5 * MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDTH, MIDDLE_ARM_HEIGHT) };
    var draw_finger_upper = function(){ drawFinger(0, 0.5 * UPPER_ARM_HEIGHT, UPPER_ARM_WIDTH, UPPER_ARM_HEIGHT) };
    switch (Id) {
        case palmId:
            m = rotate(0, 0, 0, 1);

            m = mult(m, rotate(angle, 0, 0, 1));
            m = mult(m, rotate(phi_angle, 1, 0, 0));
            m = mult(m, translate(-0.5 * PALM_WIDTH + width_err, -0.5 * PALM_HEIGHT + height_err, -PALM_WIDTH))
            m = mult(m, rotate(theta[Id], 0, 1, 0));
            figure[Id] = createNode(m, palm, null, lowerThumbId, "palm");
            break;
            
        // Thumb
        case lowerThumbId:
            var dx = PALM_WIDTH + LOWER_ARM_WIDTH * 0.5;
            m = translate(dx, PALM_HEIGHT/4, PALM_DEPTH/2);
            // m = mult(m, rotate(+10, 1, 0, 0));
            m = mult(m, rotate(+35, 1, 0, 0));
            m = mult(m, rotate(-theta[Id], 0, 0, 1));
            figure[Id] = createNode(m, draw_finger_lower, Id+2, Id+1, "lowerThumb");
            break;
        case upperThumbId:
            m = translate(0.0, LOWER_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 0, 0, 1));
            figure[Id] = createNode(m, draw_finger_middle, null, null, "lowerThumb");
            break;

        // Index
        case lowerIndexId:
            m = translate(FINGER_SPACING * 0 + LOWER_ARM_WIDTH * 0.5, PALM_HEIGHT, PALM_DEPTH/2);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            m = mult(m, rotate(FINGER_RADIAL_SPACING * -2, 0, 0, 1));
            figure[Id] = createNode(m, draw_finger_lower, Id+3, Id+1, "idx1");
            break;
        case lowerIndexId+1:
            m = translate(0, LOWER_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_middle, null, upperIndexId, "idx2");
            break;
        case lowerIndexId+2:
            m = translate(0, MIDDLE_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_upper, null, null, "idx3");
            break;

        // Middle
        case lowerMiddleId:
            m = translate((FINGER_SPACING + LOWER_ARM_WIDTH) * 1  + LOWER_ARM_WIDTH * 0.5, PALM_HEIGHT, PALM_DEPTH/2);
            m = mult(m, rotate(FINGER_RADIAL_SPACING * -1, 0, 0, 1));
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_lower, Id+3, Id+1, "midd1");
            break;
        case lowerMiddleId+1:
            m = translate(0, LOWER_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_middle, null, Id+1, "midd2");
            break;
        case lowerMiddleId+2:
            m = translate(0, MIDDLE_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_upper, null, null, "midd3");
            break;

        // Ring
        case lowerRingId:
            m = translate((FINGER_SPACING + LOWER_ARM_WIDTH) * 2  + LOWER_ARM_WIDTH * 0.5, PALM_HEIGHT, PALM_DEPTH/2);
            m = mult(m, rotate(FINGER_RADIAL_SPACING * 0, 0, 0, 1));
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_lower, Id+3, Id+1, "ring1");
            break;
        case lowerRingId+1:
            m = translate(0, LOWER_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_middle, null, Id+1, "ring2");
            break;
        case lowerRingId+2:
            m = translate(0, MIDDLE_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_upper, null, null, "ring3");
            break;

        // Pinky
        case lowerPinkyId:
            m = translate((FINGER_SPACING + LOWER_ARM_WIDTH) * 3  + LOWER_ARM_WIDTH * 0.5, PALM_HEIGHT, PALM_DEPTH/2);
            m = mult(m, rotate(FINGER_RADIAL_SPACING * 1, 0, 0, 1));
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_lower, null, Id+1, "pinky1");
            break;
        case lowerPinkyId+1:
            m = translate(0, LOWER_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_middle, null, Id+1, "pinky2");
            break;
        case lowerPinkyId+2:
            m = translate(0, MIDDLE_ARM_HEIGHT, 0.0);
            m = mult(m, rotate(theta[Id], 1, 0, 0));
            figure[Id] = createNode(m, draw_finger_upper, null, null, "pinky3");
            break;
    }

}
function palm() {
    var s = scale4(PALM_WIDTH, PALM_HEIGHT, PALM_DEPTH);
    var instanceMatrix = mult(translate(0.5 * PALM_WIDTH, 0.5 * PALM_HEIGHT, 0.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);

}
function drawFinger(dx, dy, width, height){
    var instanceMatrix = instanceMatrix = mult(modelViewMatrix, translate(dx, dy, 0.0) );
	instanceMatrix = mult(instanceMatrix, scale4(width, height, width));
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    // for(var i =0; i<6; i++){gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4)};
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}
function lowerThumb() {
    var dx = 0;// PALM_WIDTH + LOWER_ARM_WIDTH * 0.5;
    var dy = 0.5 * LOWER_ARM_HEIGHT;

    // draw orgin frame
    var instanceMatrix = modelViewMatrix;
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);
    // draw translated frame
    instanceMatrix = mult(instanceMatrix, translate(dx, dy, 0.0) );
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);
    // draw scaled frame
	instanceMatrix = mult(instanceMatrix, scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH));
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);
}
function upperThumb() {
    var dx = 0;
    var dy = 0.5 * UPPER_ARM_HEIGHT;

    // draw orgin frame
    var instanceMatrix = modelViewMatrix;
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);

    // draw translated frame
    instanceMatrix = mult(instanceMatrix, translate(dx, dy, 0.0) );
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);

    // draw scaled frame
	instanceMatrix = mult(instanceMatrix, scale4(MIDDLE_ARM_WIDTH, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDTH));
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(instanceMatrix));
    for(var i =0; i<6; i++) gl.drawArrays(gl.TRIANGLE_FAN, 4*i, 4);
}
var render = function() {
    traverse(palmId);
    requestAnimFrame(render);
}
function spettacolino() {
    MOVEMENT_OVERRIDE = true
    var original_position = get_angles();
    var angles = [];
    angles[palmId]= 0;
    angles[lowerThumbId]=80;
    angles[lowerPinkyId]=220;
    angles[lowerRingId]=220;
    angles[lowerMiddleId]=220;
    angles[lowerIndexId]=220;
    angles[1337]=0;
    go_to(angles, function(){
        go_to(original_position, function(){
            MOVEMENT_OVERRIDE = false;
        }, true);
    }, true);

    /*
    var movement = 0;
    var speed = 2;
    if(theta[palmId] < limits[palmId]){
        movement = 1
        theta[palmId] += 1;
    }
    var finger_angle = -theta[lowerThumbId] + theta[upperThumbId];
    if(finger_angle < 180){ // off by 1/4
        var arclength = (75+finger_angle)/(180+75);
        console.log(arclength);
        if(limits[lowerThumbId] > -theta[lowerThumbId]){
            theta[lowerThumbId] += -2;
            movement = 1
        }
        if(limits[upperThumbId] > theta[upperThumbId]){
        theta[upperThumbId] += 1;
            movement = 1
        }
        if(movement == 1){
            speed *= arclength;
        }
    }
    for(i=upperThumbId+1; i<upperPinkyId; i=i+3){
        var finger_angle = theta[i] + theta[i+1] + theta[i+2];
        if(finger_angle < 275-3){
            for(var j=i; j<i+3; j++){
                if(limits[j] > theta[j]){
                    theta[j] += 0.8 + ((12-i)/12) * speed;
                    movement = 1;
                }
            }
        }
    }
    for(i=0; i<numNodes; i++) initNodes(i);
    if (movement == 1) {
        setTimeout(function() {
            spettacolino()
        }, 40);
    } else {
        for(i=upperThumbId+1; i<upperPinkyId; i=i+3){
        var finger_angle = theta[i] + theta[i+1] + theta[i+2];
            console.log(i, finger_angle);
        }
        MOVEMENT_OVERRIDE = false;
        go_to(original_position);
    }
    */
}
angle = 0;
var hand_direction = 1;
function bye() {
    if(MOVEMENT_OVERRIDE){ return }
    for (var i = 0; i < numNodes; i++){
        theta[i] = Math.random()*30;
    }
    theta[0] = 0;
    wave();
}
var direction_changes = 0
function wave(callback){
    if(Math.abs(angle) > 30){
        direction_changes += 1
        hand_direction = -1 * hand_direction;
    }
    angle += hand_direction;
    for(i=0; i<numNodes; i++) initNodes(i);
    if(direction_changes < 5 && angle != 0){
        setTimeout(function() {
            wave(callback)
        }, 40);
    } else {
        if(callback){
            callback();
        }
    }
}
var height_err = 0;
var width_err = 0;
var theta_err = 0;
var phi_error = 0;
function hover(){
    if(MOVEMENT_OVERRIDE) return;

    for (var i = 1; i < numNodes; i++){
        // var controllability = (theta[i] - limits[i])/(2*limits[i])
        theta[i] += 0.3 * (Math.random() - 0.5); // / controllability;
    }
    height_err += 0.015 * (Math.random() - 0.5);
    width_err += 0.005 * (Math.random() - 0.5);
    // theta_err += 0.2 * (Math.random() - 0.5);
    // phi_error += 0.2 * (Math.random() - 0.5);
    for(i=0; i<numNodes; i++) initNodes(i);
    setTimeout(function() {
        hover()
    }, 100);
}
var is_relaxing = false;
function relax(){
    if(Math.random() < 0.10 && !MOVEMENT_OVERRIDE && !is_relaxing){
        is_relaxing = true;
        var work_position = get_angles();
        var rest_position = [];
        rest_position[palmId]= 30;
        rest_position[lowerThumbId]=14;
        rest_position[lowerPinkyId]=31;
        rest_position[lowerRingId]=40;
        rest_position[lowerMiddleId]=35;
        rest_position[lowerIndexId]=32;
        rest_position[1337]=150;
        function resume(){ 
            wave(function(){
                setTimeout(function() {
                    if (MOVEMENT_OVERRIDE) return;
                    go_to(work_position, function(){
                        is_relaxing = false;
                    });
                }, 1000);
            });
        }
        go_to(rest_position, resume);
    }
    setTimeout(relax, 1000);
}
function go_to(angles, callback, priority) {
    if(!priority && MOVEMENT_OVERRIDE) return;
    var movement = false;
    var speed = 0.5;
    var direction = 1;

    var error = angles[palmId] - theta[palmId];
    var direction = Math.max(-1, Math.min(1, error));
    if(Math.abs(direction) == 1){
	    if(Math.abs(theta[palmId]) < limits[palmId]){
            movement = true;
            theta[palmId] += direction * speed;
	    }
    }
    var error = angles[1337] - phi_angle;
    var direction = Math.max(-1, Math.min(1, error));
    if(Math.abs(direction) == 1){
        movement = true;
        phi_angle += direction * speed;
    }

    var thumb_angle = -theta[lowerThumbId] + theta[upperThumbId];
    error = angles[lowerThumbId] - thumb_angle;
    direction = Math.max(-1, Math.min(1, error));
    if(Math.abs(direction) == 1){
        if(limits[lowerThumbId] > -theta[lowerThumbId]){
            theta[lowerThumbId] += -direction * speed / 2;
            movement = true;
        }
        if(limits[upperThumbId] > theta[upperThumbId]){
            theta[upperThumbId] += direction * speed / 4;
            movement = true;
        }
    }
    if(movement){
        if(direction > 0){
            speed /= Math.abs(error/180);
        } else {
            speed += Math.abs(error/30);
        }
    }
    for(i=upperThumbId+1; i<upperPinkyId; i=i+3){
        var finger_angle = theta[i] + theta[i+1] + theta[i+2];
	    error = finger_angle - angles[i];
    	direction = Math.max(-1, Math.min(1, -error));
        if(Math.abs(direction) == 1){
            for(var j=i; j<i+3; j++){
                var finger_speed = 0.2;
                finger_speed += Math.pow(direction * (12-i)/50, 2)
                var step = direction * speed * finger_speed / ((j+1)/6)

                if(Math.abs(limits[j]) > theta[j] + step){
                    theta[j] += step;
                    movement = true;
                }
            }
        }
    }
    for(i=0; i<numNodes; i++) initNodes(i);
    if (movement) {
        setTimeout(function() {
            go_to(angles, callback, priority)
        }, 20);
    } else {
        if(callback){
            callback();
        }
    }
}
function get_angles(){
    var angles = [];
    angles[palmId] = theta[palmId];
    angles[1337] = phi_angle;
    angles[lowerThumbId] = -theta[lowerThumbId] + theta[upperThumbId];
    for(i=upperThumbId+1; i<upperPinkyId; i=i+3){
        angles[i] = theta[i] + theta[i+1] + theta[i+2];
    }
    return angles;
}
