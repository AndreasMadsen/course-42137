
import collections
import textwrap

from solution.combination import Combination
from solution.penalties import Penalties

def _decrement_counter(counter, attribute):
    counter[attribute] -= 1
    if counter[attribute] == 0: del counter[attribute]

def _remove_from_defafultdict(obj, attribute, value):
    obj[attribute].remove(value)
    if len(obj[attribute]) == 0: del obj[attribute]

class Solution:
    def __init__(self, database, schedule=None):
        self.schedule = []
        self.penalties = Penalties()

        self._database = database

        self._dict_time = collections.defaultdict(list)
        self._dict_course = collections.defaultdict(list)

        self._sum_time = collections.Counter()
        self._sum_room = collections.Counter()
        self._sum_course = collections.Counter()
        self._sum_time_room = collections.Counter()
        self._sum_period_room = collections.Counter()

        self._intialize_cost()

        # Add schedule list if provided
        if schedule is not None:
            for item in schedule:
                if isinstance(item, Combination): item = item.all
                self.mutate_add(*item)

    @property
    def objective(self):
        return self.penalties.cost()

    def _intialize_cost(self):
        # The only cost associated with an empty solution is unscheduled cost
        # and the minimum working days cost.
        U_sum = 0
        W_sum = 0
        for course in self._database.courses.values():
            # There are not scheduled any courses
            U_sum += course.number_of_lectures
            # All courses have zero working days
            W_sum += course.minimum_working_days

        self.penalties.U_sum += U_sum
        self.penalties.W_sum += W_sum

    def export(self):
        return [c.all for c in self.schedule]

    def copy(self):
        return Solution(self._database, schedule=self.schedule)

    def _add_valid(self, course, day, period, room):
        # 1b
        # This course is already registred at this time
        if self._sum_room[course, day, period] > 0: return False
        # This course can not be assigned to this time slot
        F_ct = (course, day, period) in self._database.unavailability
        if F_ct == 1: return False

        # 1c
        # no other course is registred at this time in this room
        if self._sum_course[day, period, room] > 0: return False

        # 1d
        # the maximum number of lecturers is not exceeded
        L_c = self._database.courses[course].number_of_lectures
        if self._sum_time_room[course] >= L_c: return False

        # 1e
        # There are no conflicting courses scheduled at this time
        for conflicting_course in self._database.courses[course].conflicts:
            for existing_combination in self._dict_time[day, period]:
                if conflicting_course == existing_combination.course:
                    return False

        return True

    def _add_delta(self, course, day, period, room):
        # V: exceeded room capacity
        number_of_student = self._database.courses[course].number_of_student
        room_capacity = self._database.rooms[room].capacity
        V_sum = max(0, number_of_student - room_capacity)

        # U: scheduled to few times
        # This assumes the additon is valid, thus we already know there is
        # space for one more course. Adding the course will improve the score.
        U_sum = -1

        # P: room stability
        P_sum = 0
        used_rooms = {c.room for c in self._dict_course[course]}
        if (room not in used_rooms and len(used_rooms) > 0): P_sum = 1

        # W: to few working days
        day_spread = {c.day for c in self._dict_course[course]}
        min_spread = self._database.courses[course].minimum_working_days
        W_sum = 0
        if (len(day_spread) < min_spread and day not in day_spread): W_sum = -1

        # A: curriculum continuity
        A_sum = 0
        for q in self._database.courses[course].curricula:
            found_tm2_continuity = False
            found_tm1_continuity = False
            found_tp1_continuity = False
            found_tp2_continuity = False

            for c in self._database.curricula[q].courses:
                # We can assume that there do not exists another course with
                # curriculum q at (day, period) since that would be invalid.

                if self._sum_room[c, day, period - 2] > 0:
                    found_tm2_continuity = True

                if self._sum_room[c, day, period - 1] > 0:
                    found_tm1_continuity = True

                if self._sum_room[c, day, period + 1] > 0:
                    found_tp1_continuity = True

                if self._sum_room[c, day, period + 2] > 0:
                    found_tp2_continuity = True

            # Check if course exists before.
            # If a penalty was added for period - 1, then remove that
            # penalty
            if found_tm1_continuity and not found_tm2_continuity:
                A_sum -= 1

            # Check if course exists after.
            # If a penalty was added for period + 1, then remove that
            # penalty
            if found_tp1_continuity and not found_tp2_continuity:
                A_sum -= 1

            # If no continuity was found for curriculum q, then add a penalty
            if not found_tm1_continuity and not found_tp1_continuity:
                A_sum += 1

        return Penalties(U_sum, W_sum, A_sum, P_sum, V_sum)

    def _update_add(self, course, day, period, room):
        # Create combination
        combination = Combination(course, day, period, room)
        self.schedule.append(combination)

        # Maintain datastructures
        self._sum_time[combination.course_room] += 1
        self._sum_room[combination.course_time] += 1
        self._sum_course[combination.time_room] += 1
        self._sum_time_room[combination.course] += 1
        self._sum_period_room[combination.course_day] += 1
        self._dict_time[combination.time].append(combination)
        self._dict_course[combination.course].append(combination)

    def simulate_add(self, course, day, period, room):
        if not self._add_valid(course, day, period, room):
            return None

        return self._add_delta(course, day, period, room)

    def mutate_add(self, course, day, period, room, penalties=None):
        if penalties is None:
            penalties = self.simulate_add(course, day, period, room)

        if (penalties is None):
            raise Exception('bad combination (%d, %d, %d, %d)' % (
                course, day, period, room))

        # Update datastructures
        self._update_add(course, day, period, room)

        # Update penalties and objective
        self.penalties += penalties

    def _remove_valid(self, course, day, period, room):
        removed_combination = (course, day, period, room)

        # A combination has to exists to be removed
        for combination in self.schedule:
            if combination.all == removed_combination:
                return True

        return False

    def _remove_delta(self, course, day, period, room):
        # V: exceeded room capacity
        number_of_student = self._database.courses[course].number_of_student
        room_capacity = self._database.rooms[room].capacity
        V_sum = -max(0, number_of_student - room_capacity)

        # U: scheduled to few times
        U_sum = 1

        # P: room stability
        P_sum = 0
        all_rooms = {c.room for c in self._dict_course[course]}
        used_rooms = [c.room for c in self._dict_course[course] if c.room == room]
        if (len(all_rooms) > 1 and len(used_rooms) == 1): P_sum = -1

        # W: to few working days
        day_spread = {c.day for c in self._dict_course[course]}
        used_days = [c.day for c in self._dict_course[course] if c.day == day]
        min_spread = self._database.courses[course].minimum_working_days
        W_sum = 0
        if (len(day_spread) <= min_spread and len(used_days) == 1):
            W_sum = 1

        # A: curriculum continuity
        A_sum = 0
        for q in self._database.courses[course].curricula:
            found_tm2_continuity = False
            found_tm1_continuity = False
            found_tp1_continuity = False
            found_tp2_continuity = False

            for c in self._database.curricula[q].courses:
                # We can assume that there do not exists another course with
                # curriculum q at (day, period) since that would be invalid.

                if self._sum_room[c, day, period - 2] > 0:
                    found_tm2_continuity = True

                if self._sum_room[c, day, period - 1] > 0:
                    found_tm1_continuity = True

                if self._sum_room[c, day, period + 1] > 0:
                    found_tp1_continuity = True

                if self._sum_room[c, day, period + 2] > 0:
                    found_tp2_continuity = True

            # Check if course exists before.
            # If a penalty was added for period - 1, then remove that
            # penalty
            if found_tm1_continuity and not found_tm2_continuity:
                A_sum += 1

            # Check if course exists after.
            # If a penalty was added for period + 1, then remove that
            # penalty
            if found_tp1_continuity and not found_tp2_continuity:
                A_sum += 1

            # If no continuity was found for curriculum q, then add a penalty
            if not found_tm1_continuity and not found_tp1_continuity:
                A_sum -= 1

        return Penalties(U_sum, W_sum, A_sum, P_sum, V_sum)

    def _update_remove(self, course, day, period, room):
        # Create combination and remove, this uses an custom __eq__ function
        combination = Combination(course, day, period, room)
        self.schedule.remove(combination)

        # Maintain datastructures
        _decrement_counter(self._sum_time, combination.course_room)
        _decrement_counter(self._sum_room, combination.course_time)
        _decrement_counter(self._sum_course, combination.time_room)
        _decrement_counter(self._sum_time_room, combination.course)
        _decrement_counter(self._sum_period_room, combination.course_day)
        _remove_from_defafultdict(self._dict_time, combination.time, combination)
        _remove_from_defafultdict(self._dict_course, combination.course, combination)

    def simulate_remove(self, course, day, period, room):
        if not self._remove_valid(course, day, period, room):
            return None

        return self._remove_delta(course, day, period, room)

    def mutate_remove(self, course, day, period, room, penalties=None):
        if penalties is None:
            penalties = self.simulate_remove(course, day, period, room)

        if (penalties is None):
            raise Exception('bad combination (%d, %d, %d, %d)' % (
                course, day, period, room))

        # Update datastructures
        self._update_remove(course, day, period, room)

        # Update penalties and objective
        self.penalties += penalties

    def simulate_swap(self, combination_a, combination_b):
        # Create new combinations
        a_on_b = (combination_a[0], ) + combination_b[1:]
        b_on_a = (combination_b[0], ) + combination_a[1:]

        # Try removing a
        remove_a = self.simulate_remove(*combination_a)
        if (remove_a is None):
            return None
        else:
            self._update_remove(*combination_a)

        # Try removing b and revert -a if failed
        remove_b = self.simulate_remove(*combination_b)
        if (remove_b is None):
            self._update_add(*combination_a)
            return None
        else:
            self._update_remove(*combination_b)

        # Try adding a_on_b and revert -a-b if failed
        add_a_on_b = self.simulate_add(*a_on_b)
        if (add_a_on_b is None):
            self._update_add(*combination_b)
            self._update_add(*combination_a)
            return None
        else:
            self._update_add(*a_on_b)

        # Try adding b_on_a and revert -a-b+a_on_b if failed
        add_b_on_a = self.simulate_add(*b_on_a)
        if (add_b_on_a is None):
            self._update_remove(*a_on_b)
            self._update_add(*combination_b)
            self._update_add(*combination_a)
            return None

        # Revert all operations
        self._update_remove(*a_on_b)
        self._update_add(*combination_b)
        self._update_add(*combination_a)

        # Sum up the penalties
        penalties = Penalties()
        penalties += remove_a
        penalties += remove_b
        penalties += add_a_on_b
        penalties += add_b_on_a
        return penalties

    def mutate_swap(self, combination_a, combination_b, penalties=None):
        if penalties is None:
            penalties = self.simulate_swap(combination_a, combination_b)

        if (penalties is None):
            raise Exception('bad combination swap((%d, %d, %d, %d), (%d, %d, %d, %d))' % (
                combination_a + combination_b))

        # Create new combinations
        a_on_b = (combination_a[0], ) + combination_b[1:]
        b_on_a = (combination_b[0], ) + combination_a[1:]

        # Create combination and remove
        self._update_remove(*combination_a)
        self._update_remove(*combination_b)
        self._update_add(*a_on_b)
        self._update_add(*b_on_a)

        # Update penalties and objective
        self.penalties += penalties

    def simulate_move(self, combination, destination):
        # create new combination
        new_combination = (combination[0], ) + destination

        # Try removing a
        remove = self.simulate_remove(*combination)
        if (remove is None):
            return None
        else:
            self._update_remove(*combination)

        # Try adding the new combination, revert removal if failed
        add = self.simulate_add(*new_combination)
        if (add is None):
            self._update_add(*combination)
            return None

        # Revert all operations
        self._update_add(*combination)

        # Sum up the penalties
        penalties = Penalties()
        penalties += remove
        penalties += add
        return penalties

    def mutate_move(self, combination, destination, penalties=None):
        if penalties is None:
            penalties = self.simulate_move(combination, destination)

        if (penalties is None):
            raise Exception('bad combination move((%d, %d, %d, %d), (%d, %d, %d))' % (
                combination + destination))

        # Create new combination
        new_combination = (combination[0], ) + destination

        # Create combination and remove
        self._update_remove(*combination)
        self._update_add(*new_combination)

        # Update penalties and objective
        self.penalties += penalties

    def missing_courses(self):
        courses = []
        for course in self._database.courses.values():
            missing = course.number_of_lectures - self._sum_time_room[course.course]
            if missing > 0: courses.append((course.course, missing))

        return courses

    def existing_combinations(self):
        return [combination.all for combination in self.schedule]

    def avaliable_slots(self):
        for d in range(0, self._database.meta.days):
            for p in range(0, self._database.meta.periods_per_day):
                for r in range(0, self._database.meta.rooms):
                    slot = (d, p, r)
                    if slot not in self._sum_course: yield slot

    def __str__(self):
        header = textwrap.dedent("""\
        Unscheduled {U_sum}
        RoomCapacity {V_sum}
        MinimumWorkingDays {W_sum}
        CurriculumCompactness {A_sum}
        RoomStability {P_sum}
        Objective {cost}
        """.format(
            cost=self.penalties.cost(),
            **self.penalties.dict()
        ))

        body = ""
        for combination in self.schedule:
            body += str(combination) + "\n"

        return header + body
