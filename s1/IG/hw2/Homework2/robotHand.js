"use strict";

var canvas, gl, program;

var NumVertices = 36; //(6 faces)(2 triangles/face)(3 vertices/triangle)

var points = [];
var colors = [];

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
    vec4(1.0, 0.0, 1.0, 1.0), // red
    vec4(0.0, 0.5, 0.5, 1.0), // gray
    vec4(0.5, 1.0, 0.0, 1.0), // green
    vec4(0.0, 0.0, 1.0, 1.0), // blue
    vec4(1.0, 0.0, 0.0, 1.0), // magenta
    vec4(0.0, 0.0, 0.0, 1.0), // black
    vec4(0.0, 0.0, 1.0, 1.0), // blue
    vec4(0.0, 1.0, 1.0, 1.0) // cyan
];


// Parameters controlling the size of the Robot's arm

var BASE_HEIGHT = 5.0;
var BASE_WIDTH = 6.0;
var LOWER_ARM_HEIGHT = 3.0;
var LOWER_ARM_WIDTH = 0.5;
var UPPER_ARM_HEIGHT = 1.5;
var UPPER_ARM_WIDTH = 0.5;
var MIDDLE_ARM_HEIGHT = 2.0;
var MIDDLE_ARM_WIDHT = 0.5;

// Shader transformation matrices

var modelViewMatrix, projectionMatrix;


var i = 0;
var palmId = ++i;

var thumb1Id = ++i;
var thumb2Id = ++i;

var index1Id = ++i;
var index2Id = ++i;
var index3Id = ++i;

var middle1Id = ++i;
var middle2Id = ++i;
var middle3Id = ++i;

var ring1Id = ++i;
var ring2Id = ++i;
var ring3Id = ++i;

var pinky1Id = ++i;
var pinky2Id = ++i;
var pinky3Id = ++i;

var numNodes = i;
var stack = [];
var figure = [];
for (var i = 0; i < numNodes; i++) figure[i] = createNode(null, null, null, null);

function createNode(transform, render, sibling, child){
    var node = {
    transform: transform,
    render: render,
    sibling: sibling,
    child: child,
    }
    return node;
}

function initNodes(Id) {

    var m = mat4();
    switch (Id) {
        case palmId:
            m = rotate(theta[palmId], 0, 1, 0);
            figure[palmId] = createNode(m, torso, null, headId);
            break;
        case index1Id:
        case index2Id:
        case index3Id:
            m = translate(0.0, torsoHeight + 0.5 * headHeight, 0.0);
            m = mult(m, rotate(theta[head1Id], 1, 0, 0))
            m = mult(m, rotate(theta[head2Id], 0, 1, 0));
            m = mult(m, translate(0.0, -0.5 * headHeight, 0.0));
            figure[headId] = createNode(m, head, leftUpperArmId, null);
            break;

        case middle1Id:
        case middle2Id:
        case middle3Id:
            m = translate(-(torsoWidth + upperArmWidth), 0.9 * torsoHeight, 0.0);
            m = mult(m, rotate(theta[leftUpperArmId], 1, 0, 0));
            figure[leftUpperArmId] = createNode(m, leftUpperArm, rightUpperArmId, leftLowerArmId);
            break;

        case ring1Id:
        case ring2Id:
        case ring3Id:
            m = translate(torsoWidth + upperArmWidth, 0.9 * torsoHeight, 0.0);
            m = mult(m, rotate(theta[rightUpperArmId], 1, 0, 0));
            figure[rightUpperArmId] = createNode(m, rightUpperArm, leftUpperLegId, rightLowerArmId);
            break;

        case pinky1Id:
        case pinky2Id:
        case pinky3Id:
            m = translate(-(torsoWidth + upperLegWidth), 0.1 * upperLegHeight, 0.0);
            m = mult(m, rotate(theta[leftUpperLegId], 1, 0, 0));
            figure[leftUpperLegId] = createNode(m, leftUpperLeg, rightUpperLegId, leftLowerLegId);
            break;

        case thumb1Id:
        case thumb2Id:
            m = translate(0.0, upperLegHeight, 0.0);
            m = mult(m, rotate(theta[rightLowerLegId], 1, 0, 0));
            figure[rightLowerLegId] = createNode(m, rightLowerLeg, null, null);
            break;
    }

}

