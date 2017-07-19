/**
 * Created by awok on 18/07/17.
 */
function start_game(files) {
    window.audio.pause();
    window.audio = new Audio('Chop_Suey_8 Bit.mp3');
    window.audio.play();
    // var file_types = [ "pdf", "py", "html", "js", "ppt", "img", "mp3", "mp4", "zip", "unk", ];
    var file_types = ["img", "pdf", "unk"];

    if (window.use_colors) {
        window.config = {};
        window.config['textures'] = {};

        for(var idx = 0; idx < file_types.length; ++idx){
            var html_name = file_types[idx];
            var extension = html_name;
            if(html_name === "unk") extension = "*";
            var e = document.getElementById( html_name + "Color");
            window.config['textures'][extension] = {
                'colors': eval(e.options[e.selectedIndex].value),
            };
        }
    } else {
        window.config = {
            'textures': {
                'pdf': 'pdf.jpg',
                'py': 'python.jpg',
                'html': 'html.jpg',
                'js': 'js.jpg',
                'ppt': 'ppt.jpg',
                '*': 'qmark.jpg',
                'txt': 'txt.jpg',
                'png': 'jpg.jpg',
                'jpg': 'jpg.jpg',
                'mp3': 'audio.jpg',
                'mp4': 'video.jpg',
                'mkv': 'video.jpg',
                'zip': 'zip.jpg'
            }
        }
    }
    if(files){
        buildTreeFromPathList(files, true);

    } else
        buildTreeFromPathList([
            "robotics/Robotics1_15.09.11.mkv",
            "robotics/Robotics1_16.06.06.mp3",
            "robotics/Robotics1_15.02.06_long.py",
            "robotics/notes.mp4",
            "robotics/Robotics - Modelling, Planning and Control.zip",
            "robotics/07_PositionOrientation.png",
            "robotics/09_DirectKinematics.jpg",
            "robotics/printme.js",
            "robotics/08_EulerRPYHomogeneous.ppt",
            "robotics/notes.html",
            //"robotics/general",
            "robotics/slides/16_DynamicControlSingleAxis.pdf",
            "robotics/slides/13_TrajectoryPlanningJoints.pdf",
            "robotics/slides/15_KinematicControl.pdf",
            "robotics/slides/10_InverseKinematics.pdf",
            "robotics/slides/14_TrajectoryPlanningCartesian.pdf",
            "robotics/slides/11_DifferentialKinematics.pdf",
            "robotics/slides/12_InverseDiffKinStatics.pdf",
            "robotics/exams/Robotics1_16.01.11.pdf"
        ], true)

    document.getElementsByTagName('canvas')[0].style['display'] = 'block';
    document.getElementsByTagName('body')[0].style['overflow'] = 'hidden';

    document.getElementById('screen').style['display'] = 'none';
    document.getElementById('outer').style['display'] = 'none';
}
function hide_colors() {
    window.use_colors = false;
    var els = document.getElementsByClassName('colorChoice');
    for (var index = 0; index < els.length; ++index) {
        els[index].style['display'] = 'none';
    }
}
function show_colors() {
    window.use_colors = true;
    var els = document.getElementsByClassName('colorChoice');
    for (var index = 0; index < els.length; ++index) {
        els[index].style['display'] = 'block';
    }
}
function move_one_char(){
    var output = document.getElementById("real_output");
    if(output === null) setTimeout(move_one_char, 100);

    var buffer = document.getElementById("buffer");
    var next_char = window.final_output[0];
    if(!next_char){ return; }

    if(next_char === "\n"){
        window.output_buffer += window.print_buffer + "\n";
        output.innerHTML = window.output_buffer;
        buffer.innerHTML = "";
        window.print_buffer = "";
    } else {
        buffer.innerHTML += next_char;
        window.print_buffer += next_char;
    }
    window.final_output = window.final_output.substring(1, window.final_output.length);
    setTimeout(move_one_char, 2)
}
setTimeout(function(){
    window.print_buffer = "";
    window.output_buffer = "";
    window.final_output = document.getElementById("finalOutput").innerHTML;
    move_one_char();
}, 1000);

function select_folder() {
    document.getElementById('path_selector').click();
}
window.audio = new Audio('geomDash.mp3');
window.audio.play();
