:- use_module(library(clpfd)).
% A SLOT is to be assigned to a LOCATION and a NUM (if possible), Or it cannot exist
% 
% VARIABLES:
% 
% A SLOT = (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION, TEACHER)
% EX (3, GRAPHICS, LAB, 7 CSEN, 7 CSEN T18, 1)
% 
% NUM: {0..29} .. 5X6
% 
% SUBJECT: Any sort of subject
% 
% TYPE: {LAB, SMALL_LEC, BIG_LEC, TUT}
% 
% GROUP: The group taken the course (ex. 7 CSEN)
% 
% SUBGROUP: The subgroup represents the tut. lab. or a lec. group (basically repeated) (ex. 7 CSEN T18)
%
% LOCATION: {0..63}, where 0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs  
% 
% CONSTRAINTS: DOWN BELOW  ||
%                          \/
% 

schedule(SLOTS, HOLIDAY, SUBJECTS, GROUPS, SUBGROUPS):-
    % TODO Maybe SUBJECTS, GROUPS, and SUBGROUPS 
    print("Began"), nl,
    
    % Extract variables for labeling later
    extract_variable_slots(SLOTS, VARIABLES),
    % print("VARIABLES = "), print(VARIABLES), nl,

    % => The schedules of the tutorial groups. A group can not be assigned 
    % to multiple meetings at the same time.
    ensure_slots(SLOTS, HOLIDAY),
    % print("SLOTS ENSURED"), nl,

    % (TIMING, SUBGROUP)
    % No subgroup have more than one slot at the same time
    % Implicitly no lecture at the same time of corresponding tut. ensured
    serialize_subgroups(SLOTS, SUBGROUPS),
    % print("SUBGROUPS SERIALIZED"), nl,

    % (TIMING, TYPE, GROUP)
    % No more than one lec given to the same group at the same time
    serialize_lecs_per_group(SLOTS, GROUPS),
    % print("LEC SERIALIZED PER EACH GROUP"), nl,
    
    % (TIMING, TEACHER)
    % A staff member can not be assigned to multiple meetings at the same time.
    no_slots_assigned_same_teacher(SLOTS),
    % print("NO OVERLAPING-TEACHER ENSURED"), nl,

    % (TIMING, LOCATION)
    % A room can not be assigned to multiple meetings at the same time.
    % No slot at the same location at the same time
    % Ensure allocation of resources
    ensure_allocation(SLOTS, LOCATION_TOTAL_COST),
    no_slots_at_same_location(SLOTS),
    % print("ALLOCATION ENSURED"), nl,

    labeling([min(LOCATION_TOTAL_COST)], VARIABLES).

/**
 * Extract variable slots 
 */
extract_variable_slots([], []).
extract_variable_slots([SLOT|SLOTS], VAR_SLOTS):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    nonvar(NUM), nonvar(LOCATION),
    extract_variable_slots(SLOTS, VAR_SLOTS).
extract_variable_slots([SLOT|SLOTS], [NUM, LOCATION|VAR_SLOTS]):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    var(NUM), var(LOCATION),
    extract_variable_slots(SLOTS, VAR_SLOTS).

/**
 * Ensure slots structure, and NUM of slot validity
 */
ensure_slots([], _).
ensure_slots([SLOT|SLOTS], HOLIDAY):-
    SLOT = (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, _, _),
    (
        (HOLIDAY = 0, NUM in 5..29);
        (HOLIDAY = 5, NUM in 0..24);
        (HOLIDAY = 1, NUM in 0..4\/10..29);
        (HOLIDAY = 2, NUM in 0..9\/15..29);
        (HOLIDAY = 3, NUM in 0..14\/20..29);
        (HOLIDAY = 4, NUM in 0..19\/25..29)
    ),
    nonvar(SUBJECT),
    nonvar(TYPE),
    nonvar(GROUP),
    nonvar(SUBGROUP),
    ensure_slots(SLOTS, HOLIDAY).

/**
 * No two slots at the same time placed the same location
 */
no_slots_at_same_location(SLOTS):-
    all_different_locations_per_slot(29, SLOTS).  

all_different_locations_per_slot(-1,_).
all_different_locations_per_slot(NUM, SLOTS):-
    NUM >= 0,
    extract_locations_of_same_time_slots(NUM , SLOTS, LOCATIONS),
    all_distinct(LOCATIONS),
    NEW_NUM #= NUM - 1, 
    all_different_locations_per_slot(NEW_NUM, SLOTS).

extract_locations_of_same_time_slots(_, [] ,[]).
extract_locations_of_same_time_slots(TARGET_NUM, [SLOT|SLOTS], [LOCATION|LOCATIONS]):-  
    SLOT = (NUM,_,_,_,_,LOCATION, _), 
    NUM #= TARGET_NUM,
    extract_locations_of_same_time_slots(TARGET_NUM, SLOTS, LOCATIONS).
extract_locations_of_same_time_slots(TARGET_NUM, [SLOT|SLOTS], LOCATIONS):-
    SLOT = (ANOTHER_NUM,_,_,_,_,_,_),
    ANOTHER_NUM #\= TARGET_NUM,
    extract_locations_of_same_time_slots(TARGET_NUM, SLOTS, LOCATIONS).

