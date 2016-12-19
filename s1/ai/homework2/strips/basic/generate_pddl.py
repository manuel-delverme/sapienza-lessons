import sys
import subprocess
import random
import os
from PIL import Image


def generate_domain(domain_name, extended=False):
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
    domain = "(define "
    domain += "(domain {domain_name})".format(domain_name=domain_name)
    ##################################################################
    #                                                                #
    #                       PREDICATES                               #
    #                                                                #
    ##################################################################
    domain += """
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
    )"""
    ##################################################################
    #                                                                #
    #                        ACTIONS                                 #
    #                                                                #
    ##################################################################
    domain += """
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
    """
    ##################################################################
    #                                                                #
    #                        ACTIONS                                 #
    #                                                                #
    ##################################################################

    domain += ")"
    return domain[:]


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

    ##################################################################
    #                                                                #
    #                   OBJECTS IN THE WORLD                         #
    #                                                                #
    ##################################################################
    objects = []
    squares = []
    house_map = Image.new('RGB', (NUM_SQUARES, NUM_SQUARES), (0,0,0))

    for i in range(NUM_SQUARES):
        for j in range(NUM_SQUARES):
            squares.append("square{}_{}".format(i, j))

    objects.extend(squares)

    walls = ["wall{}".format(i) for i in range(NUM_WALLS)]
    objects.extend(walls)

    robot = "paul"
    objects.append(robot)

    ##################################################################
    #                                                                #
    #                   RELATIONS BETWEEN OBJECTS                    #
    #                                                                #
    ##################################################################
    relations = []
    for square in squares:
        relations.append("square {}".format(square))

    for wall in walls:
        relations.append("wall {}".format(wall))

    walled_squares = set()

    i = random.choice(range(NUM_SQUARES))
    j = random.choice(range(NUM_SQUARES))
    robot_position = (i, j)

    relations.append("robot {}".format(robot))
    relations.append("empty {}".format(robot))
    # relations.append("empty {}".format(robot))

    i = random.choice(range(NUM_SQUARES))
    j = random.choice(range(NUM_SQUARES))
    print("seed", i,j)
    while len(walled_squares) < NUM_WALLS:
        offsets = random.sample([(1, 0), (-1, 0), (0, 1),],2)
        for delta in offsets:
            ti = i + delta[0]
            tj = j + delta[1]
            if (ti, tj) not in walled_squares and not (ti, tj) == robot_position:
                try:
                    house_map.putpixel((tj, ti), (255, 0, 0))
                except Exception as e:
                    pass
                else:
                    if len(walled_squares)+1 > NUM_WALLS:
                        break
                    walled_squares.add((ti, tj))
                    relations.append("is-in wall{} square{}_{}".format(len(walled_squares) - 1, ti, tj))
        if random.randint(0,10) < 2:
            i = random.choice(range(NUM_SQUARES))
            j = random.choice(range(NUM_SQUARES))
            print("jump", i,j)
        else:
            i = ti
            j = tj
            print("cont", i,j)

    taken = ["square{}_{}".format(i_, j_) for i_, j_ in walled_squares]

    for i in range(NUM_SQUARES):
        for j in range(NUM_SQUARES):
            # print((j, i), (255, 255, 255))
            fro = "{}_{}".format(i, j)
            for delta in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                ti = i + delta[0]
                tj = j + delta[1]
                if ti < 0 or tj < 0 or ti >= NUM_SQUARES or tj >= NUM_SQUARES or (i, j) in walled_squares:
                    continue
                else:
                    to = "{}_{}".format(ti, tj)
                    relations.append("can-move square{} square{}".format(fro, to))
                    house_map.putpixel((j, i), (255, 255, 255))



    starting_position = taken[0]
    while starting_position in taken:
        starting_position = random.choice(squares)

    relations.append("at paul {}".format(starting_position))

    ##################################################################
    #                                                                #
    #                       GOAL STATE                               #
    #                                                                #
    ##################################################################
    def dist(x,y):
        x = sum(ord(a) for a in x)
        y = sum(ord(a) for a in y)
        return abs(y-x)

    goal_square = taken[0]
    good_squares = squares
    random.shuffle(good_squares)
    while goal_square in taken or dist(goal_square, starting_position) < 70:
        goal_square = good_squares.pop(0)
        if not good_squares:
            break
    print("dist", dist(goal_square, starting_position))

    goal = ["at paul {}".format(goal_square)]

    generated_problem = generate_problem("paul-goes_home", "paul-world", objects, relations, goal)
    problem_path = "generated_problem.pddl"
    with open(problem_path, "w") as prob:
        prob.write(generated_problem)

    generated_domain = generate_domain("paul-world", extended=True)
    domain_path = "generated_domain.pddl"
    with open(domain_path, "w") as domain:
        domain.write(generated_domain)
    print("../../Metric-FF-v2.1/ff -o {} -f {} -s 1".format("domain.pddl", problem_path))
    output = subprocess.check_output("../../Metric-FF-v2.1/ff -o {} -f {} -s 1".format("domain.pddl", problem_path),
                                     stderr=subprocess.STDOUT,
                                     shell=True)
    for row in output.splitlines():
        row = str(row).strip()
        idx = row.find("MOVE PAUL SQUARE")
        if idx > 0:
            idx += len("MOVE PAUL SQUARE")
            code = row[idx:-1]
            squares = code.replace("SQUARE", "").split()
            for sq in squares:
                x, y = sq.split("_")
                house_map.putpixel((int(y),int(x)), (0, 0, 255))
    house_map.save("map.png", "PNG")
    os.system("img2txt -W {} -H {} map.png".format(2.1*NUM_SQUARES, NUM_SQUARES))

if __name__ == "__main__":
    main()
    print("done")
