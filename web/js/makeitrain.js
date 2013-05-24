$(function() {
            var y = 0, a = 0, b = 0, vb = 4, vy = 2, va = 3, canvas, context, image, height, width;
     
            canvas = $("#canvas")[0];
            width = $(document).width()+10;
            context = canvas.getContext("2d");
            
            setInterval(draw, 1000/24);

            function draw() {
              context.clearRect(0, 0, canvas.width, canvas.height);
              context.beginPath();
              context.fillStyle = "#339900";
              context.font = "bold 40pt Helvetica";
              context.fillText("$", 10, y-100);
              context.fillText("$", 50, y);
              context.font = "bold 80pt Helvetica";
              context.fillText("$", 110, y-50);
              context.fillText("$", 150, y-80);
              context.fillText("$", 280, y);
              context.font = "bold 40pt Helvetica";
              context.fillText("$", 360, y);
              context.fillText("$", 490, y-60);
              context.font = "bold 80pt Helvetica";
              context.fillText("$", 530, y-90);
              context.fill();
              y += vy;
              if(y > canvas.height + 220) {
                y = 0;
              }
              context.beginPath();
              context.fillStyle = "#CCFF00";
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 15, a-150);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 80, a);
              context.fillText("$", 170, a-60);
              context.fillText("$", 280, a);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 360, a-90);
              context.fillText("$", 580, a-10);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 700, b-40);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 800, a-120);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 960, a-30);
              context.fillText("$", 1080, a-10);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 1200, b-150);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 1450, a-90);
              context.fill();
              a += va;
              if(a > canvas.height + 220) {
                a = 0;
              }
              context.beginPath();
              context.fillStyle = "#006600";
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 40, b-90);
              context.fillText("$", 25, b-140);
              context.font = "bold 70pt Helvetica";
              context.fillText("$", 95, b-10);
              context.fillText("$", 150, b-40);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 240, b-60);
              context.font = "bold 70pt Helvetica";
              context.fillText("$", 500, b-15);
              context.fillText("$", 960, b-130);
              context.fillText("$", 1180, b-10);
              context.font = "bold 50pt Helvetica";
              context.fillText("$", 1300, b);
              context.font = "bold 30pt Helvetica";
              context.fillText("$", 1650, b-40);
              context.fill();
              b += vb;
              if(b > canvas.height + 220) {
                b = 0;
              }
            }
      });