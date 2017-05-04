"use strict";
var die = "dead";
var run_next;

var canvas;
var gl;
var program;

// cube structure
var numVertices  = 36;
var texSize = 256;
var numChecks = 8;

var flag = true;
var vertexLight = false;

// cube texture
var texture1, texture2;

// var t1, t2;
var normalsArray = [];
var viewerPos;
var modelViewMatrix, projection;

var useDirectionalLight = true;
var usePointLight = true;
var useSpotLight = true;

var directionalLightLocation = vec4(-1.0, -1.0, -1.0, 0.0);
var pointLightLocation =       vec4(1.0, 1.0, 1.0, 1.0);
var spotLightLocation =        vec4(1.0, 1.0, 1.0, 1.0);
var spotLightNormal =          vec4(1.0, 1.0, 1.0, 1.0);

var lightAmbient = vec4(  1.0, 1.0, 1.0, 1.0 );
var lightDiffuse = vec4(  1.0, 1.0, 1.0, 1.0 );
var lightSpecular = vec4( 1.0, 1.0, 1.0, 1.0 );


// should match the terms in light model
var materialAmbient = vec4( 1.0, 1.0, 1.0, 1.0 );
var materialDiffuse = vec4( 1.0, 1.0, 1.0, 1.0 );
var materialSpecular = vec4( 1.0, 1.0, 1.0, 1.0 );
var materialShininess = 100.0;

// POINT 4
var emission = vec4(0.0, 0.3, 0.3, 1.0);

var attenuationConstant = 0.1;
var attenuationLinear = 0.1;
var attenuationQuadratic = 0.1;

var c;

// draw textures
var image1 = new Uint8Array(4*texSize*texSize);
for ( var i = 0; i < texSize; i++ ) {
    for ( var j = 0; j <texSize; j++ ) {
        var patchx = Math.floor(i/(texSize/numChecks));
        var patchy = Math.floor(j/(texSize/numChecks));
        if(patchx%2 ^ patchy%2) c = 255;
        else c = 0;
        //c = 255*(((i & 0x8) == 0) ^ ((j & 0x8)  == 0))
        image1[4*i*texSize+4*j] = c;
        image1[4*i*texSize+4*j+1] = c;
        image1[4*i*texSize+4*j+2] = c;
        image1[4*i*texSize+4*j+3] = 255;
    }
}

var image2 = new Uint8Array(4*texSize*texSize);
// Create a checkerboard pattern
for ( var i = 0; i < texSize; i++ ) {
    for ( var j = 0; j <texSize; j++ ) {
        image2[4*i*texSize+4*j] = 127+127*Math.sin(0.1*i*j);
        image2[4*i*texSize+4*j+1] = 127+127*Math.sin(0.1*i*j);
        image2[4*i*texSize+4*j+2] = 127+127*Math.sin(0.1*i*j);
        image2[4*i*texSize+4*j+3] = 255;
       }
}

var pointsArray = [];
var colorsArray = [];
var texCoordsArray = [];

var texCoord = [
    vec2(0, 0),
    vec2(0, 1),
    vec2(1, 1),
    vec2(1, 0)
];

var vertices = [
    vec4( -0.5, -0.5,  0.5, 1.0 ),
    vec4( -0.5,  0.5,  0.5, 1.0 ),
    vec4( 0.5,  0.5,  0.5, 1.0 ),
    vec4( 0.5, -0.5,  0.5, 1.0 ),
    vec4( -0.5, -0.5, -0.5, 1.0 ),
    vec4( -0.5,  0.5, -0.5, 1.0 ),
    vec4( 0.5,  0.5, -0.5, 1.0 ),
    vec4( 0.5, -0.5, -0.5, 1.0 )
];
 
var vertexColors = [
    vec4( 0.0, 0.0, 0.0, 1.0 ),  // black
    vec4( 1.0, 0.0, 0.0, 1.0 ),  // red
    vec4( 1.0, 1.0, 0.0, 1.0 ),  // yellow
    vec4( 0.0, 1.0, 0.0, 1.0 ),  // green
    vec4( 0.0, 0.0, 1.0, 1.0 ),  // blue
    vec4( 1.0, 0.0, 1.0, 1.0 ),  // magenta
    vec4( 0.0, 1.0, 1.0, 1.0 ),  // white
    vec4( 0.0, 1.0, 1.0, 1.0 )   // cyan
];

var xAxis = 0;
var yAxis = 1;
var zAxis = 2;
var axis = xAxis;

var theta = [45.0, 45.0, 45.0];

var thetaLoc;

