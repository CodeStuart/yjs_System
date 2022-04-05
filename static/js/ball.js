function createsigma(nodes, edges, classname) {
    var g = {nodes, edges};
    var topiccss = {
        width: '400px',
        height: '390px',
        float: "left"
    };
    var name = "." + classname;

    $(name).html("<div class='mention' id='topic00'></div>");
    $("#topic00").css(topiccss);
    s = new sigma({
        graph: g,
        container: 'topic00'
    });

}


function createdemo(nodes, edges, divid, width, height) {

    var radius = 7;

    var strokeScale = d3.scale.linear()
        .range([1.5, 4])
        .nice();

    var svg = d3.select("#" + divid).append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("class", "g-nodes")
        .attr("font-size",18)
    ;


    // var force = d3.layout.force()
    //                 // .nodes(nodes)
    //                 // .links(edges)
    //                 .size([width,height])
    //                 .linkDistance(10)
    //                 .charge(-500);
    //                 // .start();
    var force = d3.layout.force()
        .gravity(.5)
        .charge(-1000)
        .linkDistance(160)
        .size([width, height])
;

    var color = d3.scale.category20();

    var link = svg.selectAll("line")
        .data(edges)
        .enter()
        .append("line")
        .attr("class", "link")
        .style("stroke", function (d) {

            return "#778899";

        })
        .style("stroke-width", 1);


    var link_text = svg.selectAll(".link_text")
        .data(edges)
        .enter()
        .append("text")
        .attr("class", "link_text")
        .text(function (d) {
            return d.correlation;
        });


    var node = svg.selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", radius - .75)
        .style("fill", function (d) {
            if (d.group == 1)
                return "yellow";
            if (d.group == 10)
                return "#40E0D0";
            if (d.group == 2)
                return "#00BFFF";
        })
        .call(force.drag);


    var node_text = svg.selectAll(".node_text")
        .data(nodes)
        .enter()
        .append("text")
        .attr("class", "node_text")
        .attr("dy", ".3em")
        .attr("dx", "-.4em")
        .text(function (d) {
            return d.name
        });

    node.append("title")
        .text(function (d) {
            return "pool: " + d.name
        });

    // force.on("tick", function () {
    //
    // node.attr("cx", function(d) { return d.x; })
    //     .attr("cy", function(d) { return d.y; });
    //
    // node_text.attr("x",function(d){ return d.x });
    // node_text.attr("y",function(d){ return d.y });
    //
    // link.attr("x1", function(d) { return d.source.x;})
    //     .attr("y1", function(d) { return d.source.y; })
    //     .attr("x2", function(d) { return d.target.x; })
    //     .attr("y2", function(d) { return d.target.y; });
    //
    // link_text.attr("x",function(d){ return (d.source.x + d.target.x) / 2 ; });
    // link_text.attr("y",function(d){ return (d.source.y + d.target.y) / 2 ; });
    //
    // link_text.style("fill-opacity",function(d){
    //   return d.source.show || d.target.show ? 1.0 : 1.0 ;
    // });
    //
    //
    // });

    force
        .nodes(nodes)
        .links(edges)
        .on("tick", tick)
        .start();

    function tick() {
        node.attr("cx", function (d) {
            return d.x = Math.max(radius, Math.min(width - radius, d.x));
        })
            .attr("cy", function (d) {
                return d.y = Math.max(radius, Math.min(height - radius, d.y));
            });

        node_text.attr("x", function (d) {
            return d.x
        });
        node_text.attr("y", function (d) {
            return d.y
        });

        link.attr("x1", function (d) {
            return d.source.x;
        })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        link_text.attr("x", function (d) {
            return (d.source.x + d.target.x) / 2;
        });
        link_text.attr("y", function (d) {
            return (d.source.y + d.target.y) / 2;
        });

        link_text.style("fill-opacity", function (d) {
            return d.source.show || d.target.show ? 1.0 : 1.0;
        });
    }

}


function drawkeywords(data, width, height, divid) {
    var maxRadius = 32;
    var mixRadius = 18;
    var collisionPadding = 4;
    var color = d3.scale.category20c();

    var svg = d3.select("#" + divid).append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("class", "g-nodes");


    var charge = -500;
    var force_height = height;
    if (data.length < 10) {
        charge = -800;
        force_height = height - 100;
    }

    var force = d3.layout.force()
        .gravity(0.1)
        .charge(charge)
        .linkDistance(0)
        .size([width, force_height]);
    force.nodes(data)
        .start();
    var node = svg.selectAll(".g-node")
        .data(data)
        .enter()
        .append("a")
        .attr("fill", "#CA4C44")
        .attr("class", "g-node")
        /*	    .on("click",click)*/
        .on("mouseover", mouseover)
        .on("mouseout", mouseout)
        .call(force.drag);

    function radius(d) {
        if (d.value * 1000 > maxRadius) {
            return maxRadius;
        } else if (d.value * 1000 < mixRadius) {
            return mixRadius
        }
        return d.value * 1000;
    }

    function mouseover() {
        d3.select(this).select("circle").transition()
            .duration(750)
            .attr("r", function (d) {
                return radius(d) + 2
            });
    }

    function mouseout() {
        d3.select(this).select("circle").transition()
            .duration(30)
            .attr("r", function (d) {
                return radius(d) - 2
            });
    }


    node.append("circle").attr("class", "g-node").attr("r", function (d) {
        if (d.value * 1000 > maxRadius) {
            return maxRadius;
        } else if (d.value * 1000 < mixRadius) {
            return mixRadius
        }
        return d.value * 1000;
    });

    node.append("title").text(function (d) {
        return d.name;
    });

    var nodetext = node.append("text")
        .attr("dx", 0)
        .attr("dy", ".36em")
        .attr("text-anchor", "middle")
        .attr("class", "g-name")
        .style("pointer-events", "none")
        .attr("font-family", "sans-serif")
        .attr("fill", "#000")
        .style("font-size", function (d) {
            return size(d) + "px";
        })
        .style("width", function (d) {
            return d.value - 3 + "px";
        })
        .text(function (d) {
            return d.name
        });


    function tick(e) {
        node.each(gravity(e.alpha * .1))
            .each(collide(0.5))
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
    }


    function gravity(alpha) {
        var cx = width / 2,
            cy = height / 2,
            ax = alpha / 4,
            ay = alpha;
        return function (d) {
            d.x += (cx - d.x) * ax;
            d.y += (cy - d.y) * ay;
        };
    }


    function collide(alpha) {
        return function (d) {
            data.forEach(function (d2) {
                var dr, d2r;
                if (d.value > maxRadius) {
                    dr = maxRadius;
                } else if (d.value < mixRadius) {
                    dr = mixRadius
                } else {
                    dr = d.value;
                }
                if (d2.value > maxRadius) {
                    d2r = maxRadius;
                } else if (d2.value < mixRadius) {
                    d2r = mixRadius
                } else {
                    d2r = d2.value;
                }
                if (d != d2) {
                    x = d.x - d2.x;
                    y = d.y - d2.y;
                    distance = Math.sqrt(x * x + y * y);
                    minDistance = dr + d2r + collisionPadding;
                    if (distance < minDistance) {
                        distance = (distance - minDistance) / distance * alpha;
                        moveX = x * distance;
                        moveY = y * distance;
                        d.x -= moveX;
                        d.y -= moveY;
                        d2.x += moveX;
                        d2.y += moveY;
                    }
                }
            });
        }
    }

    function size(d) {
        if ((d.value - 3) > 35) {
            return 35;
        } else {
            return Math.max(15, (d.value - 3));
        }
    }
}
