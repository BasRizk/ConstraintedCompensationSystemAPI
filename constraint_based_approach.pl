:- use_module(library(clpfd)).
:- include('util.pl').
% A SLOT is to be assigned to a LOCATION and a NUM (if possible), Or it cannot exist
% 
% VARIABLES:
% 
% A SLOT = (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
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
    % => The schedules of the tutorial groups. A group can not be assigned 
    % to multiple meetings at the same time.
    ensure_slots(SLOTS, HOLIDAY),
    print("SLOTS ENSURED"), nl,

    % (TIMING, LOCATION)
    % => The schedules of the rooms. A room can not be assigned to multiple meetings at the same time.
    % No slot at the same location at the same time
    % Ensure allocation of resources
    ensure_allocation(SLOTS),
    check_all_slots_diffLocations(SLOTS),
    print("ALLOCATION ENSURED"), nl,
    
    % % (TIMING, SUBGROUP)
    % % No subgroup have more than one slot at the same time
    % % Implicitly no lecture at the same time of corresponding tut. ensured
    chain_per_subgroup(SLOTS, SUBGROUPS),
    print("CHAINED PER SUBGROUPS ENSURED"), nl,

    % % % (TIMING, SUBJECT, TYPE, GROUP)
    % % % No more than one lec given to the same group at the same time
    chain_lec_per_group(SLOTS, GROUPS),
    print("CHAINED LEC PER GROUP SAME SUBJECT ENSURED"), nl.


/**
 * Ensure allocation
 * 1. Meeting types -- Assign TYPE LAB to lab resource only
 * 2. Room Type Optimization -- Prioritize usage of non-labs to non-labs
 * LOCATION: {0..63}, where 0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs  
 */
ensure_allocation([]).
ensure_allocation([SLOT|SLOTS]):-
    % PRIORITIZED OPTIMAL SOLUTION
    SLOT = (_, _, TYPE, _, _, LOCATION),
    (
        (TYPE = lab, LOCATION in 56..63);
        (TYPE = big_lec, LOCATION in 50..54);
        (TYPE = small_lec, LOCATION in 55..55);
        (TYPE = tut, LOCATION in 0..49)
    ),
    ensure_allocation(SLOTS).
ensure_allocation([SLOT|SLOTS]):-
    % POSSIBLE ANSWER ALSO
    SLOT = (_, _, TYPE, _, _, LOCATION),
    (
        (TYPE = small_lec, LOCATION in 50..55);
        (TYPE = tut, LOCATION in 0..63);
        % TODO DELETE
        (TYPE = lab, LOCATION in 0..49)
    ),
    ensure_allocation(SLOTS).

/**
 * Return list of ones of equal length
 */
corresponding_list_of_ones([], []).
corresponding_list_of_ones([_|Xs], [1|ONES]):-
    corresponding_list_of_ones(Xs, ONES).

/**
 * Chain lectures of the same group for each group
 * 
 */
chain_lec_per_group(_,[]).
chain_lec_per_group(SLOTS, [GROUP|GROUPS]):-
    list_lec_group_timings(SLOTS, GROUP, TIMINGS_LIST),
    corresponding_list_of_ones(TIMINGS_LIST, ONES), serialized(TIMINGS_LIST, ONES),
    chain_lec_per_group(SLOTS, GROUPS).

list_lec_group_timings([],_,[]).
list_lec_group_timings([SLOT|SLOTS], TARGET_GROUP, TIMINGS_LIST):-
    SLOT = (_, _, TYPE, GROUP, _, _),
    (TYPE \= small_lec; TYPE \= big_lec; GROUP \= TARGET_GROUP),
    list_lec_group_timings(SLOTS, TARGET_GROUP, TIMINGS_LIST).
list_lec_group_timings([SLOT|SLOTS], TARGET_GROUP, [TIME|TIMINGS_LIST]):-
    SLOT = (TIME, _, TYPE, TARGET_GROUP, _, _),
    (TYPE = small_lec; TYPE = big_lec),
    list_lec_group_timings(SLOTS, TARGET_GROUP, TIMINGS_LIST).


/**
 * Chain all types of slots for each subgroup
 */
chain_per_subgroup(_,[]).
chain_per_subgroup(SLOTS, [SUBGROUP|SUBGROUPS]):-
    list_subgroup_timings(SLOTS, SUBGROUP, TIMINGS_LIST),
    corresponding_list_of_ones(TIMINGS_LIST, ONES), serialized(TIMINGS_LIST, ONES),
    chain_per_subgroup(SLOTS, SUBGROUPS).

list_subgroup_timings([],_,[]).
list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, TIMINGS_LIST):-
    SLOT = (_, _, _, _, SUBGROUP, _),
    SUBGROUP \= TARGET_SUBGROUP,
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).

list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, [TIME|TIMINGS_LIST]):-
    SLOT = (TIME, _, _, _, TARGET_SUBGROUP, _),
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).

/**
 * Ensure slots structure, and NUM of slot validity
 * 
 */
ensure_slots([], _).
ensure_slots([SLOT|SLOTS], HOLIDAY):-
    SLOT = (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, _),
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

% CONSTRAINTS:
% 
% 1. Conflicts
%  The schedules of the faculty members. A staff member can not be assigned to multiple meetings at
% the same time.
% -- (NOT EVEN REFERED TO ANYWHERE, MAYBE SOLVABLE IF BASED ON CHOICES OF INPUTS! AKA ANOTHER INTERSECTED SCHEDULE)
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
