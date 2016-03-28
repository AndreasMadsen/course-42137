
import random
import collections

def initialize(solution):
    # create a list of missing courses in random order
    courses = []
    for (course, missing) in solution.missing_courses():
        courses += [course] * missing
    random.shuffle(courses)

    # create a double ended qoue of avaliable slots in random order
    slots = list(solution.avaliable_slots())
    random.shuffle(slots)
    slots = collections.deque(slots)

    # Insert missing courses
    for course in courses:
        for i in range(0, len(slots)):
            slot = slots.pop()

            # Create simulated solution
            penalties = solution.simulate_add(course, *slot)

            # If valid and better
            if penalties is not None and penalties.cost() < 0:
                solution.mutate_add(course, *slot, penalties=penalties)
                break
            else:
                # append back the slot if it couldn't be used, such it can
                # be used by another course
                slots.appendleft(slot)
