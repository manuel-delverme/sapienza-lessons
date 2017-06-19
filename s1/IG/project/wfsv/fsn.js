FS_GRAPH = function(tree) {
    this.selectedFiles = {};
    this.tree = tree;
    this.cd(FS_GRAPH.DIR_SEPARATOR);
};
FS_GRAPH.DIR_SEPARATOR = '/';
FS_GRAPH.TYPE_FILE = 'file';
FS_GRAPH.TYPE_DIR = 'dir';

FS_GRAPH.prototype = {
    tree : null,
    current : null,

    getEntry : function(path) {
        if (path == '') {
            path = this.current.getPath();
        } else if (path == null) {
            path = '/';
        }
        var cur = this.current;
        var elems = path.split('/');
        if (elems[0] == '') {
            cur = this.tree;
        }
        while (elems.length > 0) {
            var seg = elems.shift();
            if (seg != '') {
                if (seg == '..') {
                    cur = cur.parent;
                } else if (seg == '.') {
                    cur = cur;
                } else if (cur.entries != null) {
                    cur = cur.entries[seg];
                } else {
                    return null;
                }
            }
        }
        return cur;
    },

    cd : function(path) {
        var cur = this.getEntry(path);
        if (cur == null) {
            throw(new Error('cd: No such path ' + path));
        }
        this.current = cur;
        if (this.onChangeDir) {
            this.onChangeDir(this.getCurrentPath());
        }
    },

    ls : function(path) {
        var cur = path ? this.getEntry(path) : this.current;
        if (cur == null) {
            throw(new Error('ls: No such path ' + path));
        }
        var a = [];
        if (cur.entries != null) {
            for (var i in cur.entries)
                a.push(cur.entries[i]);
        } else {
            a.push(cur);
        }
        a.sort(function(x,y) {
            var xdir = x.entries !== null;
            var ydir = y.entries !== null;
            if (xdir && !ydir) {
                return -1;
            } else if (ydir && !xdir) {
                return 1;
            } else {
                return (x.name < y.name ? -1 : (x.name == y.name ? 0 : 1));
            }
        });
        return a;
    },

    rm : function(path) {
        var cur = this.getEntry(path);
        if (cur == null) {
            throw(new Error('rm: No such path ' + path));
        }
        var parent = cur.parent;
        if (!parent) {
            throw(new Error("rm: Can't delete root directory " + path));
        }
        parent.removeEntry(cur);
        if (this.onRelayoutNeeded)
            this.onRelayoutNeeded(parent);
    },

    createParent : function(path, callerName) {
        if (!callerName) {
            callerName = 'createParent';
        }
        var segs = path.split('/');
        var parent = segs.slice(0,-1).join('/');
        if (parent == "" && segs.length == 2) {
            parent = "/";
        }
        var cur = this.getEntry(parent);
        if (cur == null) {
            this.mkdir(parent);
            cur = this.getEntry(parent);
            if (!cur) {
                throw(new Error(callerName + ': Could not find ' + parent));
            }
        }
        var name = segs.last();
        if (cur.entries == null) {
            throw(new Error(callerName + ": Can't " + callerName + " inside a file " + parent));
        } else if (cur.entries[name]) {
            throw(new Error(callerName + ": File already exists " + path));
        }
        return cur;
    },

    mv : function(src, dst) {
        var e = this.getEntry(src);
        if (!e) {
            throw(new Error("mv: Source file "+src+ " does not exist"));
        } else if (!e.parent) {
            throw(new Error("mv: Can't move root directory."));
        }
        var cur = this.createParent(dst, 'mv');
        var p = e.parent;
        p.removeEntry(e);
        e.name = dst.split('/').last();
        cur.addEntry(e);
        if (this.onRelayoutNeeded) {
            this.onRelayoutNeeded(p);
            this.onRelayoutNeeded(cur);
            this.onRelayoutNeeded(e, true);
        }
    },

    cp : function(src, dst) {
        var e = this.getEntry(src);
        if (!e) {
            throw(new Error("cp: Source file "+src+ " does not exist"));
        }
        var cur = this.createParent(dst, 'cp');
        var copy = e.clone();
        copy.name = dst.split('/').last();
        cur.addEntry(copy);
        if (this.onRelayoutNeeded) {
            this.onRelayoutNeeded(cur, true);
        }
    },

    mkdir : function(path) {
        var cur = this.createParent(path, 'mkdir');
        var entry = new FS_GRAPH.Entry(path.split('/').last(), 0, {});
        cur.addEntry(entry);
        if (this.onRelayoutNeeded)
            this.onRelayoutNeeded(cur);
    },

    create : function(path, size) {
        size = parseInt(size);
        var cur = this.createParent(path, 'create');
        var entry = new FS_GRAPH.Entry(path.split('/').last(), size, null);
        cur.addEntry(entry);
        if (this.onRelayoutNeeded)
            this.onRelayoutNeeded(cur);
    },

    touch : function(path) {
        if (!this.getEntry(path)) {
            this.create(path, 0);
        }
    },

    getCurrentPath : function() {
        return this.current.getPath();
    },

    selectFile : function(path) {
        this.selectedFiles[path] = true;
    },

    deselectFile : function(path) {
        delete this.selectedFiles[path];
    },

    flattenLayout : function(layout, arr) {
        arr.push(layout);
        if (layout.entries != null) {
            for (var f in layout.entries) {
                this.flattenLayout(layout.entries[f], arr);
            }
        }
        return arr;
    },

    getLayout : function(path, maxDepth) {
        if (!path)
            path = '/';
        var entry = this.getEntry(path);
        if (entry.entries == null) {
            throw new Error("Can't layout a file: " + path);
        } else {
            var layout = this.createLayout(entry, {x:0, y:0, z:0, scale: 1}, null, maxDepth, 0);
            return this.flattenLayout(layout, []);
        }
    },

    createLayout : function(tree, offset, dir, maxDepth, depth) {
        var layout;
        if (tree.is_file) {
            layout = this.createFileLayout(tree, offset, dir);
        } else {
            layout = this.createDirLayout(tree, offset, dir, maxDepth, depth);
        }
        layout.is_file = tree.is_file;
        return layout;
    },

    createFileLayout : function(file, offset, dir) {
        return {path: file.getPath(), name: file.name, size: file.size, offset: offset, parent: dir};
    },

    createDirLayout : function(tree, offset, dir, maxDepth, depth) {
        var fs_nodes = [];
        var fileCount = 0;
        var dirCount = 0;

        for (var file_object in tree.entries) {
            fs_nodes.push(file_object);
            if (tree.entries[file_object].entries)
                dirCount++;
            else
                fileCount++;
        }
        fs_nodes.sort();
        var squareSide = Math.ceil(Math.sqrt(fileCount));
        var fidx = 0, didx = 0;
        var layout = {path: tree.getPath(), name: tree.name, size: tree.size, offset: offset, entries: {}, parent: dir};
        for (var i=0; i<fs_nodes.length; i++) {
            var entry = tree.entries[fs_nodes[i]];
            var off = Object.extend({}, offset);
            if (entry.is_file) {
                off.scale = 1 / Math.max(3, squareSide);
                var x = fidx % squareSide;
                var y = Math.floor(fidx / squareSide);
                off.x = 160 * (x - (squareSide - 1) / 2) * off.scale;
                off.y = 0 * off.scale;
                off.z = -160 * (y - (squareSide - 1) / 2) * off.scale;
                fidx++;
            } else {
                off.scale = Math.min(0.8, 1 / dirCount);
                off.x = off.scale * (-(dirCount - 1) / 2 + didx) * 100;
                off.y = off.scale * 1;
                off.z = -160;
                didx++;
            }
            layout.entries[entry.name] = this.createLayout(entry, off, layout, maxDepth, depth + 1);
        }
        return layout;
    }

};


