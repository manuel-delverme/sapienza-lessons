import sys
import random
import os


def generate_domain(domain_name):
    #  domain = ""
    #  domain += "(define (domain paul-world)\n".format(domain_name)
    #  domain += "\t\t(:predicates\n"
    #  for p in predicates:
    #      args = ' ?' + ' ?'.join(p.args)
    #      domain += "\t\t\t{}\n".format(p.name, args)
    #  domain += "\t\t)\n"

    #  for a in actions:
    #      domain += "\t\t(:action\n".format(p.name)
    #      domain += "\t\t\t:parameters\n".format(p.name)
    #      domain += "\t\t\t(\n"
    #      for param in a.params:
    #          domain += "\t\t\t\t{}\n".format("?" + param)
    #      domain[-1] = ")"
    #     domain += "\n\n"
    domain = """
(define (domain {domain_name})
    (:predicates
        (can-move ?from ?to)
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
)
    """.format(domain_name=domain_name)
    return domain[1:]


def generate_problem(problem_name, domain, objects, relations, goal):
    problem = ""
    problem += "(define (problem {})\n".format(problem_name)
    problem += "\t(:domain {})\n".format(domain)
    problem += "\t(:objects\n"

    for obj in objects:
        problem += "\t\t{}\n".format(obj)
    problem += "\t)\n"

    problem += "\t(:init\n"
    for rel in relations:
        problem += "\t\t({})\n".format(rel)
    problem += "\t)\n"

    problem += "\t(:goal\n"
    problem += "\t\t(and\n"
    for literal in goal:
        problem += "\t\t\t({})\n".format(literal)
    problem += "\t\t)\n"
    problem += "\t)\n"
    problem += ")\n"

    return problem


def main():
    if len(sys.argv) > 1:
        NUM_SQUARES = int(sys.argv[1])
        if len(sys.argv) > 2:
            NUM_WALLS = int(sys.argv[2])
        else:
            NUM_WALLS = NUM_SQUARES
    else:
        NUM_SQUARES = 3
        NUM_WALLS = 3

    objects = []

    squares = []
    for i in range(NUM_SQUARES):
        for j in range(NUM_SQUARES):
            squares.append("square{}_{}".format(i, j))

    objects.extend(squares)

    walls = ["wall{}".format(i) for i in range(NUM_WALLS)]
    objects.extend(walls)

    robot = "paul"
    objects.append(robot)

    relations = []
    for square in squares:
        relations.append("square {}".format(square))

    for wall in walls:
        relations.append("wall {}".format(wall))

    for i in range(NUM_SQUARES):
        for j in range(NUM_SQUARES):
            fro = "{}_{}".format(i, j)
            for delta in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                ti = i + delta[0]
                tj = j + delta[1]
                if ti < 0 or tj < 0 or ti >= NUM_SQUARES or tj >= NUM_SQUARES:
                    continue
                else:
                    to = "{}_{}".format(ti, tj)
                    relations.append("can-move square{} square{}".format(fro, to))

    walled_squares = set()

    i = random.choice(range(NUM_SQUARES))
    j = random.choice(range(NUM_SQUARES))
    robot_position = (i, j)

    relations.append("robot {}".format(robot))
    relations.append("empty {}".format(robot))
    # relations.append("empty {}".format(robot))

    while len(walled_squares) != NUM_WALLS:
        i = random.choice(range(NUM_SQUARES))
        j = random.choice(range(NUM_SQUARES))
        if (i, j) not in walled_squares and not (i, j) == robot_position:
            walled_squares.add((i, j))
            relations.append("is-in wall{} square{}_{}".format(len(walled_squares) - 1, i, j))

    taken = ["square{}_{}".format(i_, j_) for i_, j_ in walled_squares]

    starting_position = taken[0]
    while starting_position in taken:
        starting_position = random.choice(squares)

    relations.append("at paul {}".format(starting_position))

    goal_square = taken[0]
    while goal_square in taken:
        goal_square = random.choice(squares)

    goal = ["at paul {}".format(goal_square)]

    generated_problem = generate_problem("paul-goes_home", "paul-world", objects, relations, goal)
    problem_path = "generated_problem.pddl"
    with open(problem_path, "w") as prob:
        prob.write(generated_problem)

    generated_domain = generate_domain("paul-world")
    domain_path = "generated_domain.pddl"
    with open(domain_path, "w") as domain:
        domain.write(generated_domain)
    os.system("../Metric-FF-v2.0/ff -o {} -f {} -s 1".format(domain_path, problem_path))

if __name__ == "__main__":
    main()
    print("done")