/**
 * No two slots at the same time are assigned to the same TEACHER.
 */
no_slots_assigned_same_teacher(SLOTS):-
    all_different_teachers_per_slot(29, SLOTS).  

all_different_teachers_per_slot(-1,_).
all_different_teachers_per_slot(NUM, SLOTS):-
    NUM >= 0,
    extract_teachers_of_same_time_slots(NUM , SLOTS, TEACHERS),
    all_distinct(TEACHERS),
    NEW_NUM #= NUM - 1, 
    all_different_teachers_per_slot(NEW_NUM, SLOTS).

extract_teachers_of_same_time_slots(_, [] ,[]).
extract_teachers_of_same_time_slots(TARGET_NUM, [SLOT|SLOTS], [TEACHER|TEACHERS]):-  
    SLOT = (NUM,_,_,_,_,_,TEACHER), 
    NUM #= TARGET_NUM,
    extract_teachers_of_same_time_slots(TARGET_NUM, SLOTS, TEACHERS).
extract_teachers_of_same_time_slots(TARGET_NUM, [SLOT|SLOTS], TEACHERS):-
    SLOT = (ANOTHER_NUM,_,_,_,_,_,_),
    ANOTHER_NUM #\= TARGET_NUM,
    extract_teachers_of_same_time_slots(TARGET_NUM, SLOTS, TEACHERS).

/**
 * Ensure allocation
 * 1. Meeting types -- Assign TYPE LAB to lab resource only
 * 2. Room Type Optimization -- Prioritize usage of non-labs to non-labs
 * LOCATION: {0..63}, where 0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs 
 */
location_cost(lab, LOCATION, COST):-
    (LOCATION in 56..63, COST #= 1);
    (LOCATION in 0..49, COST #= 2).
location_cost(tut, LOCATION, COST):-
    (LOCATION in 0..49, COST #= 1);
    (LOCATION in 56..63, COST #= 2).
location_cost(small_lec, LOCATION, COST):-
    (LOCATION in 55..55, COST #= 1);
    (LOCATION in 50..54, COST #= 2).
location_cost(big_lec, LOCATION, 1):-
    LOCATION in 50..54.

ensure_allocation([], 0).
ensure_allocation([SLOT|SLOTS], TOTAL_COST):-
    TOTAL_COST #= (OLD_COST + SINGLE_COST),
    ensure_allocation(SLOTS, OLD_COST),
    SLOT = (_, _, TYPE, _, _, LOCATION,_),
    location_cost(TYPE, LOCATION, SINGLE_COST).

/**
 * Return list of ones of equal length
 */
corresponding_list_of_ones([], []).
corresponding_list_of_ones([_|Xs], [1|ONES]):-
    corresponding_list_of_ones(Xs, ONES).

/**
 * Serialize lectures for each group
 */
serialize_lecs_per_group(_,[]).
serialize_lecs_per_group(SLOTS, [GROUP|GROUPS]):-
    serialize_lecs_per_group(SLOTS, GROUPS),
    % Once as there are two many possiblities of the same permutation of the timing_list
    % because of - TYPE does not equal or group does not equal - line
    once(list_lec_group_timings(SLOTS, GROUP, TIMINGS_LIST)),
    corresponding_list_of_ones(TIMINGS_LIST, ONES),
    serialized(TIMINGS_LIST, ONES).

list_lec_group_timings([],_,[]).
list_lec_group_timings([SLOT|SLOTS], TARGET_GROUP, TIMINGS_LIST):-
    list_lec_group_timings(SLOTS, TARGET_GROUP, TIMINGS_LIST),
    SLOT = (_, _, TYPE, GROUP, _, _, _),
    (TYPE \= small_lec; TYPE \= big_lec; GROUP \= TARGET_GROUP).
list_lec_group_timings([SLOT|SLOTS], TARGET_GROUP, [TIME|TIMINGS_LIST]):-
    list_lec_group_timings(SLOTS, TARGET_GROUP, TIMINGS_LIST),
    SLOT = (TIME, _, TYPE, TARGET_GROUP, _, _, _),
    (TYPE = small_lec; TYPE = big_lec).

/**
 * Serialize all types of slots for each subgroup
 */
serialize_subgroups(_,[]).
serialize_subgroups(SLOTS, [SUBGROUP|SUBGROUPS]):-
    serialize_subgroups(SLOTS, SUBGROUPS),
    list_subgroup_timings(SLOTS, SUBGROUP, TIMINGS_LIST),
    corresponding_list_of_ones(TIMINGS_LIST, ONES),
    serialized(TIMINGS_LIST, ONES).

list_subgroup_timings([],_,[]).
list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, TIMINGS_LIST):-
    SLOT = (_, _, _, _, SUBGROUP, _, _),
    SUBGROUP \= TARGET_SUBGROUP,
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).

list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, [TIME|TIMINGS_LIST]):-
    SLOT = (TIME, _, _, _, TARGET_SUBGROUP, _, _),
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).



% CONSTRAINTS:
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
