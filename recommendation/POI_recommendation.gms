$title POI recommendation

set nodes
/'n_x0_y0',
 'n_x0_y1',
 'n_x0_y2',
 'n_x0_y3',
 'n_x1_y0',
 'n_x1_y1',
 'n_x1_y2',
 'n_x1_y3',
 'n_x2_y0',
 'n_x2_y1',
 'n_x2_y2',
 'n_x2_y3',
 'n_x3_y0',
 'n_x3_y1',
 'n_x3_y2',
 'n_x3_y3',
 'n_x4_y0',
 'n_x4_y1',
 'n_x4_y2',
 'n_x4_y3'/;
 
set arcs(nodes,nodes);

parameter edge_record(nodes,nodes)/
$ondelim
$include arcs.csv
$offdelim
/;

alias(nodes,i,j);

arcs(i,j) = no;

arcs(i,j)$(edge_record(i,j) > 0.5)= yes;

parameter edge_weight(nodes,nodes)/
$ondelim
$include edge_weight.csv
$offdelim
/;

parameter blue(nodes);
blue(nodes) = 0;
blue('n_x0_y3') = 1;
blue('n_x4_y2') = 1;

parameter green(nodes);
green(nodes) = 0;
green('n_x2_y0') = 1;
green('n_x2_y1') = 1;

parameter purple(nodes);
purple(nodes) = 0;
purple('n_x2_y3') = 1;
purple('n_x3_y0') = 1;
purple('n_x4_y0') = 1;

parameter supply(nodes);
supply('n_x0_y0') = 1;
supply('n_x4_y3') = -1;


binary variable
    flow(nodes,nodes)
    choice(i)
;
    

flow.l(i,j) = 0;

free variable
    obj
;

equation
    networkFlow(i)
    choice_constr(i)
    blue_demand
    green_demand
    purple_demand
    objective
;

networkFlow(i)..
    sum(j$arcs(i,j), flow(i,j)) - sum(j$arcs(j,i), flow(j,i)) =e= supply(i);
    

choice_constr(i)..
    sum(j$arcs(i,j), flow(i,j)) + sum(j$arcs(j,i), flow(j,i)) =g= choice(i);
    

blue_demand..
    sum(i,choice(i)*blue(i)) =g= 1;

green_demand..
    sum(i,choice(i)*green(i)) =g= 1;
    
purple_demand..
    sum(i,choice(i)*purple(i)) =g= 1;
    
objective..
    obj =e= sum((i,j)$arcs(i,j), flow(i,j) * edge_weight(i,j)) + sum(i,choice(i));


model POI/all/;

solve POI using mip minizing obj;

display flow.l, choice.l;





