"use strict";

var canvas;
var gl;

var numVertices = 36;

var texSize = 256;
var numChecks = 16;

var program;

var texture1;
var texture2;
var texture3;
var texture4;

var t1;
var t2;

var c;

var R1;
var R2;
var R3;

var flag = false;
var lightD = false;
var lightP = false;
var lightS = false;
var shininess = 10.0;
var CF = 0.85;
var alpha = 2.0;
var Gourad = true;
var cut_off = 0.85;
var lightDir;
var lightPos;
var lightSpot;
var materialShininess;
var GP;



var image1 = new Uint8Array(4 * texSize * texSize);

// Create a checkerboard pattern

for (var i = 0; i < texSize; i++) {
    for (var j = 0; j < texSize; j++) {
        var patchx = Math.floor(i / (texSize / numChecks));
        var patchy = Math.floor(j / (texSize / numChecks));
        if (patchx % 2 ^ patchy % 2) c = 255;
        else c = 0;
        //c = 255*(((i & 0x8) == 0) ^ ((j & 0x8)  == 0))
        image1[4 * i * texSize + 4 * j] = c;
        image1[4 * i * texSize + 4 * j + 1] = c;
        image1[4 * i * texSize + 4 * j + 2] = c;
        image1[4 * i * texSize + 4 * j + 3] = 255;
    }
}


var image2 = new Uint8Array(4 * texSize * texSize);

for (var i = 0; i < texSize; i++) {
    for (var j = 0; j < texSize; j++) {

        image2[4 * i * texSize + 4 * j] = 127 + 127 * Math.sin(0.1 * i * j);
        image2[4 * i * texSize + 4 * j + 1] = 127 + 127 * Math.sin(0.1 * i * j);
        image2[4 * i * texSize + 4 * j + 2] = 127 + 127 * Math.sin(0.1 * i * j);
        image2[4 * i * texSize + 4 * j + 3] = 255;
    }
}

var image3 = new Uint8Array(4 * texSize * texSize);

R1 = Math.floor(Math.random() * 128);
R2 = Math.floor(Math.random() * 128);
R3 = Math.floor(Math.random() * 128);

for (var i = 0; i < texSize; i++) {
    for (var j = 0; j < texSize; j++) {

        image3[4 * i * texSize + 4 * j] = R1; //R1 + R1*Math.sin(0.1*i*j);
        image3[4 * i * texSize + 4 * j + 1] = R2; //R2 + R2*Math.sin(0.1*i*j);
        image3[4 * i * texSize + 4 * j + 2] = R3; //R3 + R3*Math.sin(0.1*i*j);
        image3[4 * i * texSize + 4 * j + 3] = 255;
    }
}


var pointsArray = [];
var colorsArray = [];
var texCoordsArray = [];
var normalsArray = [];

var texCoord = [
    vec2(0, 0),
    vec2(0, 1),
    vec2(1, 1),
    vec2(1, 0)
];

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

var vertexColors = [
    vec4(0.0, 0.0, 0.0, 1.0), // black
    vec4(1.0, 0.0, 0.0, 1.0), // red
    vec4(1.0, 1.0, 0.0, 1.0), // yellow
    vec4(0.0, 1.0, 0.0, 1.0), // green
    vec4(0.0, 0.0, 1.0, 1.0), // blue
    vec4(1.0, 0.0, 1.0, 1.0), // magenta
    vec4(0.0, 1.0, 1.0, 1.0), // white
    vec4(0.0, 1.0, 1.0, 1.0) // cyan
];

//Directions for lights

var lightDirectionDir = vec3(-1.0, 0.0, 0.0);
var lightDirectionSpot = vec3(1.3, -1.3, -0.1);

//Positions for lights

var lightPositionPos = vec4(0.0, 3.0, 0.0, 1.0);
var lightPositionSpot = vec4(-1.5, 1.5, 0.2, 1.0);


//Costants for attenuation
var C = 1.0;
var B = 0.2;
var A = 0.1;


var lightAmbient = vec4(0.2, 0.2, 0.2, 1.0);

var lightDiffuseD = vec4(1.0, 1.0, 1.0, 1.0);
var lightSpecularD = vec4(1.0, 1.0, 1.0, 1.0);

