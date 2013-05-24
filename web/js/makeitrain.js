$(function() {
            var y = 0, a = 0, b = 0, vb = 4, vy = 2, va = 3, canvas, context, image, height, width;
     
            canvas = $("#canvas")[0];
            width = $(document).width();
            context = canvas.getContext("2d");
            
            setInterval(draw, 1000/24);

            function draw() {
              context.clearRect(0, 0, canvas.width, canvas.height);
              context.beginPath();
              context.fillStyle = "#339900";
              context.font = "bold 40pt Helvetica";
              context.fillText("$", 10, y-10);
              context.fillText("$", 50, y);
              context.font = "bold 80pt Helvetica";
              context.fillText("$", 110, y-30);
              context.fillText("$", 150, y-20);
              context.fillText("$", 280, y);
              context.font = "bold 40pt Helvetica";
              context.fillText("$", 360, y);
              context.fillText("$", 490, y-15);
              context.font = "bold 80pt Helvetica";
              context.fillText("$", 530, y-15);
              context.fill();
              y += vy;
              if(y > canvas.height + 60) {
                y = 0;
              }
              context.beginPath();
              context.fillStyle = "#CCFF00";
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 15, a-10);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 80, a);
              context.fillText("$", 170, a-30);
              context.fillText("$", 280, a);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 360, a-20);
              context.fillText("$", 580, a-5);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 700, b-45);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 800, a-5);
              context.fill();
              a += va;
              if(a > canvas.height + 60) {
                a = 0;
              }
              context.beginPath();
              context.fillStyle = "#006600";
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 40, b-20);
              context.fillText("$", 25, b);
              context.font = "bold 70pt Helvetica";
              context.fillText("$", 95, b-10);
              context.fillText("$", 150, b);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 240, b);
              context.font = "bold 70pt Helvetica";
              context.fillText("$", 500, b-45);
              context.fill();
              b += vb;
              if(b > canvas.height + 60) {
                b = 0;
              }
            }
      });