function configureTexture() {
    texture1 = gl.createTexture();
    gl.bindTexture( gl.TEXTURE_2D, texture1 );
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, texSize, texSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, image1);
    gl.generateMipmap( gl.TEXTURE_2D );
    gl.texParameteri( gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST_MIPMAP_LINEAR );
    gl.texParameteri( gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    texture2 = gl.createTexture();
    gl.bindTexture( gl.TEXTURE_2D, texture2 );
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, texSize, texSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, image2);
    gl.generateMipmap( gl.TEXTURE_2D );
    gl.texParameteri( gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST_MIPMAP_LINEAR );
    gl.texParameteri( gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
}

function quad(a, b, c, d) {
     var t1 = subtract(vertices[b], vertices[a]);
     var t2 = subtract(vertices[c], vertices[b]);
     var normal = cross(t1, t2);
     normal = vec3(normal);
     normal = normalize(normal);

     normalsArray.push(normal);
     normalsArray.push(normal);
     normalsArray.push(normal);
     normalsArray.push(normal);
     normalsArray.push(normal);
     normalsArray.push(normal);

     pointsArray.push(vertices[a]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[0]);
     
     pointsArray.push(vertices[b]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[1]);


     pointsArray.push(vertices[c]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[2]);

     pointsArray.push(vertices[a]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[0]);

     pointsArray.push(vertices[c]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[2]);

     pointsArray.push(vertices[d]);
     colorsArray.push(vertexColors[a]);
     texCoordsArray.push(texCoord[3]);
}

function colorCube()
{
    quad( 1, 0, 3, 2 );
    quad( 2, 3, 7, 6 );
    quad( 3, 0, 4, 7 );
    quad( 6, 5, 1, 2 );
    quad( 4, 5, 6, 7 );
    quad( 5, 4, 0, 1 );
}

canvas = document.getElementById("gl-canvas");
gl = WebGLUtils.setupWebGL( canvas );
if ( !gl ) { alert( "WebGL isn't available" ); }
gl.viewport( 0, 0, canvas.width, canvas.height );
gl.clearColor( 1.0, 1.0, 1.0, 1.0 );

gl.enable(gl.DEPTH_TEST);
colorCube();

function main(light_mode) {
    program = initShaders( gl, light_mode  + "-vertex-shader", light_mode + "-fragment-shader" );
    gl.useProgram( program );

    var nBuffer = gl.createBuffer();
    gl.bindBuffer( gl.ARRAY_BUFFER, nBuffer );
    gl.bufferData( gl.ARRAY_BUFFER, flatten(normalsArray), gl.STATIC_DRAW );

    var vertexNormal = gl.getAttribLocation( program, "vertexNormal" );
    gl.vertexAttribPointer( vertexNormal, 3, gl.FLOAT, false, 0, 0 );
    gl.enableVertexAttribArray( vertexNormal );

    viewerPos = vec3(0.0, 0.0, -20.0 );

    var ambientLight = mult(lightAmbient, materialAmbient);
    var diffuseLight = mult(lightDiffuse, materialDiffuse);
    var specularLight = mult(lightSpecular, materialSpecular);

    gl.uniform4fv(gl.getUniformLocation(program, "ambientLight"), flatten(ambientLight));
    gl.uniform4fv(gl.getUniformLocation(program, "diffuseLight"), flatten(diffuseLight) );
    gl.uniform4fv(gl.getUniformLocation(program, "specularLight"), flatten(specularLight) );
    gl.uniform4fv(gl.getUniformLocation(program, "directionalLightLocation"), flatten(directionalLightLocation));
    gl.uniform4fv(gl.getUniformLocation(program, "pointLightLocation"), flatten(pointLightLocation) );
    gl.uniform1f(gl.getUniformLocation(program, "shininess"),materialShininess);
    
    // initialize view position
    projection = ortho(-1, 1, -1, 1, -100, 100);
    gl.uniformMatrix4fv( gl.getUniformLocation(program, "projectionMatrix"), false, flatten(projection));

    // --< homework
    
    //
    // color the cube
    //

    var colorBuffer = gl.createBuffer();
    gl.bindBuffer( gl.ARRAY_BUFFER, colorBuffer );
    // fill the buffer with colorsArray
    gl.bufferData( gl.ARRAY_BUFFER, flatten(colorsArray), gl.STATIC_DRAW );

    // get a reference for color array
    var vertexColor = gl.getAttribLocation( program, "vertexColor" );
    gl.vertexAttribPointer( vertexColor, 4, gl.FLOAT, false, 0, 0 );
    gl.enableVertexAttribArray( vertexColor );

    //
    // draw cube
    //
    var vertexBuffer = gl.createBuffer(); // allocate js obj
    gl.bindBuffer( gl.ARRAY_BUFFER, vertexBuffer ); // allocate gpu obj
    gl.bufferData( gl.ARRAY_BUFFER, flatten(pointsArray), gl.STATIC_DRAW ); // load data into gpu

    // link out shader variables with our data buffer
    var vertexPosition = gl.getAttribLocation( program, "vertexPosition" );
    gl.vertexAttribPointer( vertexPosition, 4, gl.FLOAT, false, 0, 0 );
    gl.enableVertexAttribArray( vertexPosition );


    //
    // texture position
    //
    var tBuffer = gl.createBuffer();
    gl.bindBuffer( gl.ARRAY_BUFFER, tBuffer);
    gl.bufferData( gl.ARRAY_BUFFER, flatten(texCoordsArray), gl.STATIC_DRAW );

    var vertexTexturesCoord = gl.getAttribLocation( program, "vertexTextureCoord" );
    gl.vertexAttribPointer( vertexTexturesCoord , 2, gl.FLOAT, false, 0, 0 );
    gl.enableVertexAttribArray( vertexTexturesCoord );

    configureTexture();

    // 
    // texture colors
    //
    gl.activeTexture( gl.TEXTURE0 );
    gl.bindTexture( gl.TEXTURE_2D, texture1 );
    gl.uniform1i(gl.getUniformLocation( program, "Texture0"), 0);

    // draw wave texture
    gl.activeTexture( gl.TEXTURE1 );
    gl.bindTexture( gl.TEXTURE_2D, texture2 );
    gl.uniform1i(gl.getUniformLocation( program, "Texture1"), 1);

    render();
}

