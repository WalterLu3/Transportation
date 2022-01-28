
$title shortest path try

option limcol = 0, limrow = 0, solprint = off;
set
    nodes
    roadID
    season
    seriousness /K, A, B, C, O/;
;

parameter seriousnessScore(seriousness)
    /
        K 10
        A 8
        B 3
        C 2
        O 1
    /;


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

$gdxin ../crash_seriousness.gdx
$load season=dim3
parameter crashS(nodes,nodes,season,seriousness) number of crashes on a road with different seasons and seriousness;
$load  crashS=serious_crash
$gdxin


$gdxin ../link_speed.gdx
parameter speed(nodes,nodes) number of crashes on a road with different seasons and seriousness;
$load  speed=speed
$gdxin

distance(i,j)$(distance(i,j) > 0) = distance(i,j)/speed(i,j);



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

*supply(nodes)$(ord(nodes) = origin) = 1;

*supply(nodes)$(ord(nodes) = destination) = -1;

supply('1664291') = 1;
supply('1662117') = -1;

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
    total_dist =e= sum(arc(i,j),flow(i,j)*distance(i,j) + 10000*flow(i,j)*crash(i,j));



model seasonalPath /balance, objective_shortestPath/;


set roadChosen(season,roadID);

roadChosen(season,roadID) = no;

parameter
        tempCrash(roadID)
        seasonLength(season)
        seasonCrash(season);

scalar total;
parameter  originalCrash(nodes,nodes);

loop(season,
* using crash number as edge weights
crash(i,j) = sum((seriousness), seriousnessScore(seriousness)*crashS(i,j,season,seriousness));
originalCrash(i,j) = sum((seriousness), 1*crashS(i,j,season,seriousness));


solve seasonalPath using mip minimizing total_dist;

roadChosen(season,roadID)$( sum(road(roadID,i,j), flow.l(i,j)) > 0.5) = yes;
roadChosen(season,roadID)$( sum(road(roadID,i,j), flow.l(j,i)) > 0.5) = yes;
seasonLength(season) = sum(road(roadID,i,j)$roadChosen(season,roadID), distance(i,j));
seasonCrash(season) = sum(road(roadID,i,j)$roadChosen(season,roadID), originalCrash(i,j));

);



display seasonCrash;
*display seasonCrash;



