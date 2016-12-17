# The initial plan includes the plan constraints for Start and Finish,
# with ordering Start≺Finish
# 2. The successor function
# i - pick one open precondition p on action B
# ii - pick one action A that achieves p
# iii - add the causal link 𝐴 ՜
# 𝑝
# 𝐵 and the ordering constraint
# A≺B; if A is new add also Start≺A and B ≺Finish
# iv - resolve conflicts, if possible, otherwise backtrack
# 3. The goal test succeeds when there are no more open
# preconditionThe initial plan includes the plan constraints for Start and Finish,
# with ordering Start≺Finish
# 2. The successor function
# i - pick one open precondition p on action B
# ii - pick one action A that achieves p
# iii - add the causal link 𝐴 ՜
# 𝑝
# 𝐵 and the ordering constraint
# A≺B; if A is new add also Start≺A and B ≺Finish
# iv - resolve conflicts, if possible, otherwise backtrack
# 3. The goal test succeeds when there are no more open
# preconditionss

class node:
    def __init__(self):
        self.data = None # contains the data
        self.next = None # contains the reference to the next node


class linked_list:
    def __init__(self):
        self.cur_node = None

    def add_node(self, data):
        new_node = node() # create a new node
        new_node.data = data
        new_node.next = self.cur_node # link the new node to the 'previous' node.
        self.cur_node = new_node #  set the current node to the new one.

    def list_print(self):
        node = self.cur_node # cant point to ll!
        while node:
            print node.data
            node = node.next

class Action(object):
    def __init__(self):
        # http://artint.info/code/python/code.pdf

class Plan(object):
    def __init__(self):
        self.befores = {}

    def add_ordering_constraint(self, pre,  post):
        # pre -- [] -- post
        self.before[post].append(pre)

    def get_or_create(self, name):
        self.add_ordering_constraint('start', name)
        self.add_ordering_constraint(name, 'finish')
        return name


plan = Plan()
start = plan.add_node('start')
goal = plan.add_node('goal')
plan.add_ordering_constraint(start, goal)

while(True):
    prec, node = plan.get_last_precondition()
    if not prec:
        break

    for action in actions:
        if prec in action.effects:
            action_node = plan.get_or_create(action)
            plan.add_causal_link(node2, node)
            plan.add_ordering_constraint(node2, node)
pplan = plan.build()
print(pplan)
