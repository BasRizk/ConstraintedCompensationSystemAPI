:- use_module(library(clpfd)).

schedule(SLOTS, DAYOFF, PREFERED_DAYS, GROUPS):-
    ensure_slots(SLOTS, DAYOFF),
    %  The schedules of the tutorial groups. A group can not be assigned 
    % to multiple meetings at the same time.
    chain_per_group(SLOTS, GROUPS).


chain_per_group(SLOTS, [GROUP|GROUPS]):-
    list_group_timings(SLOTS, GROUP, TIMINGS_LIST),
    chain(TIMINGS_LIST, "<"),
    chain_per_group(SLOTS, GROUPS).

list_group_timings([],_,[]).
list_group_timings([SLOT|SLOTS], TARGET_GROUP, [TIME|TIMINGS_LIST]):-
    SLOT = (NUM, _, _, GROUP),
    GROUP = TARGET_GROUP,
    TIME = NUM,
    list_group_timings(SLOTS, GROUP, TIMINGS_LIST).

% Ensure slots structure, and NUM validaty
ensure_slots([], _).
ensure_slots([SLOT|SLOTS], DAYOFF):-
    SLOT = (NUM, SUBJECT, TYPE, GROUP),
    (
        (NUM in 5..29, DAYOFF == 1);
        (NUM in 0..24, DAYOFF == 6);
        (NUM in 0..4\/10..29, DAYOFF = 2);
        (NUM in 0..9\/15..29, DAYOFF = 3);
        (NUM in 0..14\/20..29, DAYOFF = 4);
        (NUM in 0..19\/25..29, DAYOFF = 5)
    ),
    nonvar(SUBJECT),
    nonvar(TYPE),
    nonvar(GROUP),
    ensure_slots(SLOTS, DAYOFF).

% Return the resource amount of a subject based on its type
% Basically number of rooms
% TODO Maybe edit according to priority somehow later
get_room_resource(lab, 8).
get_room_resource(tut, 50).
get_room_resource(big_lec, 5).
get_room_resource(small_lec, 1).
   

% set_tasks_per_group(_,[],[]).
% set_tasks_per_group(SLOTS, [GROUP|GROUPS], [TASKS|LIST_OF_TASKS]):-
%     set_tasks_of_group(SLOTS, GROUP, TMP_TASKS),
%     set_tasks_per_group(SLOTS, GROUPS, LIST_OF_TASKS).


% set_tasks_of_group([],_,[]).
% % Ignore slot if it is not from the target_group
% set_tasks_of_group([SLOT|SLOTS], TARGET_GROUP, TASKS):-
%     SLOT = (_, _, _, GROUP),
%     GROUP \= TARGET_GROUP,
%     set_tasks_of_group(SLOTS, TARGET_GROUP, TASKS).
% % Create a task of a slot if it is of that target_group
% set_tasks_of_group([SLOT|SLOTS], TARGET_GROUP, [TASK|TASKS]):-
%     SLOT = (NUM, SUBJECT, TYPE, GROUP),
%     GROUP = TARGET_GROUP,
%     TASK = (S1, _, _, 1, _),
%     set_tasks_of_group(SLOTS, TARGET_GROUP, TASKS).


% Rooms : 50
% Large halls (capacity 230) : 5
% Small halls (capacity 100) :1
% Computer labs : 8

% VARIABLES:
% A SLOT is to be assigned to a location {ROOM, SMALL_HALL, BIG_HALL, LAB} (if possible)
% if a slot cannot be a signed to a location, along the rest of the constraints
% that means that it cannot be there.
% Another then with different -- NUM -- should be used!
% 
    % A SLOT can be identified as (NUM, SUBJECT, TYPE, GROUP)
    % EX (3, GRAPHICS, LAB, 7 CSEN T18)
% 
% NUM: {0..29} .. 5X6
% 
% SUBJECT: Any sort of subject
% 
% TYPE: {LAB, SMALL_LEC, BIG_LEC, TUT}
% 
% GROUP: Any sort of group...
% ex. 7 CSEN is considered as different group than the more specific group 7 CSEN T18
% 
% ANOTHER OPTION FOR GROUP: is to contain GROUP and SUBGROUP
% where then (7CSEN, L1) is lecture group for example, and (7CSEN, T18) is more specific group example

% CONSTRAINTS:
% 
% 1. Conflicts
%  The schedules of the faculty members. A staff member can not be assigned to multiple meetings at
% the same time.
% -- (NOT EVEN REFERED TO ANYWHERE, MAYBE SOLVABLE IF BASED ON CHOICES OF INPUTS! AKA ANOTHER INTERSECTED SCHEDULE)
%  The schedules of the rooms. A room can not be assigned to multiple meetings at the same time.
% -- (CAN BE SATISIFIED STRAIGHT FORWARDLY BY THE MODEL ABOVE)
% 
% 2. Meeting types -- Assign TYPE LAB to lab resource only
% A lab should not be scheduled in a classroom.
% 
% 3. Room Type Optimization -- Prioritize usage of non-labs to non-labs
% To make sure resources are used in an optimal way, a tutorial should not be held in a lab unless that
% would make the instance solvable.
% 
% 4. Different Calendars -- Either, consider it in the backend before giving the query or split GROUP var!
% It is possible that different study groups have different calendars. It is for example possible that 1st year
% students start two weeks after continuing students. In that case, it should be possible to use the rooms
% of the meetings of the first year students during the first two weeks in any needed compensation.
% 
% 5. Perserving days-off -- (Where can we find those?)*
% -- maybe add prefer addition on already busy days, by adding some weights and trying to max. that! -- 
% The system should make sure that the weekly off-days of the groups and the faculty members are preseved
% as much as possible.
% 
% 6. Perferences -- (UI requirement)*
% A faculty member should be able to use the interface to insert the slots in which prefer/ do not prefer to
% have the compensations in. The system should try to satisfy the preferences as much as possible.


% 
% The rooms/halls/labs are counted for each semester alone then summed up at the end of each sheet.
% For your project, the maximum locations available per slot should be as follows:
% Rooms : 50
% Large halls (capacity 230) : 5
% Small halls (capacity 100) :1
% Computer labs : 8
% 