var lightDiffuseP = vec4(1.0, 1.0, 1.0, 1.0);
var lightSpecularP = vec4(1.0, 1.0, 1.0, 1.0);

var lightDiffuseS = vec4(1.0, 1.0, 1.0, 1.0);
var lightSpecularS = vec4(1.0, 1.0, 1.0, 1.0);

var materialAmbient = vec4(1.0, 1.0, 1.0, 1.0);
var materialDiffuse = vec4(1.0, 1.0, 1.0, 1.0);
var materialSpecular = vec4(1.0, 1.0, 1.0, 1.0);

var modelView;
var projection;


var xAxis = 0;
var yAxis = 1;
var zAxis = 2;
var axis = xAxis;

var theta = [45.0, 45.0, 45.0];


function configureTexture() {

    texture1 = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture1);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, texSize, texSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, image1);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER,
        gl.NEAREST_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    texture2 = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture2);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, texSize, texSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, image2);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER,
        gl.NEAREST_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    texture3 = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture3);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, texSize, texSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, image3);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER,
        gl.NEAREST_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);


}

function quad(a, b, c, d) {

    var t1 = subtract(vertices[b], vertices[a]);
    var t2 = subtract(vertices[c], vertices[b]);
    var normal = cross(t1, t2);
    var normal = vec3(normal);
    normal = normalize(normal);

    pointsArray.push(vertices[a]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[0]);
    normalsArray.push(normal);

    pointsArray.push(vertices[b]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[1]);
    normalsArray.push(normal);

    pointsArray.push(vertices[c]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[2]);
    normalsArray.push(normal);

    pointsArray.push(vertices[a]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[0]);
    normalsArray.push(normal);

    pointsArray.push(vertices[c]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[2]);
    normalsArray.push(normal);

    pointsArray.push(vertices[d]);
    colorsArray.push(vertexColors[a]);
    texCoordsArray.push(texCoord[3]);
    normalsArray.push(normal);

}

