

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
$gdxin ../../turning_network_time_updated.gdx
$loadm nodes=dim1 nodes=dim2
parameter real_distance(nodes,nodes) distance of a road;
$load  real_distance=time
$gdxin

* load turn data
$gdxin ../../turning_network_turn_updated.gdx
parameter turn(nodes,nodes) distance of a road;
$load  turn=turn
$gdxin


* load updated risk factor
$gdxin ../../crash_drisk0320.gdx
parameter risk(nodes,nodes) distance of a road;
$load  risk=drisk
$gdxin

* load crash count
$gdxin ../../crash_count0320.gdx
parameter count(nodes,nodes) distance of a road;
$load  count=count
$gdxin



$gdxin ../../turning_network_linkID_updated.gdx
set road(roadID<,i,j);
$load  road=road
$gdxin



parameter distance(nodes,nodes);

distance(i,j) = real_distance(i,j)*99;

real_distance(i,j) = real_distance(i,j) + turn(i,j) - 1;



set arc(nodes,nodes);

arc(i,j) = no;
arc(i,j)$(distance(i,j) > 0.5) = yes;
* adjust the distance
distance(i,j)$(arc(i,j)) = distance(i,j) -1;

scalar
    turn_const /100/
    intermediate_val /10/
    Lambda /0.9/
    width just for record /0/ 
    height just for record /0/
            
;

Lambda = %lambda%;
width = %width%;
height = %height%;

parameter
    supply(nodes)
;

scalar origin,destination;
execseed = 1 + gmillisec(jnow);




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


set loopNum /l1*l50/;
set roadChosenIntermediate(roadID,loopNum);
parameter  stochastic(i,j), stochastic2(i,j), modelStatus(loopNum);
scalar stochasticLambda;

model weighted /balance, objective_shortestPath2/;


******** limit origin and destination *********
$include candidate_reference
*set originTest(nodes)/'1666494_1', '1666699_1', '1666490_1', '1666349_1', '1666498_1', '1666480_1', '1666500_1', '1666321_1', '1667144_1', '1666947_1', '1666504_1', '1665482_1', '1666295_1', '1665823_1', '1667085_1', '1666485_1', '1667503_1', '1665861_1', '1667037_1', '1666512_1', '1664609_1', '1666737_1', '1666421_1', '1666511_1', '1666648_1', '1666414_1', '1666688_1', '1666588_1', '1668086_1', '1666165_1', '1666285_1', '1666324_1', '1666642_1', '1668298_1', '1667300_1', '1667026_1', '1666584_1', '1666025_1', '2304262_1', '1667518_1', '1665153_1', '1668285_1', '1666984_1', '1666026_1', '1666509_1', '1666589_1', '1667774_1', '1667949_1', '1666907_1', '1666044_1'/;
*set destTest(nodes)/'1662728_1', '1662725_1', '1662771_1', '1662681_1', '1662738_1', '1662604_1', '1662673_1', '1662749_1', '1662569_1', '1662769_1', '1662591_1', '1662704_1', '1662536_1', '2067158_1', '1662751_1', '1662477_1', '1662631_1', '2020746_1', '1662494_1', '1662474_1', '1662481_1', '1662420_1', '1662841_1', '1662582_1', '1662431_1', '1662421_1', '1662857_1', '1662638_1', '1662437_1', '1662460_1', '1662784_1', '1662439_1', '1662813_1', '1662486_1', '2036953_1', '1662887_1', '1662416_1', '1662837_1', '1662440_1', '1662843_1', '2037747_1', '1662429_1', '1662220_1', '1663059_1', '1662944_1', '1662166_1', '1662835_1', '1662933_1', '1662303_1', '1662139_1'/;



set newOrigin(nodes);
set newDestin(nodes);
set originLoop(loopNum,i);
set destinationLoop(loopNum,i);
parameter outDistance(loopNum), outRisk(loopNum);


stochastic(i,j) = uniform(0.8,1.2);
stochastic2(i,j) = uniform(0.8,1.2);

distance(i,j) = real_distance(i,j)*99 * stochastic(i,j);
risk(i,j) = risk(i,j) * stochastic2(i,j);

loop( loopNum,
supply(nodes) = 0;
newOrigin(nodes) = no;
newDestin(nodes) = no;


embeddedCode Python:
    import random
    choice = random.choice(list(gams.get("originTest")))
    choice2 = random.choice(list(gams.get("destTest")))
    gams.set("newOrigin", [choice])
    gams.set("newDestin", [choice2])
endEmbeddedCode newOrigin, newDestin




supply(newOrigin) = 1;
supply(newDestin) = -1;
originLoop(loopNum,newOrigin) = yes;
destinationLoop(loopNum,newDestin) = yes;



solve weighted using mip minimizing total_dist;

*paretoRatioIntermediate = sum(arc(i,j),flow.l(i,j)*risk(i,j))/sum(arc(i,j),flow.l(i,j)*distance(i,j))
modelStatus(loopNum) = weighted.ModelStat;

outDistance(loopNum) = sum((i,j),flow.l(i,j) * distance(i,j));
outRisk(loopNum) = sum((i,j),flow.l(i,j) * risk(i,j));


roadChosenIntermediate(roadID,loopNum)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
*roadChosenIntermediate(roadID,loopNum)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;

);

*supply(nodes) = 0;
*roadChosenIntermediate(roadID,'l50')= no;
*supply('1666494_1') = 1;
*supply('1662728_1') = -1;
*solve weighted using mip minimizing total_dist;
*roadChosenIntermediate(roadID,'l50')$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;

execute_unload 'trajectories_local.gdx', roadChosenIntermediate, Lambda, outDistance, outRisk, originLoop, destinationLoop, width, height, modelStatus;


