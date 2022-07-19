

$title network

option limcol = 0, limrow = 0, solprint = off;
set
    nodes
    roadID
    season
    seriousness
;

alias (nodes,i,j);

* load traveling time on network
$gdxin ../turning_network_time_updated.gdx
$loadm nodes=dim1 nodes=dim2
parameter real_distance(nodes,nodes) distance of a road;
$load  real_distance=time
$gdxin

* load turn data
$gdxin ../turning_network_turn_updated.gdx
parameter turn(nodes,nodes) distance of a road;
$load  turn=turn
$gdxin


* load updated risk factor
$gdxin ../crash_drisk0320.gdx
parameter risk(nodes,nodes) distance of a road;
$load  risk=drisk
$gdxin

* load crash count
$gdxin ../crash_count0320.gdx
parameter count(nodes,nodes) distance of a road;
$load  count=count
$gdxin



$gdxin ../turning_network_linkID_updated.gdx
set road(roadID<,i,j);
$load  road=road
$gdxin



parameter distance(nodes,nodes);

distance(i,j) = real_distance(i,j);

real_distance(i,j) = real_distance(i,j) + turn(i,j) - 1;

set arc(nodes,nodes);

arc(i,j) = no;
arc(i,j)$(distance(i,j) > 0.5) = yes;
* adjust the distance
distance(i,j)$(arc(i,j)) = distance(i,j) -1;

scalar
    turn_const /100/
    intermediate_val /10/
    Lambda /0.1/;
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


* starting point for paper
 supply('1666494_2') = 1;


* ending point for paper
 supply('1662728_3') = -1;

*supply('1664156_1') = 1;
*supply('2212306_1') = -1;

*supply('10949_1') = 1;
*supply('2212306_1') = -1;


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
    total_dist =e= sum(arc(i,j),Lambda*flow(i,j)*distance(i,j) + (1-Lambda)*flow(i,j)*risk(i,j) + flow(i,j)*turn(i,j));
    


    
turn_constr..
    sum(arc(i,j),flow(i,j)*turn(i,j)) =l= turn_const;


set loopNum /l1*l100/;
set roadChosenIntermediate(roadID,loopNum);
parameter  stochastic(i,j), stochastic2(i,j);
scalar stochasticLambda;

model weighted /balance, objective_shortestPath2/;

loop( loopNum,

** stochastic component

stochastic(i,j) = uniform(0.2,1.8);
stochastic2(i,j) = uniform(0.2,1.8);
stochasticLambda = uniform(0,1);


*** intermediate model

*scalar paretoRatioDistance, paretoRatioRisk, paretoRatioIntermediate;

*distance(i,j) = real_distance(i,j);
distance(i,j) = real_distance(i,j)*stochastic(i,j);
risk(i,j) = risk(i,j) * stochastic2(i,j);

*intermediate_val = (0.2*roadChosenDistance_risk+1.8*roadChosenRisk_risk)/2;


Lambda = stochasticLambda;

solve weighted using mip minimizing total_dist;

*paretoRatioIntermediate = sum(arc(i,j),flow.l(i,j)*risk(i,j))/sum(arc(i,j),flow.l(i,j)*distance(i,j))



roadChosenIntermediate(roadID,loopNum)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
*roadChosenIntermediate(roadID,loopNum)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

);

execute_unload 'trajectories_100.gdx', roadChosenIntermediate;


$ontext
Lambda = 1;

solve weighted using mip minimizing total_dist;

paretoRatioDistance = sum(arc(i,j),flow.l(i,j)*risk(i,j))/sum(arc(i,j),flow.l(i,j)*distance(i,j))
set roadChosenDistance(roadID);

roadChosenDistance(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenDistance(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

Lambda = 0;


solve weighted using mip minimizing total_dist;


paretoRatioRisk = sum(arc(i,j),flow.l(i,j)*risk(i,j))/sum(arc(i,j),flow.l(i,j)*distance(i,j))
set roadChosenRisk(roadID);

roadChosenRisk(roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosenRisk(roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;
$offtext
