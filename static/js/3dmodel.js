/*
Copyright 2024 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

import * as THREE from 'three';

import Stats from 'three/addons/libs/stats.module.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

let container, stats, clock, gui, mixer, controls;
let camera, scene, renderer, model;

const api = { model: 'Bugdroid' };

let container_width, container_height = 0;

let isDragging = false;
let offsetX, offsetY;

initDragging();
init();

function init() {

    //container = $('#modelWindow').draggable();
    container = $('#modelContainer')[0];
    container_width = $(container).width();
    container_height = $(container).height();
    //document.body.appendChild( container );

    camera = new THREE.PerspectiveCamera( 45, container_width / container_height, 0.25, 500 );
    camera.position.set( -5, 3, 15 );
    camera.lookAt( 0, 2, 0 );

    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xe0e0e0 );
    scene.fog = new THREE.Fog( 0xe0e0e0, 100, 500 );

    clock = new THREE.Clock();

    // lights

    const hemiLight = new THREE.HemisphereLight( 0xffffff, 0x8d8d8d, 3 );
    hemiLight.position.set( 0, 20, 0 );
    scene.add( hemiLight );

    const dirLight = new THREE.DirectionalLight( 0xffffff, 3 );
    dirLight.position.set( 0, 20, 10 );
    scene.add( dirLight );

    // ground

    const mesh = new THREE.Mesh( new THREE.PlaneGeometry( 2000, 2000 ), new THREE.MeshPhongMaterial( { color: 0xcbcbcb, depthWrite: false } ) );
    mesh.rotation.x = - Math.PI / 2;
    scene.add( mesh );

    const grid = new THREE.GridHelper( 200, 40, 0x000000, 0x000000 );
    grid.material.opacity = 0.2;
    grid.material.transparent = true;
    scene.add( grid );

    model = new THREE.Mesh();
    model.name = 'Bugdroid';
    
    loadModel(model).then(result => createGUI(model));

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( container_width, container_height );
    renderer.setAnimationLoop( animate );
    container.appendChild( renderer.domElement );

    controls = new OrbitControls( camera, renderer.domElement );
    // controls.listenToKeyEvents( window ); // optional

    controls.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
    controls.dampingFactor = 0.05;

    controls.screenSpacePanning = false;
    controls.target = new THREE.Vector3(0, 2, 0);

    controls.minDistance = 25;
    controls.maxDistance = 250;

    controls.maxPolarAngle = Math.PI / 2;

    window.addEventListener( 'resize', onWindowResize );

    // stats
    stats = new Stats();
    container.appendChild( stats.dom );
}

function initDragging() {
    $("#titleBar").mousedown(function(e) {
        isDragging = true;
        offsetX = e.pageX - $("#modelWindow").offset().left;
        offsetY = e.pageY - $("#modelWindow").offset().top;
    });

    $("#closeButton").click(function(e) {
        $("#modelWindow").hide();
    });

    $("#closeButton").on('touchend', function(e) {
        $("#modelWindow").hide();
    });

    $(document).mousemove(function(e) {
        if (isDragging) {
            $("#modelWindow").offset({
                left: e.pageX - offsetX,
                top: e.pageY - offsetY
            });
        }
    });

    $(document).mouseup(function() {
        isDragging = false;
    });    
}

function setMaterialColor(model, color ) {
    model.traverse((node) => {
        if (node.isMesh) {
            let tmp = node.material;
            tmp.color = new THREE.Color(color);
            node.material = tmp;
        }
    });
}

export function reloadCurrentModel() {
    loadModel(model);
}

function loadModel(model) {
    
    var modelName = model.name;
    const loader = new GLTFLoader();
    
    console.log("Removing ", model.name);
    var selectedObject = scene.getObjectByName(modelName);
    scene.remove(selectedObject);
    
    const filename = modelName.toLowerCase().replace(" ", "_");

    return new Promise((resolve, reject) => {

        loader.load( 'static/models/'+filename+'.glb', function ( gltf ) {
            model = gltf.scene;
            model.name = modelName;
            console.log("Adding ", model.name);
            if('animations' in gltf) {
                model.animations = gltf.animations;
                console.log('Adding ' + model.animations.length + ' animations.')
            }
    
            scene.add( model );
    
            if('animations' in gltf) {
                mixer = new THREE.AnimationMixer(model);
                mixer.clipAction(model.animations[0]).play();        
            }
    
            fetch('/get_model/' + model.name)
            .then(response => { 
                if (!response.ok) {
                    console.log("Character data not found. Defaulting to black.");
                    return {'color': '#000000'}
                }
                return response.json()
            })
            .then(data => {
                setMaterialColor(model, data.color);
             
            })
            .catch(error => console.error('Error:', error));

            resolve();
        }, undefined, function ( e ) {
            console.error( e );
            reject();
        } );
    });
}

function createGUI( model ) {

    console.log("Creating GUI");

    const states = [ 
        'Bugdroid',
    ];

    gui = new GUI({ autoPlace: false, title: 'Model' });
    container.appendChild(gui.domElement);

    // states

    const statesFolder = gui.add( api, 'model' ).options( states );
    statesFolder.onChange( function (e) {
        model = new THREE.Mesh();
        model.name = e;
        loadModel(model);
    } );

}

function onWindowResize() {

    // camera.aspect = window.innerWidth / window.innerHeight;
    camera.aspect = container_width / container_height;
    camera.updateProjectionMatrix();

    //renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.setSize( container_width, container_height );

}

//

function animate() {

    const dt = clock.getDelta();
    controls.update();

    if ( mixer ) mixer.update( dt );

    renderer.render( scene, camera );

    stats.update();

}
