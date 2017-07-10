(define (problem paul-goes-home)
	(:domain extended-paul-world)
	(:objects
      kitchen
      bathroom
      living
      corridor

      manuels-tray
      mccarthy-tray
      ritchie-tray
      kernighan-tray
      tablecloth

      paul
	)
	(:init
      (is-room kitchen)
      (is-room bathroom)
      (is-room living)
      (is-room corridor)
      (is-room paul)

      (is-robot paul)

      (is-object manuels-tray)
      (is-object mccarthy-tray)
      (is-object ritchie-tray)
      (is-object kernighan-tray)
      (is-object tablecloth)

      (is-at manuels-tray living)
      (is-at mccarthy-tray living)
      (is-at ritchie-tray living)
      (is-at kernighan-tray living)
      (is-at tablecloth living)
      (is-at paul corridor)

      (can-move kitchen corridor)
      (can-move bathroom corridor)
      (can-move living corridor)
      (can-move corridor kitchen)
      (can-move corridor bathroom)
      (can-move corridor living)

      (is-empty paul)

      (should-be-cleaned-in tablecloth bathroom)
      (should-be-cleaned-in manuels-tray kitchen)

      (should-be-cleaned-in mccarthy-tray kitchen)
      (should-be-cleaned-in ritchie-tray kitchen)
      (should-be-cleaned-in kernighan-tray kitchen)

      (should-be-stored-in tablecloth living)
      (should-be-stored-in manuels-tray kitchen)
      (should-be-stored-in mccarthy-tray kitchen)
      (should-be-stored-in ritchie-tray kitchen)
      (should-be-stored-in kernighan-tray kitchen)
	)
	(:goal
		(and
            (is-clean tablecloth)
            (is-clean manuels-tray)
            (is-clean mccarthy-tray)
            (is-clean ritchie-tray)
            (is-clean kernighan-tray)

            (is-stored tablecloth)
            (is-stored manuels-tray)
            (is-stored mccarthy-tray)
            (is-stored ritchie-tray)
            (is-stored kernighan-tray)
		)
	)
)