function traverse(Id) {

    if (Id == null) return;
    stack.push(modelViewMatrix);
    modelViewMatrix = mult(modelViewMatrix, figure[Id].transform);
    figure[Id].render();
    if (figure[Id].child != null) traverse(figure[Id].child);
    modelViewMatrix = stack.pop();
    if (figure[Id].sibling != null) traverse(figure[Id].sibling);
}


// Array of rotation angles (in degrees) for each rotation axis

var Base = 0;
var LowerArm = 1;
var MiddleArm = 2;
var UpperArm = 3;


var theta = [0, 0, 0, 0];

var angle = 0;

var modelViewMatrixLoc;

var vBuffer, cBuffer;

//----------------------------------------------------------------------------

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

//____________________________________________

// Remmove when scale in MV.js supports scale matrices

function scale4(a, b, c) {
    var result = mat4();
    result[0][0] = a;
    result[1][1] = b;
    result[2][2] = c;
    return result;
}


//--------------------------------------------------


window.onload = function init() {

    canvas = document.getElementById("gl-canvas");

    gl = WebGLUtils.setupWebGL(canvas);
    if (!gl) {
        alert("WebGL isn't available");
    }

    gl.viewport(0, 0, canvas.width, canvas.height);

    gl.clearColor(1.0, 1.0, 1.0, 1.0);
    gl.enable(gl.DEPTH_TEST);

    //
    //  Load shaders and initialize attribute buffers
    //
    program = initShaders(gl, "vertex-shader", "fragment-shader");

    gl.useProgram(program);
    modelViewMatrix = mat4();

    colorCube();

    // Load shaders and use the resulting shader program

    program = initShaders(gl, "vertex-shader", "fragment-shader");
    gl.useProgram(program);

    // Create and initialize  buffer objects

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
}

//----------------------------------------------------------------------------


