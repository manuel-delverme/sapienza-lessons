window.onresize = function () {
     if (this.fsnRender) {
         this.fsnRender.canvas.width = window.innerWidth;
         this.fsnRender.canvas.height = window.innerHeight;
         this.fsnRender.display.changed = true;
     }
};

FSNRender = Klass({
    initialize: function (fsnInstance) {
        this.line_width = 2;
        this.fuckinglookAt = vec3(0, 5, 0);
        this.word_translation = vec3(0, 0, 0);
        this.avatar = null;
        this.avatar_speed = [0, 0, 0, 0];
        this.avatar_moved = false;
        this.setFSN(fsnInstance);
        this.canvas = E.canvas(window.innerWidth, window.innerHeight);
        this.display = new Magi.Scene(this.canvas);
        this.canvas.style.position = 'absolute';
        this.canvas.style.left = '0px';
        this.canvas.style.top = '0px';
        document.body.appendChild(this.canvas);
        this.display.bg = [0.7, 0.7, 0.6, 1];
        this.lightPos = vec4(8000, -2000, -15000, 1);
        this.scene = this.display.scene;
        this.camera = this.display.camera;
        this.camera.zNear = 1;
        this.camera.zFar = 1000;
        this.offset = vec3(0, 10, 180);
        this.lookOffset = vec3(0, 0, -150);
        var grad = new Magi.FilterQuad('bg-frag');
        grad.depthTest = false;
        grad.material.floats.aspect = 4 / 3;

        this.scene.appendChild(grad);
        this.updateLayout();
        this.display.drawOnlyWhenChanged = true;
        var self = this;
        this.scene.addFrameListener(function (t, dt) {
            self.sceneUpdate(t, dt);
        });
        this.camera.afterTransform(function (m) {
            var n = mat4.identity();
            mat4.translate(n, this.position);
            mat4.multiply(n, m, n);
            mat4.set(m, Magi.DefaultMaterial.lightMatrix);
        });
        this.downX = null;
        this.downY = null;

     /* MOUSE HOOKS */
        window.onmouseup = function (ev) {
            if (self.downX !== null) {
                self.downX = null;
                self.downY = null;
                ev.preventDefault();
            }
        };
        this.canvas.onmousedown = function (ev) {
            self.downX = ev.clientX;
            self.downY = ev.clientY;
            ev.preventDefault();
        };
        this.canvas.onmousemove = function (ev) {
            if (self.downX !== null) {
                var dx =self.downX - ev.clientX;
                var dy = ev.clientY - self.downY;
                // dy = Math.max(Math.min(dy,1), -1);
                // dx = Math.max(Math.min(dx,1), -1);
                self.downX = ev.clientX;
                self.downY = ev.clientY;
                if (dx != 0 || dy != 0) {
                    self.fuckinglookAt[0] += dx / 10;
                    self.fuckinglookAt[1] += dy / 15;
                }
                ev.preventDefault();
            }
        };

        function keyDownHandler(event) {
            var speed = 2;
            if (event.keyCode === 39 || event.keyCode === 68) {
                self.avatar_moved = true;
                self.avatar_speed[0] = +speed;
            }
            else if (event.keyCode === 37 || event.keyCode === 65) {
                self.avatar_moved = true;
                self.avatar_speed[1] = -speed;
            }
            else if (event.keyCode === 40 || event.keyCode === 83) {
                self.avatar_moved = true;
                self.avatar_speed[2] = +speed;
            }
            else if (event.keyCode === 38 || event.keyCode === 87) {
                self.avatar_moved = true;
                self.avatar_speed[3] = -speed;
            }
        }

        function keyUpHandler(event) {
            if (event.keyCode === 39 || event.keyCode === 68) {
                self.avatar_speed[0] = 0;
            }
            else if (event.keyCode === 37 || event.keyCode === 65) {
                self.avatar_speed[1] = 0;
            }
            else if (event.keyCode === 40 || event.keyCode === 83) {
                self.avatar_speed[2] = 0;
            }
            else if (event.keyCode === 38 || event.keyCode === 87) {
                self.avatar_speed[3] = 0;
            }
        }

        window.addEventListener('keydown', keyDownHandler, false);
        window.addEventListener('keyup', keyUpHandler, false);
    },

    setFSN: function (fsnInstance) {
        this.fsn = fsnInstance;
        var self = this;
        this.fsn.onRelayoutNeeded = function (entry, full) {
            self.updateLayoutPath(entry.getPath(), full ? null : 1);
        };
    },

    gotoPath: function (path) {
        if (this.objects[path]) {
            this.currentObjectIndex = path;
        }
    },

    updateLayout: function () {
        var layout = this.fsn.getLayout();
        for (var i in this.objects) {
            var cn = this.objects[i];
            this.destroyNode(cn);
        }
        this.objects = {};

        this.addLayout(layout);
    },

    updateLayoutPath: function (path, maxDepth) {
        var layout = this.fsn.getLayout(path, maxDepth);
        var p = this.objects[path];
        var paths = (path === '/') ? path : (path + '/');
        for (var i in this.objects) {
            if (i === path || i.slice(0, paths.length) === paths) {
                var obj = this.objects[i];
                obj.marked = true;
            }
        }
        this.addLayout(layout, p.entry);
        p.marked = false;
        for (var i in this.objects) {
            var obj = this.objects[i];
            if (obj.marked) {
                this.destroyNode(obj);
                delete this.objects[i];
            }
        }
    },

    destroyNode: function (cn) {
        for (var i = 0, len = cn.childNodes.length; i < len; i++) {
            var c = cn.childNodes[i];
            if (c.texture) {
                c.texture.destroy();
            }
        }
        if (cn.parentNode)
            cn.parentNode.removeChild(cn);
    },

    unmark: function (node) {
        node.marked = false;
        for (var i = 0; i < node.childNodes.length; i++) {
            this.unmark(node.childNodes[i]);
        }
    },

    create_connector_line: function (layout_entry, f, node) {
        var dx = layout_entry.offset.x / layout_entry.offset.scale;
        var dy = layout_entry.offset.y / layout_entry.offset.scale + 0.001;
        var dz = layout_entry.offset.z / layout_entry.offset.scale + 25 / layout_entry.offset.scale;
        // var d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        var fs = 40 * f;
        var connectorLine = new Magi.Node();

        var angle = Math.atan2(dz / 2, dx);
        var hypot = Math.sqrt(dx * dx + (dz / 2 * dz / 2)) / fs;
        var filler = 0;
        if (angle !== -Math.PI / 2) {
            var alpha = 0.5 * Math.abs(-Math.PI / 2 - angle);
            filler = 0.1 * Math.tan(alpha);
        }
        hypot += filler;

        // first to the side
        line_width = this.line_width;
        var ramp_width_obj = new Magi.ColorQuad(0, 0, 0, 1);
        ramp_width_obj.setScale(hypot / 2, line_width, 1);
        ramp_width_obj.setX(-hypot / 2);
        var ramp_x_disp = new Magi.Node();
        ramp_x_disp.setAxis(0, 0, 1).setAngle(Math.PI - angle);
        ramp_x_disp.appendChild(ramp_width_obj);
        connectorLine.appendChild(ramp_x_disp);

        // then go down
        var ramp_depth_obj = new Magi.ColorQuad(0, 0, 0, 1);
        var len = Math.abs(dz / fs / 2) + filler;
        ramp_depth_obj.setScale(len / 2, line_width, 1);
        ramp_depth_obj.setX(len / 2);
        var ramp_depth_position = new Magi.Node();
        ramp_depth_position.setAxis(0, 0, 1).setAngle(Math.PI / 2);
        ramp_depth_position.appendChild(ramp_depth_obj);
        ramp_depth_position.setPosition(dx / fs, -dz / 2 / fs - filler, 0);
        connectorLine.appendChild(ramp_depth_position);

        // ascend to the next plane
        var ramp_height_obj = new Magi.ColorQuad(0, 0, 0, 1);
        ramp_height_obj.setScale(dy / fs / 2, line_width, 1);
        // how much it goes up
        ramp_height_obj.setX(-dy / fs / 2);
        ramp_height_obj.setAxis(1, 0, 0).setAngle(-Math.PI / 2);

        var ramp_height_position = new Magi.Node();
        ramp_height_position.appendChild(ramp_height_obj);
        ramp_height_position.setAxis(0, 1, 0).setAngle(Math.PI / 2);

        // angle of approach
        var q3pp = new Magi.Node();
        q3pp.appendChild(ramp_height_position);
        q3pp.setAxis(1, 0, 0).setAngle(-0.1);
        q3pp.setPosition(dx / fs, -dz / fs, 0);
        connectorLine.appendChild(q3pp);

        connectorLine.setAxis(1, 0, 0).setAngle(-Math.PI / 2);
        connectorLine.setPosition(-dx, -dy, -dz + 20 * layout_entry.offset.scale);
        connectorLine.setScale(fs, fs, fs);
        node.connectorLine = connectorLine;
        node.appendChild(connectorLine);
    },
    create_text_mesh: function (fs_node, f, s) {
        var txt = new Magi.Text(fs_node.name, 50, '#fff', 'Arial', true);
        txt.setAlign(txt.leftAlign, txt.topAlign);
        if (fs_node.is_file) {
            txt.setScale(s * (4 / Math.max(320, txt.realWidth)));
            //txt.setAxis(0, 0, 0).setAngle(0);
            txt.setPosition(-3.5 * f * s, -3.2 * f * s, 4.5 * f * s);
            txt.setY(50);
            txt.setZ(3);
        } else {
            txt.setColor('#0f0');
            txt.setScale(s * (3 / Math.max(220, txt.realWidth)));
            txt.setPosition(-1 * s, 0.8 * s, 1.2 * s);
            txt.setZ(-20);
            txt.setY(80);
        }
        return txt;
    },
    create_model: function (fs_node, f, s) {
        var mesh;

        if (fs_node.is_file) {
            var name, file_extention;
            file_extention = fs_node.name.split('.');
            if (file_extention.length > 1) {
                name = file_extention[file_extention.length - 1];
                if (!window.config['textures'][name]) name = '*';
            } else {
                name = "*"
            }

            if (window.config['textures'][name]['colors']) {
                mesh = new Magi.ColorQuad(
                    window.config['textures'][name]['colors'][0],
                    window.config['textures'][name]['colors'][1],
                    window.config['textures'][name]['colors'][2],
                    1
                );
                mesh = new Magi.Cube();
                mesh.material.floats.MaterialEmit = vec4.create( [
                        window.config['textures'][name]['colors'][0],
                        window.config['textures'][name]['colors'][1],
                        window.config['textures'][name]['colors'][2],
                        1]);
            } else {
                var texture_file = window.config['textures'][name];
                if (!texture_file) texture_file = window.config['textures']['*'];
                mesh = new Magi.Cube();
                Magi.Texture.load(texture_file, function (tex) {
                    //mesh.material.textures.SpecTex = tex;
                    mesh.material.textures.EmitTex = tex;
                    //mesh.material.textures.DiffTex = tex;
                });
            }

            mesh.setScale(10 * f * s, 15 * f * s, 7 * f * s);
            mesh.setY(3 * f * s);

        } else {
            var square_size = 5;


            mesh = new Magi.Cube().setScale(square_size * s, 0.05 * s, square_size * s);
            mesh.setY(-mesh.scaling[1] / 2);
            mesh.material.floats.LightPos = this.lightPos;
            mesh.material.floats.MaterialDiffuse = vec4(0.1, 0.1, 0.1, 1);
            mesh.material.floats.MaterialSpecular = vec4(0.5, 0.5, 0.5, 0);
            mesh.material.floats.MaterialEmit = vec4(0.0, 0.0, 0.0, 0);
            mesh.material.floats.LightSpecular = vec4(0.5, 0.5, 0.5, 1);
            mesh.material.floats.LightDiffuse = vec4(0.4, 0.4, 0.4, 1);
            mesh.material.floats.LightAmbient = vec4(0.2, 0.2, 0.2, 1);

            Magi.Texture.load("dir.jpg", function (tex) {
                mesh.material.textures.EmitTex = tex;
            });
        }

        return mesh;
    },
    addLayout: function (layout, root) {
        var self = this;
        for (var j = 0; j < layout.length; j++) {
            var fs_node = layout[j];
            if (root) {
                if (!fs_node.parent && fs_node.name !== '/') {
                    fs_node.offset = root.offset;
                    fs_node.parent = root.parent;
                }
            }
            var i = fs_node.path;

            // var hue = (is_file ? 100 : 180) / 360;
            var rendered_object;
            // if was already rendered and with the right entries
            if (this.objects[i] && typeof this.objects[i].entry.entries === typeof fs_node.entries) {
                rendered_object = this.objects[i];
                if (rendered_object.connectorLine)
                    rendered_object.removeChild(rendered_object.connectorLine);
                rendered_object.reused = true;
                rendered_object.marked = false;
            } else {
                // add a new rendered object
                rendered_object = new Magi.Node();
                this.objects[i] = rendered_object;
            }
            fs_node.node = rendered_object;
            rendered_object.entry = fs_node;

            var x = fs_node.offset.x;
            var y = fs_node.offset.y;
            var z = fs_node.offset.z;

            rendered_object.offset = vec3(x, y, z);
            rendered_object.setPosition(x, y, z);
            rendered_object.setScale(fs_node.offset.scale);

            if (fs_node.is_file) {
                rendered_object.position[1] += 36 * fs_node.offset.scale;
                rendered_object.offset[1] += 36 * fs_node.offset.scale;
            }
            rendered_object.originalPosition = vec3(rendered_object.position);
            rendered_object.upPosition = vec3(rendered_object.position);
            rendered_object.upPosition[1] += fs_node.offset.scale * 0.4 * 20 * 9;
            rendered_object.tmpVec = vec3();
            rendered_object.origY = rendered_object.offset[1];
            if (fs_node.is_file && !rendered_object.reused) {
                rendered_object.addFrameListener(function (t, dt) {
                    if (this.is_exploding) {
                        var model = this.childNodes[0];
                        var text = this.childNodes[1];
                        var ynew;
                        var targetPosition = this.position;
                        targetPosition[1] += 1;

                        model.material.floats.MaterialEmit = vec4(1.0, 0.0, 0.0, 1);
                        model.material.floats.MaterialDiffuse = vec4(1.0, 0.0, 0.0, 0.3);

                        vec3.sub(targetPosition, this.position, this.tmpVec);
                        var d = targetPosition[1] - this.originalPosition[1];
                        vec3.scale(this.tmpVec, 0.1);
                        vec3.add(this.position, this.tmpVec, this.position);
                        this.changed = true; // vec3.distance(this.position, targetPosition) > Math.abs(d * 0.01);
                        this.offset[1] = this.origY + d;
                        this.setAngle(this.rotation.angle + 0.5);
                    }
                });
            }

            var s = fs_node.is_file ? 20 : 30;
            var f = 0.4;

            if (!rendered_object.reused) {
                rendered_object.appendChild(this.create_model(fs_node, f, s));
                rendered_object.appendChild(this.create_text_mesh(fs_node, f, s));
            }
            if (!fs_node.is_file && fs_node.parent) {
                this.create_connector_line(fs_node, f, rendered_object);
            }

            if (!rendered_object.reused) {
                if (fs_node.parent) {
                    fs_node.parent.node.appendChild(rendered_object);
                } else if (root && root.parent) {
                    root.parent.node.appendChild(rendered_object);
                } else {
                    this.scene.appendChild(rendered_object);
                }
            }
        }
        this.gotoPath(this.fsn.getCurrentPath());
        this.display.changed = true;
    },
    getAbsoluteOffset: function (obj) {
        var parents = [];
        while (obj && obj.offset) {
            parents.unshift(obj);
            obj = obj.parentNode;
        }
        var offset = this.word_translation;
        var scale = 1;
        for (var i = 0; i < parents.length; i++) {
            var p = parents[i];
            offset[0] += p.offset[0] * scale;
            offset[1] += p.offset[1] * scale;
            offset[2] += p.offset[2] * scale;
            scale *= p.entry.offset.scale;
        }
        return {offset: offset, scale: scale};
    },
    move_camera_intro: function (absolute_offset, absolute_scale) {
        // calculate object position
        var target_position = vec3();
        var target_offset = this.lookOffset;
        vec3.scale(target_offset, absolute_scale, target_position);
        vec3.add(absolute_offset, target_position, target_position);


        var new_look_at = vec3();
        vec3.sub(target_position, this.camera.lookAt, new_look_at);
        var d2len = vec3.lengthSquare(new_look_at);
        vec3.scale(new_look_at, 0.1);
        vec3.add(this.camera.lookAt, new_look_at, new_look_at);

        var offset = vec3(this.offset);
        vec3.scale(offset, absolute_scale, offset);
        var new_camera_position = vec3();
        vec3.add(target_position, offset, new_camera_position);
        vec3.sub(new_camera_position, this.camera.position, new_camera_position);
        var new_camera_position_norm = vec3.lengthSquare(new_camera_position);
        vec3.scale(new_camera_position, 0.8);
        vec3.add(this.camera.position, new_camera_position, new_camera_position);

        vec3.set(new_camera_position, this.camera.position);
        //vec3.set(new_look_at, this.camera.lookAt);
        vec3.set(absolute_offset, this.camera.lookAt);

        var distanceToTarget = vec3.distance(this.camera.position, this.camera.lookAt);
        this.camera.zNear = distanceToTarget / 8;
        this.camera.zFar = distanceToTarget * 20;

        if (Math.sqrt(d2len) > distanceToTarget * 0.001 || Math.sqrt(new_camera_position_norm) > distanceToTarget * 0.001)
            this.display.changed = true;
    },
    move_camera: function (camera_position) {
        camera_position = vec3(camera_position);
        // camera_position[2] += 15;
        // camera_position[1] += 4;
        camera_position[2] += 100;
        camera_position[1] += 30;
        vec3.set(camera_position, this.camera.position);


        var new_look_at = vec3();
        vec3.sub(this.fuckinglookAt, camera_position, new_look_at);
        vec3.scale(new_look_at, 0.5);
        vec3.add(this.fuckinglookAt, new_look_at, new_look_at);
        vec3.set(new_look_at, this.camera.lookAt);


        this.display.changed = true;

     /*
      // calculate object position
      var target_position = vec3();
      var target_offset = this.lookOffset;
      vec3.scale(target_offset, absolute_scale, target_position);
      vec3.add(absolute_offset, target_position, target_position);


      var new_look_at = vec3();
      vec3.sub(target_position, this.camera.lookAt, new_look_at);
      var d2len = vec3.lengthSquare(new_look_at);
      vec3.scale(new_look_at, 0.1);
      vec3.add(this.camera.lookAt, new_look_at, new_look_at);

      var offset = vec3(this.offset);
      vec3.scale(offset, absolute_scale, offset);
      var new_camera_position = vec3();
      vec3.add(target_position, offset, new_camera_position);
      vec3.sub(new_camera_position, this.camera.position, new_camera_position);
      var new_camera_position_norm = vec3.lengthSquare(new_camera_position);
      vec3.scale(new_camera_position, 0.8);
      vec3.add(this.camera.position, new_camera_position, new_camera_position);

      vec3.set(new_camera_position, this.camera.position);
      //vec3.set(new_look_at, this.camera.lookAt);
      vec3.set(absolute_offset, this.camera.lookAt);

      var distanceToTarget = vec3.distance(this.camera.position, this.camera.lookAt);
      this.camera.zNear = distanceToTarget / 8;
      this.camera.zFar = distanceToTarget * 50;

      if (Math.sqrt(d2len) > distanceToTarget * 0.001 || Math.sqrt(new_camera_position_norm) > distanceToTarget * 0.001)
      this.display.changed = true;
      */
    },
    explode_model: function (path) {
        if (this.objects[path]) {
            this.explodingModel = path;
        }
        var model = child.childNodes[0];
        var text = child.childNodes[1];
     /*
      for (var obj_name in this.objects) {
      if (this.objects[obj_name] === child) {
      obj = this.objects[obj_name];
      break;
      }
      }
      */
        var ynew;

        model.material.floats.MaterialEmit = vec4(0.0, 0.5, 0.4, 0);
        ynew = model.position[1] + 1.0;
        model.setY(ynew);
        model.setAxis(vec3(0, 0, 1));

        model.setAngle(model.rotation.angle + 0.5);
        ynew = text.position[1] + 1.0;
        text.setY(ynew);

        ynew = child.position[1] + 1.0;
        child.setY(ynew)

        // text.setAngle(text.rotation.angle + 0.5);
    },
    do_the_hitler_thingy: function () {
        var body = this.avatar.childNodes[0];
        body.childNodes[3].setAxis(0, 0, 1);
        body.childNodes[3].setAngle(3.14 * 5 / 4);
        body.childNodes[3].setPosition(-1.2, 0.7, 0);
    },
    sceneUpdate: function () {
        if (this.avatar_moved) {
            if (!this.avatar) {
                this.avatar = new Magi.Cube().setScale(-1, 1, -1);
                this.avatar.material.floats.LightPos = vec4(0, 0, 0, 1);
                this.avatar.material.floats.MaterialDiffuse = vec4(0.1, 0.1, 0.1, 1);
                this.avatar.material.floats.MaterialSpecular = vec4(0.5, 0.5, 0.5, 0);
                this.avatar.material.floats.MaterialEmit = vec4(0.1, 0.3, 0.3, 1);
                this.avatar.material.floats.LightSpecular = vec4(0.95, 0.95, 0.95, 1);
                this.avatar.material.floats.LightDiffuse = vec4(0.7, 0.7, 0.7, 1);
                this.avatar.material.floats.LightAmbient = vec4(0.2, 0.2, 0.2, 1);
                // todo update transform
                this.avatar.setY(0.5);

                var body;
                body = new Magi.Cube().setScale(2, 4, 2);
                body.setPosition(0, 5.5, -1.5);


                var legl;
                legl = new Magi.Cube().setScale(0.5, 1, 0.5);
                legl.setPosition(-0.5, -1, 0);
                body.appendChild(legl);


                var legr;
                legr = new Magi.Cube().setScale(0.5, 1, 0.5);
                legr.setPosition(+0.5, -1, 0);
                body.appendChild(legr);


                var armr;
                armr = new Magi.Cube().setScale(0.3, 1, 0.5);
                armr.setPosition(+0.8, 0.0, 0);
                armr.setAxis(0, 0, 1);
                armr.setAngle(0.5);
                body.appendChild(armr);

                var arml;
                arml = new Magi.Cube().setScale(0.3, 1, 0.5);
                arml.setPosition(-0.8, 0.0, 0);
                arml.setAxis(0, 0, 1);
                arml.setAngle(-0.5);
                body.appendChild(arml);

                var head;
                head = new Magi.Cube().setScale(0.8, 0.5, 0.8);
                head.setPosition(0, 0.9, 0);

                Magi.Texture.load("head3.jpg", function (tex) {
                    head.material.textures.EmitTex = tex;

                });

                Magi.Texture.load("arm.jpg", function (tex) {
                    //body.material.textures.EmitTex = tex;
                    arml.material.textures.EmitTex = tex;
                });

                Magi.Texture.load("head1.jpg", function (tex) {
                    //head.material.textures.EmitTex = tex;
                    body.material.textures.EmitTex = tex;
                    legr.material.textures.EmitTex = tex;
                    legl.material.textures.EmitTex = tex;
                    armr.material.textures.EmitTex = tex;
                    //arml.material.textures.EmitTex = tex;
                });


                arml.material.floats.LightPos = this.lightPos;
                arml.material.floats.MaterialDiffuse = vec4(0.1, 0.1, 0.1, 1);
                arml.material.floats.MaterialSpecular = vec4(0.5, 0.5, 0.5, 0);
                arml.material.floats.MaterialEmit = vec4(0.0, 0.0, 0.0, 0);
                arml.material.floats.LightSpecular = vec4(0.1, 0.1, 0.1, 1);
                arml.material.floats.LightDiffuse = vec4(0.7, 0.7, 0.7, 1);
                arml.material.floats.LightAmbient = vec4(0.2, 0.2, 0.2, 1);

                armr.material.floats.LightSpecular = vec4(0.1, 0.1, 0.1, 1);
                legl.material.floats.LightSpecular = vec4(0.1, 0.1, 0.1, 1);
                legr.material.floats.LightSpecular = vec4(0.1, 0.1, 0.1, 1);
                head.material.floats.LightSpecular = vec4(0.6, 0.6, 0.6, 1);
                body.appendChild(head);

                // mesh = new Magi.Cube().setScale(1, 9, 1);
                // mesh.setPosition(+1, 0.15, 1.2);
                // body.appendChild(mesh);

                this.avatar.appendChild(body);
                this.scene.appendChild(this.avatar);
            }


            if (this.avatar.is_falling) {
                if (this.avatar.position[1] < -300)
                    window.location.href = 'gameover.html';
                this.avatar.position[1] += -0.5;
                console.log("IS FALLING")
            } else {
                var displacement = this.avatar_speed[0] + this.avatar_speed[1];
                if (displacement != 0) {

                    this.avatar.position[0] += this.avatar_speed[0] + this.avatar_speed[1];
                    this.fuckinglookAt[0] += this.avatar_speed[0] + this.avatar_speed[1];
                    var body = this.avatar.childNodes[0];
                    body.childNodes[3].setPosition(-0.8, 0.0, 0);
                    if (displacement > 0) {
                        body.setAngle(-2.14 / 4);
                    } else {
                        body.setAngle(2.14 / 4);
                    }

                 /*
                  var left_leg = body.childNodes[0];
                  left_leg.setAxis(0, 0, 1);
                  // var new_angle = left_leg.rotation.angle + displacement * 0.01
                  var new_angle = Math.sin(this.avatar.position[0] * 0.2)/2;
                  left_leg.setAngle(new_angle);
                  var following_leg = Math.sin(this.avatar.position[0] * 0.2)/5;
                  body.childNodes[1].setAxis(0, 0, 1);
                  body.childNodes[1].setAngle(-new_angle);
                  */

                    var body = this.avatar.childNodes[0];
                    var left_leg = body.childNodes[0];
                    left_leg.setAxis(1, 0, 0);
                    // var new_angle = left_leg.rotation.angle + displacement * 0.01
                    var new_angle = Math.sin(this.avatar.position[0] * 0.1) / 2;

                    left_leg.setAngle(new_angle)
                    body.childNodes[1].setAxis(1, 0, 0);
                    body.childNodes[1].setAngle(-new_angle);

                    body.childNodes[2].setAxis(1, 0, 0);
                    body.childNodes[2].setAngle(-new_angle);
                    body.childNodes[3].setAxis(1, 0, 0);
                    body.childNodes[3].setAngle(new_angle);

                }




                // this.avatar.position[1] += this.avatar.is_falling? -1:0;
                var displacement = this.avatar_speed[2] + this.avatar_speed[3];
                if (displacement < 0) {

                    this.avatar.position[2] += this.avatar_speed[2] + this.avatar_speed[3];
                    this.fuckinglookAt[2] += this.avatar_speed[2] + this.avatar_speed[3];
                    var body = this.avatar.childNodes[0];
                    body.setAngle(0);
                    var left_leg = body.childNodes[0];
                    left_leg.setAxis(1, 0, 0);
                    // var new_angle = left_leg.rotation.angle + displacement * 0.01
                    var new_angle = Math.sin(this.avatar.position[2] * 0.1) / 2;
                    left_leg.setAngle(new_angle)
                    body.childNodes[1].setAxis(1, 0, 0);
                    body.childNodes[1].setAngle(-new_angle);

                    //body.childNodes[3].setPosition(-0.8, 0.0, 0);

                    body.childNodes[2].setAxis(1, 0, 0);
                    body.childNodes[2].setAngle(-new_angle);
                    body.childNodes[3].setAxis(1, 0, 0);
                    body.childNodes[3].setAngle(new_angle);
                    body.childNodes[3].setPosition(-0.8, 0.0, 0);
                }
                else if (displacement > 0) {
                    this.avatar.position[2] += this.avatar_speed[2] + this.avatar_speed[3];
                    this.fuckinglookAt[2] += this.avatar_speed[2] + this.avatar_speed[3];
                    var body = this.avatar.childNodes[0];
                    body.setAngle(3.14);
                    var left_leg = body.childNodes[0];
                    left_leg.setAxis(1, 0, 0);
                    // var new_angle = left_leg.rotation.angle + displacement * 0.01
                    var new_angle = Math.sin(this.avatar.position[2] * 0.1) / 2;
                    left_leg.setAngle(new_angle)
                    body.childNodes[1].setAxis(1, 0, 0);
                    body.childNodes[1].setAngle(-new_angle);

                    body.childNodes[2].setAxis(1, 0, 0);
                    body.childNodes[2].setAngle(-new_angle);
                    body.childNodes[3].setAxis(1, 0, 0);
                    body.childNodes[3].setAngle(new_angle);
                    body.childNodes[3].setPosition(-0.8, 0.0, 0);
                }
            }

            // this.avatar.setPosition(this.avatar.position[0], this.avatar.position[1], this.avatar.position[2]);
            this.avatar.changed = true;

            this.move_camera(this.avatar.position);

            var is_falling = true;
            for (var obj_index in this.objects) {
                var other_thing = this.objects[obj_index];
                if (!this.avatar || this.avatar === other_thing)
                    continue;
                var model_name = other_thing.childNodes[1].text;
                var is_inside = this.is_inside(this.avatar, other_thing);

                if (other_thing.entry.is_file) {
                    if (is_inside) {
                        this.do_the_hitler_thingy();
                        other_thing.is_exploding = true;
                    }
                } else if (is_falling) {
                    // it's a folder
                    var is_above = (this.avatar.position[1] - other_thing.absolutePosition[1]) > 0;
                    if (is_above && is_inside) {
                        // console.log(model_name, "keeping him up")
                        is_falling = false;
                    } else if (other_thing.connectorLine) {
                        // maybe one of it's connector lines?
                        var connector_line = other_thing.connectorLine;
                        var is_inside0 = this.is_inside_cl_tilted(this.avatar, connector_line.childNodes[0]);
                        var is_inside1 = this.is_inside_cl(this.avatar, connector_line.childNodes[1]);
                        is_falling = !(is_inside0 || is_inside1);
                    }
                }
                this.avatar.is_falling = is_falling;
            }
        } else {
            var target_object = this.objects[this.currentObjectIndex];
            if (!target_object) return;
            var absolute_offset = this.getAbsoluteOffset(target_object);
            this.move_camera_intro(absolute_offset.offset, absolute_offset.scale);
        }
    },
    is_inside: function (avatar, other_thing) {
        var other_thing_scale = other_thing.scaling;
        var other_thing_model = other_thing.childNodes[0];

        var cmaxx = other_thing_model.absolutePosition[0] + (other_thing_model.scaling[0] * other_thing_scale[0]) / 2;
        var cminx = other_thing_model.absolutePosition[0] - (other_thing_model.scaling[0] * other_thing_scale[0]) / 2;
        var cmaxz = other_thing_model.absolutePosition[2] + (other_thing_model.scaling[2] * other_thing_scale[0]) / 2;
        var cminz = other_thing_model.absolutePosition[2] - (other_thing_model.scaling[2] * other_thing_scale[0]) / 2;

        var px = avatar.absolutePosition[0];
        var pz = avatar.absolutePosition[2];
        if (px < cminx || pz < cminz || px > cmaxx || pz > cmaxz)
        // if (px < cminx || px > cmaxx)
            return false; //is not within cube
        return true; //is within cube
    },
    is_inside_cl_tilted: function (avatar, connector) {
        var connector_line = connector.childNodes[0];
        var from_platform = vec3(connector_line.parentNode.parentNode.parentNode.entry.parent.node.absolutePosition);
        var to_platform = vec3(connector_line.parentNode.parentNode.parentNode.absolutePosition);
        var avatar_pos = vec3(avatar.position);

        if (!from_platform) return false;
        var max_z_allowed = (to_platform[2] - from_platform[2]) / 2;
        if (avatar.position[2] < max_z_allowed || avatar.position[2] > from_platform[2])
            return false;

        from_platform[1] = from_platform[2];
        from_platform[2] = 1;
        to_platform[1] = to_platform[2] / 2;
        to_platform[2] = 1;
        avatar_pos[1] = avatar_pos[2];
        avatar_pos[2] = 1;

        var line = vec3();
        vec3.cross(from_platform, to_platform, line);
        var distance = vec3.dot(avatar_pos, line);
        if (to_platform[0] < 0) distance *= -1;
        // console.log("look at meee", (Math.abs(distance) ));
        var line_width = connector_line.scaling[1] * connector.scaling[1] * connector.parentNode.scaling[1] / 2;
        return (distance > -9000) && (distance < 5000);
    },
    is_inside_cl: function (avatar, connector) {
        var connector_line = connector.childNodes[0];
        var from_platform = vec3(connector_line.parentNode.parentNode.parentNode.entry.parent.node.absolutePosition);
        var to_platform = vec3(connector_line.parentNode.parentNode.parentNode.absolutePosition);

        if (!from_platform) return false;
        if (avatar.position[2] < to_platform[2] && avatar.position[2] > from_platform[2]) return false;

        // var length = to_platform[2] - from_platform[1]
        // console.log(c.parentNode.parentNode.parentNode.entry.name, to_platform[0] - this.avatar.position[0]);
        var distance = Math.abs(to_platform[0] - avatar.position[0]);
        var line_width = connector_line.scaling[1] * connector.scaling[1] * connector.parentNode.scaling[1] / 2;
        if (distance > line_width) {
            return false;
        } else {
            return true;
        }
    },

});

