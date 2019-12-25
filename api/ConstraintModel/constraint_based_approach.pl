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

schedule(SLOTS, HOLIDAYS, _, _, SUBGROUPS):-
    print("Began"), nl,

    % => Extract variables for labeling later
    extract_variables(SLOTS, VARIABLES),
    print("VARIABLES = "), print(VARIABLES), nl,

    % => Ensuring Domains
    % (TIMING, HOLIDAY)
    % Ensure proper domains on slots timings
    ensure_slots(SLOTS, HOLIDAYS),
    print("TIMINGS DOMAIN ENSURED"), nl,
    % (TIMING, LOCATION)
    % Ensure allocation of resources
    ensure_allocation(SLOTS, LOCATION_TOTAL_COST),
    print("LOCATIONS DOMAIN ENSURED"), nl,

    % => A group can not be assigned to multiple meetings at the same time.
    % (TIMING, SUBJECT(lec), SUBJECT_i_(nonlec))
    % No group assigned a lec and some tut. or lab at the same time of the same subject
    serialize_each_lec_with_its_companions(SLOTS),
    print("EACH LECS SERAILIZED WITH EACH OF ITS COMPANIONS"), nl,
    % (TIMING, SUBGROUP)
    % No subgroup have more than one slot at the same time
    % Implicitly no lecture at the same time of corresponding tut. ensured
    serialize_subgroups(SLOTS, SUBGROUPS),
    print("SUBGROUPS SERIALIZED"), nl,
    
    % (TIMING, TEACHER)
    % A staff member can not be assigned to multiple meetings at the same time.
    no_slots_assigned_same_teacher(SLOTS),
    print("NO OVERLAPING-TEACHER ENSURED"), nl,

    % (TIMING, LOCATION)
    % A room can not be assigned to multiple meetings at the same time.
    no_slots_at_same_location(SLOTS),
    print("NO OVERLAPING-LOCATION ENSURED"), nl,

    once(labeling([min(LOCATION_TOTAL_COST)], VARIABLES)).

/**
 * Extract variables from slots (NUM, LOCATION)
 */
extract_variables([], []).
extract_variables([SLOT|SLOTS], VAR_SLOTS):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    nonvar(NUM), nonvar(LOCATION),
    extract_variables(SLOTS, VAR_SLOTS).
extract_variables([SLOT|SLOTS], [NUM, LOCATION|VAR_SLOTS]):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    var(NUM), var(LOCATION),
    extract_variables(SLOTS, VAR_SLOTS).
extract_variables([SLOT|SLOTS], [NUM|VAR_SLOTS]):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    var(NUM), nonvar(LOCATION),
    extract_variables(SLOTS, VAR_SLOTS).
extract_variables([SLOT|SLOTS], [LOCATION|VAR_SLOTS]):-
    SLOT = (NUM, _, _, _, _, LOCATION, _),
    nonvar(NUM), var(LOCATION),
    extract_variables(SLOTS, VAR_SLOTS).

/**
 * Ensure slots structure, and NUM of slot validity
 */
ensure_slots(_, []).
ensure_slots(SLOTS, [HOLIDAY|HOLIDAYS]):-
    ensure_slots_on_holiday(SLOTS, HOLIDAY),
    ensure_slots(SLOTS, HOLIDAYS).

ensure_slots_on_holiday([], _).
ensure_slots_on_holiday([SLOT|SLOTS], HOLIDAY):-
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
    ensure_slots_on_holiday(SLOTS, HOLIDAY).

/**
 * No two slots at the same time placed the same location
 */
no_slots_at_same_location(SLOTS):-
    all_different_locations_per_slot(29, SLOTS).  

all_different_locations_per_slot(-1,_).
all_different_locations_per_slot(NUM, SLOTS):-
    NUM >= 0,
    NEW_NUM #= NUM - 1,
    all_different_locations_per_slot(NEW_NUM, SLOTS),
    extract_locations_of_same_time_slots(NUM, SLOTS, LOCATIONS),
    all_distinct(LOCATIONS).

