$title shortest path try

option limcol = 0, limrow = 0, solprint = off;
set
    nodes
;

alias (nodes,i,j);
$gdxin ../link_file.gdx
$loadm nodes=dim1 nodes=dim2
parameter distance(nodes,nodes);
$load  distance=link
$gdxin

set arc(nodes,nodes);

arc(i,j) = no;
arc(i,j)$(distance(i,j) > 0.5) = yes;

parameter
    supply(nodes)
;

supply(nodes) = 0;
supply('1661704') = 1;

supply('1665614') = -1;

free variable
    total_dist
;

positive variable
    flow(i,j)
;

equation
    balance(nodes)
    objective_shortestPath
;


balance(i)..
    sum(arc(i,j), flow(i,j)) - sum(arc(j,i), flow(j,i)) =e= supply(i);
    
objective_shortestPath..
    total_dist =e= sum(arc(i,j),flow(i,j)*distance(i,j));
    


    


model shortestPath /all/;

solve shortestPath using lp minimizing total_dist;
    
set
    resultArcs(i,j);
resultArcs(i,j) = no;
resultArcs(i,j)$(flow.l(i,j) > 0.5) = yes;

display resultArcs;
