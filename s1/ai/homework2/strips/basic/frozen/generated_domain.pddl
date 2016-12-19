(define (domain paul-world)
    (:predicates
        (can-move ?from ?to)
        (is-in ?object ?square)
        ;;(been-at ?robot ?square)
        (carry ?robot ?object)
        (at ?robot ?square)
        (square ?square)
        (wall ?wall)
        (table ?wall)
        (manuels-seat ?wall)
        (mccarthy-seat ?wall)
        (ritchie-seat ?wall)
        (kernighan-seat ?wall)
        (door ?wall)
        (closet ?wall)
        (part-of-kitchen ?square)
        (part-of-bedroom ?square)
        (part-of-livingroom ?square)
        (part-of-bathroom ?square)
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
    (:action pick-tray
        :parameters
            (?robot
             ?from-square)

        :precondition
            (and
                (robot ?robot)
                (square ?from-square)

                (is-near ?robot ?from-square)

                (is-in ?tray ?from-square)
                (empty ?robot)
            )

        :effect
            (and
                (not (is-in ?tray ?from-square))
                (not (empty ?robot))
            )
    )
    (:action leave-tray
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
    (:action run-washing-machine
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
    (:action wait-dancing
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
    )