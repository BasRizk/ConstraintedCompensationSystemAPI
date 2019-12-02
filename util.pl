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
    once(check_all_slots_rec(30, SLOTS)).  

check_all_slots_rec(-1,_).
check_all_slots_rec(N, SLOTS):-
    N #>= 0,
    once(extract_slots(N , SLOTS, L)),
    all_different(L),
    N1 is N - 1, 
    check_all_slots_rec(N1, SLOTS).
    

extract_slots(_, [] ,[]).

extract_slots(N, [SLOT|SLOTS], L):-
    SLOT = (NUM,_,_,_,_,LOCATION),
    NUM in 0..29,
    NUM #= N, 
    extract_slots(N, SLOTS, L1),
    append(L1, [LOCATION], L).    

extract_slots(N, [SLOT|SLOTS], L):-
    SLOT = (NUM,_,_,_,_,_),
    NUM in 0..29,
    NUM #\= N, 
    extract_slots(N, SLOTS, L).


test(L):-
    once(extract_slots(4, L , L1)),
    all_distinct(L1).
    