var buildTree = function (e) {
    // Reset
    var pathList_ = [];
    var fileList = e.target.files;

    for (var i = 0, file; file = fileList[i]; ++i) {
        pathList_.push(file.webkitRelativePath);
    }
    start_game(pathList_);
    // buildTreeFromPathList(pathList_, true);
};
var buildTreeFromPathList = function (pathList_, rebaseToTopDir) {
    var tree = FS_GRAPH.buildTreeFromPathList(pathList_);
    fsn = new FS_GRAPH(tree);
    if (rebaseToTopDir) {
        for (var i in fsn.tree.entries) {
            fsn.tree = fsn.tree.entries[i];
            fsn.tree.parent = null;
            fsn.tree.name = '/';
            // fsn.cd('/');
            break;
        }
    }
    if (!window.fsnRender) {
        fsnRender = new FSNRender(fsn);
    } else {
        fsnRender.setFSN(fsn);
        fsnRender.updateLayout();
    }
};
replaceSubTree = function (path, pathlist) {
    var tree = FS_GRAPH.buildTreeFromPathList(pathlist);
    var entry = fsn.getEntry(path);
    var parent = entry.parent;
    tree.name = entry.name;
    parent.removeEntry(entry);
    parent.addEntry(tree);
    fsnRender.updateLayoutPath(tree.getPath());
};

var dirsel = document.getElementById('path_selector');
dirsel.addEventListener('change', function(e){
    document.getElementById("playButton").onclick = function(){
        buildTree(e);
    }
}, false)
window.addEventListener('message', function (e) {
    var message = e.data;
    switch (message.cmd) {
        case 'build':
            buildTreeFromPathList(message.data);
            break;
        case 'replaceSubTree':
            replaceSubTree(message.data.path, message.data.pathlist);
            break;
    }
}, false);