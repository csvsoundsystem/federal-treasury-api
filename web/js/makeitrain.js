$(function() {
            var y = 0, a = 0, b = 0, vb = 4, vy = 2, va = 3, canvas, context, image, height, width;
     
            canvas = $("#canvas")[0];
            width = $(document).width();
            context = canvas.getContext("2d");
            
            setInterval(draw, 1000/24);

            function draw() {
              context.clearRect(0, 0, width, 300);
              context.beginPath();
              context.fillStyle = "#339900";
              context.font = "bold 20pt Helvetica";
              context.fillText("$", 10, y-10);
              context.fillText("$", 30, y);
              context.fillText("$", 80, y-30);
              context.fillText("$", 110, y-20);
              context.fillText("$", 200, y);
              context.fillText("$", 400, y-15);
              context.fill();
              y += vy;
              if(y > 300) {
                y = 0;
              }
              context.beginPath();
              context.fillStyle = "#CCFF00";
              context.font = "bold 15pt Helvetica";
              context.fillText("$", 15, a-10);
              context.fillText("$", 40, a);
              context.fillText("$", 100, a-30);
              context.fillText("$", 150, a);
              context.fillText("$", 250, a-20);
              context.fillText("$", 410, a-5);
              context.fillText("$", 460, b-45);
              context.fill();
              a += va;
              if(a > 300) {
                a = 0;
              }
              context.beginPath();
              context.fillStyle = "#006600";
              context.font = "bold 26pt Helvetica";
              context.fillText("$", 20, b-20);
              context.fillText("$", 5, b);
              context.fillText("$", 75, b-10);
              context.fillText("$", 130, b);
              context.fillText("$", 220, b);
              context.fillText("$", 480, b-45);
              context.fill();
              b += vb;
              if(b > 300) {
                b = 0;
              }
            }
      });