function base() {
    var s = scale4(BASE_WIDTH, BASE_HEIGHT, BASE_WIDTH);
    var instanceMatrix = mult(translate(5.0, 0.5 * BASE_HEIGHT, 0.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

//----------------------------------------------------------------------------


function upperArm() {
    var s = scale4(UPPER_ARM_WIDTH, UPPER_ARM_HEIGHT, UPPER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * UPPER_ARM_HEIGHT, -1.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function upperArm1() {
    var s = scale4(UPPER_ARM_WIDTH, UPPER_ARM_HEIGHT, UPPER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * UPPER_ARM_HEIGHT, 2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function upperArm2() {
    var s = scale4(UPPER_ARM_WIDTH, UPPER_ARM_HEIGHT, UPPER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * UPPER_ARM_HEIGHT, -2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function upperArm3() {
    var s = scale4(UPPER_ARM_WIDTH, UPPER_ARM_HEIGHT, UPPER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * UPPER_ARM_HEIGHT, 1.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

//----------------------------------------------------------------------------


function middleArm() {
    var s = scale4(MIDDLE_ARM_WIDHT, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDHT);
    var instanceMatrix = mult(translate(0.0, 0.5 * MIDDLE_ARM_HEIGHT, -1.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function middleArm1() {
    var s = scale4(MIDDLE_ARM_WIDHT, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDHT);
    var instanceMatrix = mult(translate(0.0, 0.5 * MIDDLE_ARM_HEIGHT, 2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function middleArm2() {
    var s = scale4(MIDDLE_ARM_WIDHT, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDHT);
    var instanceMatrix = mult(translate(0.0, 0.5 * MIDDLE_ARM_HEIGHT, -2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function middleArm3() {
    var s = scale4(MIDDLE_ARM_WIDHT, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDHT);
    var instanceMatrix = mult(translate(0.0, 0.5 * MIDDLE_ARM_HEIGHT, 1.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}


//----------------------------------------------------------------------------


function lowerArm() {
    var s = scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH);
    var r = rotate(0, 1, 0, 0);
    var t = translate(0.0, 0.5 * LOWER_ARM_HEIGHT, -1.0);
    var instanceMatrix = mult(r, mult(t, s));
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function lowerArm1() {
    var s = scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * LOWER_ARM_HEIGHT, 2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function lowerArm2() {
    var s = scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * LOWER_ARM_HEIGHT, -2.75), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function lowerArm3() {
    var s = scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH);
    var instanceMatrix = mult(translate(0.0, 0.5 * LOWER_ARM_HEIGHT, 1.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function lowerThumb() {
    var s = scale4(LOWER_ARM_WIDTH, LOWER_ARM_HEIGHT, LOWER_ARM_WIDTH);
    var r = rotate(45, 1, 0, 0);
    // var t = translate( 0.0, 0.5 * LOWER_ARM_HEIGHT, -1.0 );
    var t = translate(0.0, 0.7 * LOWER_ARM_HEIGHT, 3.0);
    var instanceMatrix = mult(r, mult(t, s));

    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}


//----------------------------------------------------------------------------
var render = function() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    traverse(palmId);

    /*
    modelViewMatrix = rotate(90, 0, 1, 0 );
    base();
    // mvPushMatrix();

    var rot = rotate(-2*theta[LowerArm], 0, 1, 0);
    var stack_modelViewMatrix = modelViewMatrix;

    // modelViewMatrix = mult(modelViewMatrix, translate(0, up, right));
    modelViewMatrix = mult(modelViewMatrix, rot);
    lowerThumb();

    modelViewMatrix = stack_modelViewMatrix

    modelViewMatrix = mult(modelViewMatrix, translate(0.0, BASE_HEIGHT, 0.0));
    modelViewMatrix = mult(modelViewMatrix, rotate(theta[LowerArm], 0, 0, 1 ));

    modelViewMatrix = mult(modelViewMatrix, rotate(-10, 1, 0, 0 ));
    lowerArm();
    modelViewMatrix = mult(modelViewMatrix, rotate(-10, 1, 0, 0 ));
    // modelViewMatrix = mult(modelViewMatrix, rotate(10, 0, 1, 0 ));
    lowerArm1();
    // modelViewMatrix = mult(modelViewMatrix, rotate(10, 0, 1, 0 ));
    lowerArm2();
    // modelViewMatrix = mult(modelViewMatrix, rotate(10, 0, 1, 0 ));
    lowerArm3();
     
    modelViewMatrix = mult(modelViewMatrix, translate(0.0, LOWER_ARM_HEIGHT, 0.0));
    modelViewMatrix = mult(modelViewMatrix, rotate(theta[MiddleArm], 0, 0, 1 ));
    middleArm();
   	middleArm1();
	middleArm2();
	middleArm3();
    // upperThumb();
	
    modelViewMatrix  = mult(modelViewMatrix, translate(0.0, MIDDLE_ARM_HEIGHT, 0.0));
    modelViewMatrix  = mult(modelViewMatrix, rotate(theta[UpperArm], 0, 0, 1) );
    upperArm();
	upperArm1();
	upperArm2();
	upperArm3();

    */
    requestAnimFrame(render);
}

function upperThumb() {
    var s = scale4(MIDDLE_ARM_WIDHT, MIDDLE_ARM_HEIGHT, MIDDLE_ARM_WIDHT);
    // var instanceMatrix = mult(translate( -1.0, 0.7 * MIDDLE_ARM_HEIGHT, 9.0 ),s);
    var instanceMatrix = mult(translate(-1.0, 0.0, -1.5, 9.0), s);
    var t = mult(modelViewMatrix, instanceMatrix);
    gl.uniformMatrix4fv(modelViewMatrixLoc, false, flatten(t));
    gl.drawArrays(gl.TRIANGLES, 0, NumVertices);
}

function spettacolino(decade) {
    // console.log("spettacolino", decade)
    theta[0] = decade;
    theta[1] = decade;
    theta[2] = decade;
    theta[3] = 1.0;
    if (decade < 110) {
        setTimeout(function() {
            spettacolino(decade + 1)
        }, 40);
    }
    /* else {
            theta[0] = 0;
            theta[1] = 0;
            theta[2] = 0;
            theta[3] = 1.0;
       }*/
}
