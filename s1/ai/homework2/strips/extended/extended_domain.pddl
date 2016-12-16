(define (domain extended-paul-world)
    (:predicates
        (is-room ?room)
        (is-robot ?robot)
        (is-object ?object)

        (is-at ?object ?room) ;; robot is a moving-room
        (can-move ?room ?room)
        (is-empty ?robot)
        (is-clean ?object)
        (is-stored ?object)
        (should-be-cleaned-in ?object ?room)
        (should-be-stored-in ?object ?room)

        ;; (manuels-seat ?wall)
        ;; (mccarthy-seat ?wall)
        ;; (ritchie-seat ?wall)
        ;; (kernighan-seat ?wall)
    )

    (:action move
        :parameters
            (?robot
             ?from-room
             ?to-room)
        :precondition
            (and
                (is-robot ?robot)
                (is-room ?from-room)
                (is-room ?to-room)

                (is-at ?robot ?from-room)
                (can-move ?from-room ?to-room)
            )
        :effect
            (and
                (is-at ?robot ?to-room)
                (not
                  (is-at ?robot ?from-room)
                )
            )
    )
    (:action pick-obj
        :parameters
            (?robot
             ?from-room
             ?object
            )
        :precondition
            (and
                (is-robot ?robot)
                (is-room ?from-room)
                (is-object ?object)

                (is-at ?robot ?from-room)
                (is-at ?object ?from-room)

                (is-empty ?robot)
            )

        :effect
            (and
                (is-at ?object ?robot)
                (not
                  (is-empty ?robot)
                )
            )
    )
    (:action drop-obj ;; load
        :parameters
            (?robot
             ?to-room
             ?object
            )
        :precondition
            (and
                ;; unary
                (is-robot ?robot)
                (is-room ?to-room)
                (is-object ?object)

                ;; robot - room
                (is-at ?robot ?to-room)

                ;; robot - obj
                (is-at ?object ?robot)

                ;; obj - room
                (should-be-cleaned-in ?object ?to-room)
            )

        :effect
            (and
                (is-empty ?robot) ;; robot is empty
                (not
                  (is-at ?object ?robot)
                )
                (is-at ?object ?to-room)
            )
    )
    (:action run-machine ;;
        :parameters(
             ?robot
             ?object
             ?from-room)
        :precondition ;; wm is loaded; 
            (and
                ;; unary
                (is-robot ?robot)
                (is-room ?from-room)
                (is-object ?object)

                ;; robot - object
                (is-at ?object ?robot)
                ;; robot - room
                (is-at ?robot ?from-room)
                ;; room - object
                (should-be-cleaned-in ?object ?from-room)
            )
        :effect ;; wm is not loaded, robot is loaded, tray is on robot
            (and
                (is-clean ?object)
            )
    )
    (:action store-object
        :parameters
            (?robot
             ?object
             ?from-room)
        :precondition ;; robot is loaded; obj is clean 
            (and
                ;; unary
                (is-robot ?robot)

                (is-object ?object)
                (is-clean ?object)

                (is-room ?from-room)

                ;; robot - object
                (is-at ?object ?robot)
                ;; robot - room
                (is-at ?robot ?from-room)
                ;; room - object
                (should-be-stored-in ?object ?from-room)
            )

        :effect
            (and
                (is-at ?object ?from-room)
                (is-stored ?object)
                (not
                    (is-at ?object ?robot)
                )
            )
    )
    ;; (:action wait-dancing
    ;;     :parameters
    ;;         (?robot
    ;;          ?from-room
    ;;          )
    ;;     :precondition
    ;;         (and
    ;;             (is-robot ?robot)
    ;;             (is-empty ?robot)
    ;;         )
    ;;     :effect
    ;; )
)
    