function colorCube() {
    quad(1, 0, 3, 2);
    quad(2, 3, 7, 6);
    quad(3, 0, 4, 7);
    quad(6, 5, 1, 2);
    quad(4, 5, 6, 7);
    quad(5, 4, 0, 1);
}


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

    lightDir = gl.getUniformLocation(program, "lightD");
    lightPos = gl.getUniformLocation(program, "lightP");
    lightSpot = gl.getUniformLocation(program, "lightS");
    GP = gl.getUniformLocation(program, "Gourad");
    materialShininess = gl.getUniformLocation(program, "shininess")
    CF = gl.getUniformLocation(program, "cut_off");

    configureTexture();

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, texture1);
    gl.uniform1i(gl.getUniformLocation(program, "Tex0"), 0);

    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, texture2);
    gl.uniform1i(gl.getUniformLocation(program, "Tex1"), 1);

    gl.activeTexture(gl.TEXTURE2);
    gl.bindTexture(gl.TEXTURE_2D, texture3);
    gl.uniform1i(gl.getUniformLocation(program, "Tex2"), 2);

    colorCube();

    var nBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, nBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, flatten(normalsArray), gl.STATIC_DRAW);

    var vNormal = gl.getAttribLocation(program, "vNormal");
    gl.vertexAttribPointer(vNormal, 3, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(vNormal);

    var cBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, cBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, flatten(colorsArray), gl.STATIC_DRAW);

    var vColor = gl.getAttribLocation(program, "vColor");
    gl.vertexAttribPointer(vColor, 4, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(vColor);

    var vBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, flatten(pointsArray), gl.STATIC_DRAW);

    var vPosition = gl.getAttribLocation(program, "vPosition");
    gl.vertexAttribPointer(vPosition, 4, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(vPosition);

    var tBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, tBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, flatten(texCoordsArray), gl.STATIC_DRAW);

    var vTexCoord = gl.getAttribLocation(program, "vTexCoord");
    gl.vertexAttribPointer(vTexCoord, 2, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(vTexCoord);


    projection = ortho(-1, 1, -1, 1, -100, 100);

    var ambientProduct = mult(lightAmbient, materialAmbient);
    var diffuseProductD = mult(lightDiffuseD, materialDiffuse);
    var specularProductD = mult(lightSpecularD, materialSpecular);

    var diffuseProductP = mult(lightDiffuseP, materialDiffuse);
    var specularProductP = mult(lightSpecularP, materialSpecular);

    var diffuseProductS = mult(lightDiffuseS, materialDiffuse);
    var specularProductS = mult(lightSpecularS, materialSpecular);


    document.getElementById("ButtonX").onclick = function() {
        axis = xAxis;
    };
    document.getElementById("ButtonY").onclick = function() {
        axis = yAxis;
    };
    document.getElementById("ButtonZ").onclick = function() {
        axis = zAxis;
    };
    document.getElementById("ButtonT").onclick = function() {
        flag = !flag;
    };
    document.getElementById("ButtonLightD").onclick = function() {
        lightD = !lightD;
    };
    document.getElementById("ButtonLightP").onclick = function() {
        lightP = !lightP;
    };
    document.getElementById("ButtonLightS").onclick = function() {
        lightS = !lightS;
    };
    document.getElementById("ButtonGP").onclick = function() {
        Gourad = !Gourad;
    };
    document.getElementById("Shininess_plus").onclick = function() {
        shininess += 2.0;
    };
    document.getElementById("Shininess_minus").onclick = function() {
        shininess -= 2.0;
    };
    document.getElementById("CF_plus").onclick = function() {
        cut_off += 0.01;
    };
    document.getElementById("CF_minus").onclick = function() {
        cut_off -= 0.01;
    };


    gl.uniform4fv(gl.getUniformLocation(program, "ambientProduct"), flatten(ambientProduct));
    gl.uniform4fv(gl.getUniformLocation(program, "diffuseProductD"), flatten(diffuseProductD));
    gl.uniform4fv(gl.getUniformLocation(program, "specularProductD"), flatten(specularProductD));
    gl.uniform4fv(gl.getUniformLocation(program, "diffuseProductP"), flatten(diffuseProductP));
    gl.uniform4fv(gl.getUniformLocation(program, "specularProductP"), flatten(specularProductP));
    gl.uniform4fv(gl.getUniformLocation(program, "diffuseProductS"), flatten(diffuseProductS));
    gl.uniform4fv(gl.getUniformLocation(program, "specularProductS"), flatten(specularProductS));

    gl.uniform3fv(gl.getUniformLocation(program, "lightDirectionDir"), flatten(lightDirectionDir));

    gl.uniform4fv(gl.getUniformLocation(program, "lightPositionPos"), flatten(lightPositionPos));

    gl.uniform3fv(gl.getUniformLocation(program, "lightDirectionSpot"), flatten(lightDirectionSpot));
    gl.uniform4fv(gl.getUniformLocation(program, "lightPositionSpot"), flatten(lightPositionSpot));

    gl.uniform1f(gl.getUniformLocation(program, "alpha"), alpha);
    gl.uniform1f(gl.getUniformLocation(program, "C"), C);
    gl.uniform1f(gl.getUniformLocation(program, "B"), B);
    gl.uniform1f(gl.getUniformLocation(program, "A"), A);
    //gl.uniform1f(gl.getUniformLocation(program,"cut_off"),cut_off);

    gl.uniformMatrix4fv(gl.getUniformLocation(program, "projectionMatrix"), false, flatten(projection));

    render();
}

var render = function() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    if (flag) theta[axis] += 1.0;

    gl.uniform1i(lightDir, lightD);
    gl.uniform1i(lightPos, lightP);
    gl.uniform1i(lightSpot, lightS);
    gl.uniform1i(GP, Gourad);
    gl.uniform1f(materialShininess, shininess);
    gl.uniform1f(CF, cut_off);

    modelView = mat4();
    modelView = mult(modelView, rotate(theta[xAxis], [1, 0, 0]));
    modelView = mult(modelView, rotate(theta[yAxis], [0, 1, 0]));
    modelView = mult(modelView, rotate(theta[zAxis], [0, 0, 1]));


    gl.uniformMatrix4fv(gl.getUniformLocation(program, "modelViewMatrix"), false, flatten(modelView));

    gl.drawArrays(gl.TRIANGLES, 0, numVertices);
    requestAnimFrame(render);
}
