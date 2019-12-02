:- use_module(library(clpfd)).



split_list([],_).

split_list([SLOT|SLOTS], L):-
    SLOT = (NUM,_),
    NUM in 0..29,
    NUM_INDEX is NUM + 1,
    length(L, 30),    
    nth1(NUM_INDEX, L , SLOT_LIST),
    % print(NUM),print(' '),print(SLOT_LIST),nl,
    
    append(SLOT_LIST, [SLOT], SLOT_LIST_2),
    nth1(NUM_INDEX, L , SLOT_LIST_2),
    split_list(SLOTS, L).

    % print(L)