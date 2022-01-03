$title shortest path try

option limcol = 0, limrow = 0, solprint = off;
set
    nodes
    roadID
;

alias (nodes,i,j);
$gdxin ../link_file.gdx
$loadm nodes=dim1 nodes=dim2
parameter distance(nodes,nodes) distance of a road;
$load  distance=link
$gdxin

$gdxin ../road_file.gdx
set road(roadID<,nodes,nodes);
$load  road=road
$gdxin

$gdxin ../crash_file.gdx
parameter  crash(nodes,nodes) number of crashes on a road;
$load  crash=crash
$gdxin


set arc(nodes,nodes);

arc(i,j) = no;
arc(i,j)$(distance(i,j) > 0.5) = yes;

parameter
    supply(nodes)
;

scalar origin,destination;
execseed = 1 + gmillisec(jnow);
origin = uniformint(1,card(nodes));
destination = uniformint(1,card(nodes));

supply(nodes)$(ord(nodes) = origin) = 1;

supply(nodes)$(ord(nodes) = destination) = -1;



free variable
    total_dist
;

integer variable
    flow(i,j)
;

flow.lo(i,j) = 0

equation
    balance(nodes)
    objective_shortestPath
    objective_safestPath
;


balance(i)..
    sum(arc(i,j), flow(i,j)) - sum(arc(j,i), flow(j,i)) =e= supply(i);
    
objective_shortestPath..
    total_dist =e= sum(arc(i,j),flow(i,j)*distance(i,j));

objective_safestPath..
    total_dist =e= sum(arc(i,j),flow(i,j)*crash(i,j));
    



model shortestPath /balance, objective_shortestPath/;

solve shortestPath using mip minimizing total_dist;

set roadChosen(roadID);

roadChosen(roadID) = no;

roadChosen(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosen(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

model safestPath /balance, objective_safestPath/;

solve safestPath using mip minimizing total_dist;
    
set roadChosenSafe(roadID);

roadChosenSafe(roadID) = no;

roadChosenSafe(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenSafe(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;


display roadChosen, roadChosenSafe;
