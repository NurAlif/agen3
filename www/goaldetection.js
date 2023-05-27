

var GoalDetection = function(el){
    this.canvas = el,
    this.height = 300,
    this.width = 300,
    this.length = 40,
    this.radius = 100,
    this.offset_x = 0,
    this.offset_y = 0,
    
    this.build = function (){

        this.offset_x = this.width/2;
        this.offset_y = this.height/2;

        var ctx = this.canvas.getContext("2d");
        this.canvas.setAttribute("height",this.height);
        this.canvas.setAttribute("width", this.width);
        
        let line_subdivision = 20
        this.radius = 120
        
        for(var i = 0; i <= line_subdivision; i++){
            let circle_point = Math.PI/line_subdivision*i;
            let pos_x = Math.cos(circle_point)*this.radius + this.offset_x;
            let pos_y = -Math.sin(circle_point)*this.radius+ this.offset_y;
            ctx.strokeStyle = "rgba(150, 150, 150, 1)";
            ctx.lineWidth = 3;
            ctx.lineTo(pos_x, pos_y);
            ctx.stroke();
            if(i == 0) ctx.moveTo(pos_x, pos_y);
        }
        
    },
    this.addDet = function(pos){
        var ctx = this.canvas.getContext("2d");
        ctx.beginPath();

        ctx.strokeStyle = "rgba(255, 100, 100, 1)";
        ctx.lineWidth = 1;
        
        let circlepoint = Math.PI/2*(pos*(2/3))+Math.PI/2;
        let pos_x = Math.cos(circlepoint);
        let pos_y = -Math.sin(circlepoint);
        
        ctx.moveTo(pos_x *(this.radius-10) + this.offset_x, pos_y *(this.radius-10) + this.offset_y);
        ctx.lineTo(pos_x *(this.radius+10) + this.offset_x, pos_y *(this.radius+10) + this.offset_y);
        ctx.stroke();
    },
    this.updateGoalScan = function(obj){
        let dets = obj.dets
        let det_len = dets.length;
        this.build();
        for(var i = 0; i< det_len; i++){
            this.addDet(dets[i][0]);
        }
    }
};
