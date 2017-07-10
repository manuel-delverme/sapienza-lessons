(define (domain paul-world)
    (:predicates
        (can-move ?from ?to); aka connected
        (is-in ?object ?square)
        ;;(been-at ?robot ?square)
        (carry ?robot ?object)
        (at ?robot ?square)
        (square ?square)
        (wall ?wall)
        (robot ?robot)
        (empty ?robot)
    )
    
    (:action move
        :parameters
            (?robot
             ?from-square 
             ?to-square)

        :precondition 
            (and 
                (robot ?robot)
                (square ?from-square)
                (square ?to-square) 

                (at ?robot ?from-square)
                (can-move ?from-square ?to-square)
            )

        :effect 
            (and 
                (at ?robot ?to-square)
                (not 
                  (at ?robot ?from-square)
                )
            )
    )

;;    (:action take-shit
;;        :parameters 
;;            (?robot 
;;             ?shit 
;;             ?square)
;;
;;        :precondition 
;;            (and 
;;                (robot ?robot)
;;                (shit ?shit)
;;                (square ?square) 
;;                (is-in ?shit ?square)
;;                (at ?robot ?square)
;;                (empty ?robot))
;;
;;        :effect 
;;            (and 
;;                (not (is-in ?shit ?square))
;;                (carry ?robot ?shit)
;;                (not (empty ?robot)))
;;    )
;;    
;;    (:action drop-shit
;;        :parameters 
;;            (?robot
;;             ?shit 
;;             ?square)
;;
;;        :precondition 
;;            (and 
;;                (robot ?robot)
;;                (shit ?shit)
;;                (square ?square)
;;                (is-dropping-place ?square)
;;                (at ?robot ?square)
;;                (carry ?robot ?shit))                     
;;                           
;;        :effect 
;;            (and 
;;                (is-in ?shit ?square) 
;;                (not (carry ?robot ?shit))
;;                (stored-shit ?shit)
;;                (empty ?robot))
;;    )
)
