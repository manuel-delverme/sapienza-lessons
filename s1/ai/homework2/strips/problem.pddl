(define (problem paul-goes-home)
    (:domain paul-world)
    (:objects
        square1 square2 square3 square4 square5 square6 
        square7 square8 square9 square10 square11 square12
        
        wall1 wall2 wall3 wall4 wall5 wall6 wall7 wall8 
        wall9 
        
        paul
    )
    
    (:init
        ;the tiles exist
        (square square1) (square square2) (square square3) 
        (square square4) (square square5) (square square6) 
        (square square7) (square square8) (square square9)
        
        ;the walls also exist
        (wall wall1) (wall wall2) (wall wall3) (wall wall4)
        (wall wall5) (wall wall6)
        

        ;the tiles are connected
        (can-move square1 square5) (can-move square1 square9)
        (can-move square2 square5) (can-move square3 square4) 
        (can-move square3 square6) (can-move square4 square3) 
        (can-move square4 square8) (can-move square4 square9)
        (can-move square5 square1) (can-move square5 square2)
        (can-move square6 square3) (can-move square6 square7)
        (can-move square6 square8) (can-move square7 square6)
        (can-move square8 square4) (can-move square8 square6)
        (can-move square9 square1) (can-move square9 square4)
        
        ;walls are usually in on the ground
        (is-in wall1 square2) (is-in wall2 square3) 
        (is-in wall3 square9) (is-in wall4 square8)
        (is-in wall5 square3) (is-in wall6 square3)   
        
        (robot paul)
        (empty paul)
        (at paul square6)
    )
    (:goal
        (and 
            (at paul square1)
        )
    )
)
