$( document ).ready(function() {

    ws_url = 'ws://' + window.location.hostname + ':9090';

    window.ros = new ROSLIB.Ros({
        url : ws_url
    });

    ros.on('connection', function() {
        console.log('Connected to websocket server.');
        $('.connection-status').addClass('badge-success')
        $('.connection-status').removeClass('badge-danger')
        $('.connection-status').html('Connected');
    });

    ros.on('error', function(error) {
        console.log('Error connecting to websocket server: ', error);
        $('.connection-status').addClass('badge-danger')
        $('.connection-status').removeClass('badge-success')
        $('.connection-status').html('Offline');
    });

    ros.on('close', function() {
        console.log('Connection to websocket server closed.');
        $('.connection-status').addClass('badge-danger')
        $('.connection-status').removeClass('badge-success')
        $('.connection-status').html('Offline');
    });

    $('.connection-status').on('click', function(){
        window.ros.connect(ws_url);
    });

    window.movementPublisher = new ROSLIB.Topic({
        ros : window.ros,
        name : '/cmd_vel',
        messageType : 'geometry_msgs/Twist'
    });

    createJoystick = function () {
        var options = {
        zone: document.getElementById('zone_joystick'),
        threshold: 0.1,
        position: { left: 50 + '%', top: 50 + '%' },
        mode: 'static',
        size: 300,
        color: '#000000',
        };
        manager = nipplejs.create(options);

        linear_speed = 0;
        angular_speed = 0;

        manager.on('start', function (event, nipple) {
            timer = setInterval(function () {
                move(linear_speed, angular_speed);
            }, 25);
        });

        manager.on('end', function () {
            if (timer) {
                clearInterval(timer);
            }
            move(0, 0);
        });

        manager.on('move', function (event, nipple) {
            max_linear = 10.0; // m/s
            max_angular = 10.0; // rad/s
            max_distance = 150.0; // pixels;
            linear_speed = Math.sin(nipple.angle.radian) * max_linear * nipple.distance/max_distance;
            angular_speed = -Math.cos(nipple.angle.radian) * max_angular * nipple.distance/max_distance;
            
        });
            
    }
    window.onload = function () {
        createJoystick();
    }     
});

function move(linear, angular) {
    if(linear > 10) linear = 10;
    if(linear < -10) linear = -10;
    if(angular > 10) angular = 10;
    if(angular < -10) angular = -10;

    var twist = new ROSLIB.Message({
        linear: { x: linear, y: 0, z: 0 },
        angular: { x: 0, y: 0, z: angular}
    });
    window.movementPublisher.publish(twist);
}