var render = function() {
    gl.clear( gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    if(flag)
        theta[axis] += 2.0;
    // gl.uniform3fv(thetaPointer, theta); // *thetaPointer = theta

    modelViewMatrix = mat4();
    modelViewMatrix = mult(modelViewMatrix, rotate(theta[xAxis], [1, 0, 0] ));
    modelViewMatrix = mult(modelViewMatrix, rotate(theta[yAxis], [0, 1, 0] ));
    modelViewMatrix = mult(modelViewMatrix, rotate(theta[zAxis], [0, 0, 1] ));

    normalMatrix = [
        vec3(modelViewMatrix[0][0], modelViewMatrix[0][1], modelViewMatrix[0][2]),
        vec3(modelViewMatrix[1][0], modelViewMatrix[1][1], modelViewMatrix[1][2]),
        vec3(modelViewMatrix[2][0], modelViewMatrix[2][1], modelViewMatrix[2][2])
    ];
    gl.uniformMatrix4fv(gl.getUniformLocation(program,"projectionMatrix"), false, flatten(projection) );
    gl.uniformMatrix3fv(gl.getUniformLocation(program,"normalMatrix"), false, flatten(normalMatrix) );
    gl.uniformMatrix4fv(gl.getUniformLocation(program,"modelViewMatrix"), false, flatten(modelViewMatrix));
    gl.uniform1f(gl.getUniformLocation(program, "shininess"),materialShininess);
    gl.uniform1f(gl.getUniformLocation(program, "attenuationConstant"), attenuationConstant);
    gl.uniform1f(gl.getUniformLocation(program, "attenuationLinear"), attenuationLinear);
    gl.uniform1f(gl.getUniformLocation(program, "attenuationQuadratic"), attenuationQuadratic);
    gl.uniform1f(gl.getUniformLocation(program, "useDirectionalLight"), useDirectionalLight);
    gl.uniform1f(gl.getUniformLocation(program, "usePointLight"), usePointLight);
    gl.uniform1f(gl.getUniformLocation(program, "useSpotLight"), useSpotLight);
    
    // draw cube
    gl.drawArrays(gl.TRIANGLES, 0, numVertices);

    if(die != "die"){
        requestAnimFrame(render);
    } else {
        die = "dead"
        run_next();
    }
}
window.onload = main("fragment-light");
document.getElementById("ButtonX").onclick = function(){axis = xAxis;};
document.getElementById("ButtonY").onclick = function(){axis = yAxis;};
document.getElementById("ButtonZ").onclick = function(){axis = zAxis;};
document.getElementById("ButtonT").onclick = function(){flag = !flag;};
document.getElementById("ButtonSpotlight").onclick = function(){
    useDirectionalLight = !useDirectionalLight;
};
document.getElementById("ButtonPointLight").onclick = function(){
    usePointLight = !usePointLight;
};
document.getElementById("ButtonDirectionalLight").onclick = function(){
    useSpotLight = !useSpotLight;
};

document.getElementById("ButtonShading").onclick = function(){
    vertexLight = !vertexLight
    if(vertexLight){
        run_next = function() {main("vertex-light")};
    }
    else{
        run_next = function() {main("fragment-light")};
    }
    die = "die";
};
