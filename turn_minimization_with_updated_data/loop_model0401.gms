
$title turning network

option limcol = 0, limrow = 0, solprint = off;
set
    nodes
    roadID
    season
    seriousness
;

alias (nodes,i,j);
$gdxin ../turning_network_time_updated.gdx
$loadm nodes=dim1 nodes=dim2
parameter real_distance(nodes,nodes) distance of a road;
$load  real_distance=time
$gdxin


$gdxin ../turning_network_turn_updated.gdx
parameter turn(nodes,nodes) distance of a road;
$load  turn=turn
$gdxin

$gdxin ../crash_drisk0320.gdx
parameter risk(nodes,nodes) distance of a road;
$load  risk=drisk
$gdxin

$gdxin ../crash_count0320.gdx
parameter count(nodes,nodes) distance of a road;
$load  count=count
$gdxin

*display distance;


$gdxin ../turning_network_linkID_updated.gdx
set road(roadID<,i,j);
$load  road=road
$gdxin



$ontext
$gdxin ../crash_file.gdx
parameter  crash(nodes,nodes) number of crashes on a road;
$load  crash=crash
$gdxin
$offtext

$ontext
$gdxin ../crash_seriousness.gdx
$load season=dim3 seriousness=dim4
parameter crashS(nodes,nodes,season,seriousness) number of crashes on a road with different seasons and seriousness;
$load  crashS=serious_crash
$gdxin
$offtext

parameter distance(nodes,nodes);

distance(i,j) = real_distance(i,j);


set arc(nodes,nodes);

arc(i,j) = no;
arc(i,j)$(distance(i,j) > 0.5) = yes;
* adjust the distance
distance(i,j)$(arc(i,j)) = distance(i,j) -1;

scalar
    turn_const /100/
    intermediate_val /10/
;

parameter
    supply(nodes)
;

scalar origin,destination;
execseed = 1 + gmillisec(jnow);
origin = uniformint(1,card(nodes));
destination = uniformint(1,card(nodes));

*supply(nodes)$(ord(nodes) = origin) = 1;

*supply(nodes)$(ord(nodes) = destination) = -1;

supply('1666494_2') = 1;
supply('1662728_3') = -1;

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
    objective_shortestPath2
    objective_short "shortest path formulation"
    intermediate_constr
    turn_constr
;


balance(i)..
    sum(arc(i,j), flow(i,j)) - sum(arc(j,i), flow(j,i)) =e= supply(i);
    
objective_short..
    total_dist =e= sum(arc(i,j),flow(i,j)*distance(i,j));
**********************************************************

intermediate_constr..
    sum(arc(i,j),flow(i,j)*risk(i,j)) =l= intermediate_val;
********************************************************** 

objective_shortestPath..
    total_dist =e= sum(arc(i,j),flow(i,j)*turn(i,j));

objective_shortestPath2..
    total_dist =e= sum(arc(i,j),flow(i,j)*distance(i,j) + 0*flow(i,j)*turn(i,j));
    


    
turn_constr..
    sum(arc(i,j),flow(i,j)*turn(i,j)) =l= turn_const;


model seasonalPath /balance, objective_shortestPath/;

model seasonalPath2 /balance, objective_shortestPath2, turn_constr/;

model shortest /balance, objective_short/;

model intermediate /balance, objective_short, intermediate_constr/;


***risk model

distance(i,j) = risk(i,j);

solve shortest using mip minimizing total_dist;

set roadChosenRisk(roadID);

scalar 
    roadChosenRisk_risk
;

roadChosenRisk(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenRisk(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

roadChosenRisk_risk = sum(arc(i,j),flow.l(i,j)*risk(i,j));

***crash count model
distance(i,j) = count(i,j);

solve shortest using mip minimizing total_dist;

set roadChosenCount(roadID);

roadChosenCount(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenCount(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

*** pure distance model
distance(i,j) = real_distance(i,j);

solve shortest using mip minimizing total_dist;

set roadChosenDistance(roadID);

scalar 
    roadChosenDistance_risk
;

roadChosenDistance(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenDistance(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

roadChosenDistance_risk = sum(arc(i,j),flow.l(i,j)*risk(i,j));
*** turn model

distance(i,j) = turn(i,j);

solve shortest using mip minimizing total_dist;

set roadChosenTurn(roadID);

roadChosenTurn(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenTurn(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

*solve seasonalPath2 using mip minimizing total_dist;

*** intermediate model

distance(i,j) = real_distance(i,j);

intermediate_val = (0.2*roadChosenDistance_risk+1.8*roadChosenRisk_risk)/2;

solve intermediate using mip minimizing total_dist;

set roadChosenIntermediate(roadID);

roadChosenIntermediate(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenIntermediate(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;



*** loop intermediate model

scalar Lambda /0.1/;
set loopN/ l1*l9/;

set roadChosenIntermediateLoop(loopN,roadID);



loop( loopN,
    intermediate_val = Lambda* ord(loopN)*roadChosenDistance_risk+ (1-Lambda*ord(loopN))*roadChosenRisk_risk;
    solve intermediate using mip minimizing total_dist;
    
    roadChosenIntermediateLoop(loopN,roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
    roadChosenIntermediateLoop(loopN,roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;
);