FS_GRAPH.Entry = function(name, size, entries) {
    this.name = name;
    this.size = size;
    this.entries = entries;
};
FS_GRAPH.DoubleDirRE = new RegExp(FS_GRAPH.DIR_SEPARATOR+FS_GRAPH.DIR_SEPARATOR, 'g');
FS_GRAPH.Entry.prototype = {
    type : FS_GRAPH.TYPE_FILE,
    size : 0,

    getPath : function() {
        var o = this;
        var segs = [o.name];
        while (o.parent) {
            o = o.parent;
            segs.unshift(o.name);
        }
        return segs.join(FS_GRAPH.DIR_SEPARATOR).replace(FS_GRAPH.DoubleDirRE, FS_GRAPH.DIR_SEPARATOR);
    },

    addEntry : function(entry) {
        this.entries[entry.name] = entry;
        entry.parent = this;
    },

    removeEntry : function(entry) {
        delete this.entries[entry.name];
        entry.parent = null;
    },

    clone : function() {
        var copy = new FS_GRAPH.Entry(this.name, this.size, this.entries);
        if (this.entries != null) {
            copy.entries = {};
            for (var i in this.entries) {
                copy.addEntry(this.entries[i].clone());
            }
        }
        return copy;
    }
};


FS_GRAPH.makeTree = function(fs_tree) {
    var subtree_root;
    var root_node = new FS_GRAPH.Entry('/', 0, {});
    var is_file, subtree;
    for (var fs_node in fs_tree) {
        root_node.size++;
        subtree = fs_tree[fs_node];
        is_file = typeof subtree === typeof(1);

        if (is_file) {
            subtree_root = new FS_GRAPH.Entry(fs_node, subtree, null)
        } else {
            subtree_root = FS_GRAPH.makeTree(subtree);
            subtree_root.name = fs_node;
            root_node.addEntry(subtree_root);
        }
        subtree_root.is_file = is_file;
        root_node.addEntry(subtree_root);
    }
    return root_node;
};
FS_GRAPH.buildTreeFromPathList = function(paths, sizes) {
    var tree_ = {};
    if (!sizes) sizes = [];
    for (var i=0; i<paths.length; i++) {
        var path = paths[i];
        var pathParts = path.split('/');
        var subObj = tree_;
        var l = pathParts.length-1;
        for (var j=0; j<l; j++) {
            var folderName = pathParts[j];
            if (typeof subObj[folderName] != 'object') {
                subObj[folderName] = {};
            }
            subObj = subObj[folderName];
        }
        if (pathParts[l] != '.') {
            subObj[pathParts[l]] = sizes[i] || 0;
        }
    }
    return FS_GRAPH.makeTree(tree_);
};