% set_of_locations(TARGET_NUM, [SLOT|SLOTS], [LOCATION|LOCATIONS], MAX_NUM_OF_CLASS_A):-
%     MAX_NUM_OF_CLASS_A >= 0,

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
    NEW_NUM #= NUM - 1,
    all_different_teachers_per_slot(NEW_NUM, SLOTS),
    extract_teachers_of_same_time_slots(NUM , SLOTS, TEACHERS),
    % print("EXTRACTED TEACHERS: "), print(TEACHERS), nl,
    all_distinct(TEACHERS).

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
corresponding_list_of_ones(Xs, ONES):-
    length(Xs, N), length(ONES, N), ONES ins 1..1.

/**
 * Serialize all types of slots for each subgroup
 */
serialize_subgroups(_,[]).
serialize_subgroups(SLOTS, [SUBGROUP|SUBGROUPS]):-
    list_subgroup_timings(SLOTS, SUBGROUP, TIMINGS_LIST),
    corresponding_list_of_ones(TIMINGS_LIST, ONES),
    serialized(TIMINGS_LIST, ONES),
    serialize_subgroups(SLOTS, SUBGROUPS).

list_subgroup_timings([],_,[]).
list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, TIMINGS_LIST):-
    SLOT = (_, _, _, _, SUBGROUP, _, _),
    SUBGROUP \= TARGET_SUBGROUP,
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).

list_subgroup_timings([SLOT|SLOTS], TARGET_SUBGROUP, [TIME|TIMINGS_LIST]):-
    SLOT = (TIME, _, _, _, TARGET_SUBGROUP, _, _),
    list_subgroup_timings(SLOTS, TARGET_SUBGROUP, TIMINGS_LIST).


/**
 * Serialize lecs of a subject taken by a group
 * with each slot of the same subject taken by that group
 * 
 * Note: Does not care about other subjects taken by that group
 */
serialize_each_lec_with_its_companions(SLOTS):-
    split_lec_nonlec(SLOTS, LEC_SLOTS, NONLEC_SLOTS),
    serialize_for_subject(LEC_SLOTS, NONLEC_SLOTS).

serialize_for_subject([], _).
serialize_for_subject([LEC|LEC_SLOTS], NONLEC_SLOTS):-
    % print("Serializing LEC: "), print(LEC), nl,
    % print("Nonlecs Are: "), print(NONLEC_SLOTS), nl,
    % once(serialize_for_subject_helper(LEC, NONLEC_SLOTS)),
    serialize_for_subject(LEC_SLOTS, NONLEC_SLOTS),
    once(pair_subject_and_companion(LEC, NONLEC_SLOTS, PAIRS)),
    % print("PAIRS: "), print(PAIRS), nl,
    serialize_pairs(PAIRS).
    % print("Serialized FOR THAT LECTURE"), nl,

pair_subject_and_companion(_,[],[]).
pair_subject_and_companion(LEC, [NONLEC|NONLEC_SLOTS], PAIRS):-
    LEC = (_, SUBJECT1, _, GROUP1, _, _, _),
    NONLEC = (_, SUBJECT2, _, GROUP2, _, _, _),
    (SUBJECT1 \= SUBJECT2; GROUP1 \= GROUP2),
    pair_subject_and_companion(LEC, NONLEC_SLOTS, PAIRS).
pair_subject_and_companion(LEC, [NONLEC|NONLEC_SLOTS], [(NUM1, NUM2)|PAIRS]):-
    LEC = (NUM1, SUBJECT, _, GROUP, _, _, _),
    NONLEC = (NUM2, SUBJECT, _, GROUP, _, _, _),
    pair_subject_and_companion(LEC, NONLEC_SLOTS, PAIRS).

serialize_pairs([]).
serialize_pairs([(A, B)|PAIRS]):-
    A #\= B,
    serialize_pairs(PAIRS).

split_lec_nonlec([], [], []).
split_lec_nonlec([SLOT|SLOTS], LECS, [SLOT|NONLECS]):-
    SLOT = (_, _, TYPE, _, _, _,_),
    (TYPE \= small_lec, TYPE \= big_lec),
    split_lec_nonlec(SLOTS, LECS, NONLECS).
split_lec_nonlec([SLOT|SLOTS], [SLOT|LECS], NONLECS):-
    SLOT = (_, _, TYPE, _, _, _,_),
    (TYPE = small_lec; TYPE = big_lec),
    split_lec_nonlec(SLOTS, LECS, NONLECS).




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
