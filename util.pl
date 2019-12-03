:- use_module(library(clpfd)).



% split_list([],_).

% split_list([SLOT|SLOTS], L):-
%     SLOT = (NUM,_),
%     NUM in 0..29,
%     NUM_INDEX is NUM + 1,
%     length(L, 30),    
%     nth1(NUM_INDEX, L , SLOT_LIST),
%     % print(NUM),print(' '),print(SLOT_LIST),nl,
    
%     append(SLOT_LIST, [SLOT], SLOT_LIST_2),
%     nth1(NUM_INDEX, L , SLOT_LIST_2),
%     split_list(SLOTS, L).

%     % print(L)

check_all_slots_diffLocations(SLOTS):-
    check_all_slots_rec(29, SLOTS).  

check_all_slots_rec(-1,_).
check_all_slots_rec(NUM, SLOTS):-
    NUM >= 0,
    extract_slots(NUM , SLOTS, LOCATIONS),
    % print("pass "), print(NUM), nl,
    % print(LOCATIONS), nl,
    all_different(LOCATIONS),
    NEW_NUM #= NUM - 1, 
    check_all_slots_rec(NEW_NUM, SLOTS).

% 28,19,lab,12,75,58
% 28,10,lab,17,101,58
extract_slots(_, [] ,[]).
extract_slots(TARGET_NUM, [SLOT|SLOTS], [LOCATION|LOCATIONS]):-  
    SLOT = (NUM,_,_,_,_,LOCATION), 
    NUM #= TARGET_NUM,
    % print(SLOT), nl,
    % print("MATCHED"), nl,
    extract_slots(TARGET_NUM, SLOTS, LOCATIONS).
extract_slots(TARGET_NUM, [SLOT|SLOTS], LOCATIONS):-
    SLOT = (ANOTHER_NUM,_,_,_,_,_),
    ANOTHER_NUM #\= TARGET_NUM,
    % print("not"), nl, print(TARGET_NUM), nl, print(ANOTHER_NUM), nl,
    extract_slots(TARGET_NUM, SLOTS, LOCATIONS).


% test(L):-
%     once(extract_slots(4, L , L1)),
%     all_distinct(L1).
    