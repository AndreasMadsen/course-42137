
import collections
import textwrap

from solution.combination import Combination

class Solution:
    def __init__(self, database, schedule=None):
        self.schedule = []
        self.objective = 0
        self.penalties = {
            "U_sum": 0,
            "W_sum": 0,
            "A_sum": 0,
            "P_sum": 0,
            "V_sum": 0
        }

        self._database = database
        self._cursor = database.cursor()

        self._dict_time = collections.defaultdict(list)
        self._dict_course = collections.defaultdict(list)

        self._sum_time = collections.Counter()
        self._sum_room = collections.Counter()
        self._sum_course = collections.Counter()
        self._sum_time_room = collections.Counter()
        self._sum_period_room = collections.Counter()

        self._intialize_cost()

        # Add schedule list if provided
        if (schedule is not None and len(schedule) > 0):
            if isinstance(schedule[0], Combination):
                self.schedule = list(schedule)
            else:
                self.schedule = [Combination(*item) for item in schedule]
            self._precalc_sums()
            self.penalties = self.cost_seperated()
            self.objective = self._total_cost(**self.penalties)

    def _intialize_cost(self):
        # The only cost associated with an empty solution is unscheduled cost
        # and the minimum working days cost.

        U_sum = 0
        W_sum = 0
        sql = '''SELECT number_of_lectures, minimum_working_days
                 FROM courses'''
        for (num_lectures, minimum_working_days) in self._cursor.execute(sql):
            # There are not scheduled any courses
            U_sum += num_lectures
            # All courses have zero working days
            W_sum += minimum_working_days

        self.penalties['U_sum'] += U_sum
        self.penalties['W_sum'] += W_sum
        self.objective = self._total_cost(**self.penalties)

    def _decrement_counter(self, counter, attribute):
        counter[attribute] -= 1
        if counter[attribute] == 0: del counter[attribute]

    def _remove_from_defafultdict(self, obj, attribute, value):
        obj[attribute].remove(value)
        if len(obj[attribute]) == 0: del obj[attribute]

    def _add_valid(self, course, day, period, room):
        # 1b
        # This course is already registred at this time
        if self._sum_room[course, day, period] > 0: return False
        # This course can not be assigned to this time slot
        sql = '''SELECT count(*) FROM unavailability
                 WHERE course = ? AND day = ? AND period = ?'''
        F_ct = self._cursor.execute(sql, (course, day, period)).fetchone()[0]
        if F_ct == 1: return False

        # 1c
        # no other course is registred at this time in this room
        if self._sum_course[day, period, room] > 0: return False

        # 1d
        # the maximum number of lecturers is not exceeded
        sql = '''SELECT number_of_lectures FROM courses
                 WHERE course = ?'''
        L_c = self._cursor.execute(sql, (course, )).fetchone()[0]
        if self._sum_time_room[course] >= L_c: return False

        # 1e
        # There are no conflicting courses scheduled at this time
        sql = '''SELECT DISTINCT c2.course as c2
                 FROM courses AS c1
                 LEFT JOIN relation AS r1 ON c1.course = r1.course
                 INNER JOIN (
                     SELECT ct.course, ct.lecturer, rt.curriculum from courses AS ct
                     LEFT JOIN relation AS rt ON ct.course = rt.course
                 ) AS c2
                   ON c1.course != c2.course
                   AND (c1.lecturer = c2.lecturer OR r1.curriculum = c2.curriculum)
                 WHERE c1.course = ?'''
        for (conflicting_course, ) in self._cursor.execute(sql, (course, )):
            for existing_combination in self._dict_time[day, period]:
                if conflicting_course == existing_combination.course:
                    return False

        return True

    def _add_delta(self, course, day, period, room):
        # V: exceeded room capacity
        sql = '''SELECT courses.number_of_student - rooms.capacity
                 FROM courses
                 INNER JOIN rooms ON rooms.room = ?
                 WHERE course = ?'''
        V_sum = max(0, self._cursor.execute(sql, (room, course)).fetchone()[0])

        # U: scheduled to few times
        # This assumes the additon is valid, thus we already know there is
        # space for one more course. Adding the course will improve the score.
        U_sum = -1

        # P: room stability
        P_sum = 0
        used_rooms = {c.room for c in self._dict_course[course]}
        if (room not in used_rooms and len(used_rooms) > 0): P_sum = 1

        # W: to few working days
        sql = '''SELECT minimum_working_days
                 FROM courses
                 WHERE course = ?'''
        day_spread = {c.day for c in self._dict_course[course]}
        min_spread = self._cursor.execute(sql, (course, )).fetchone()[0]
        W_sum = 0
        if (len(day_spread) < min_spread and day not in day_spread): W_sum = -1

        # A: curriculum continuity
        A_sum = 0
        q_sql = '''SELECT curriculum
                   FROM relation
                   WHERE course = ?'''
        c_sql = '''SELECT course
                   FROM relation
                   WHERE curriculum = ?'''

        for (q, ) in self._database.execute(q_sql, (course, )):
            found_tm2_continuity = False
            found_tm1_continuity = False
            found_tp1_continuity = False
            found_tp2_continuity = False

            for (c, ) in self._cursor.execute(c_sql, (q, )):
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

        return {
            "U_sum": U_sum,
            "W_sum": W_sum,
            "A_sum": A_sum,
            "P_sum": P_sum,
            "V_sum": V_sum
        }

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

    def simulate_add(self, course, day, period, room, full=False):
        if not self._add_valid(course, day, period, room):
            return None

        penalties = self._add_delta(course, day, period, room)

        return penalties if full else self._total_cost(**penalties)

    def mutate_add(self, course, day, period, room, penalties=None):
        if penalties is None:
            penalties = self.simulate_add(course, day, period, room, full=True)

        if (penalties is None):
            raise Exception('bad combination (%d, %d, %d, %d)' % (
                course, day, period, add))

        # Update datastructures
        self._update_add(course, day, period, room)

        # Update penalties and objective
        self.penalties['U_sum'] += penalties['U_sum']
        self.penalties['W_sum'] += penalties['W_sum']
        self.penalties['A_sum'] += penalties['A_sum']
        self.penalties['P_sum'] += penalties['P_sum']
        self.penalties['V_sum'] += penalties['V_sum']
        self.objective += self._total_cost(**penalties)

    def _remove_valid(self, course, day, period, room):
        removed_combination = (course, day, period, room)
        # A combination has to exists to be removed
        for combination in self.schedule:
            if combination.all == removed_combination:
                return True
        return False

    def _remove_delta(self, course, day, period, room):
        # V: exceeded room capacity
        sql = '''SELECT courses.number_of_student - rooms.capacity
                 FROM courses
                 INNER JOIN rooms ON rooms.room = ?
                 WHERE course = ?'''
        V_sum = -max(0, self._cursor.execute(sql, (room, course)).fetchone()[0])

        # U: scheduled to few times
        U_sum = 1

        # P: room stability
        P_sum = 0
        all_rooms = {c.room for c in self._dict_course[course]}
        used_rooms = [c.room for c in self._dict_course[course] if c.room == room]
        if (len(all_rooms) > 1 and len(used_rooms) == 1): P_sum = -1

        # W: to few working days
        sql = '''SELECT minimum_working_days
                 FROM courses
                 WHERE course = ?'''
        day_spread = {c.day for c in self._dict_course[course]}
        used_days = [c.day for c in self._dict_course[course] if c.day == day]
        min_spread = self._cursor.execute(sql, (course, )).fetchone()[0]
        W_sum = 0
        if (len(day_spread) <= min_spread and len(used_days) == 1):
            W_sum = 1

        # A: curriculum continuity
        A_sum = 0
        q_sql = '''SELECT curriculum
                   FROM relation
                   WHERE course = ?'''
        c_sql = '''SELECT course
                   FROM relation
                   WHERE curriculum = ?'''

        for (q, ) in self._database.execute(q_sql, (course, )):
            found_tm2_continuity = False
            found_tm1_continuity = False
            found_tp1_continuity = False
            found_tp2_continuity = False

            for (c, ) in self._cursor.execute(c_sql, (q, )):
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

        return {
            "U_sum": U_sum,
            "W_sum": W_sum,
            "A_sum": A_sum,
            "P_sum": P_sum,
            "V_sum": V_sum
        }

    def _update_remove(self, course, day, period, room):
        # Create combination and remove, this uses an custom __eq__ function
        combination = Combination(course, day, period, room)
        self.schedule.remove(combination)

        # Maintain datastructures
        self._decrement_counter(self._sum_time, combination.course_room)
        self._decrement_counter(self._sum_room, combination.course_time)
        self._decrement_counter(self._sum_course, combination.time_room)
        self._decrement_counter(self._sum_time_room, combination.course)
        self._decrement_counter(self._sum_period_room, combination.course_day)
        self._remove_from_defafultdict(self._dict_time, combination.time, combination)
        self._remove_from_defafultdict(self._dict_course, combination.course, combination)

    def simulate_remove(self, course, day, period, room, full=False):
        if not self._remove_valid(course, day, period, room):
            return None

        penalties = self._remove_delta(course, day, period, room)

        return penalties if full else self._total_cost(**penalties)

    def mutate_remove(self, course, day, period, room, penalties=None):
        if penalties is None:
            penalties = self.simulate_remove(course, day, period, room, full=True)

        if (penalties is None):
            raise Exception('bad combination (%d, %d, %d, %d)' % (
                course, day, period, add))

        # Update datastructures
        self._update_remove(course, day, period, room)

        # Update penalties and objective
        self.penalties['U_sum'] += penalties['U_sum']
        self.penalties['W_sum'] += penalties['W_sum']
        self.penalties['A_sum'] += penalties['A_sum']
        self.penalties['P_sum'] += penalties['P_sum']
        self.penalties['V_sum'] += penalties['V_sum']
        self.objective += self._total_cost(**penalties)

    def _add_penalties(self, target, penalties):
        target['U_sum'] += penalties['U_sum']
        target['W_sum'] += penalties['W_sum']
        target['A_sum'] += penalties['A_sum']
        target['P_sum'] += penalties['P_sum']
        target['V_sum'] += penalties['V_sum']

    def simulate_swap(self, combination_a, combination_b, full=False):
        # Create new combinations
        a_on_b = (combination_a[0], ) + combination_b[1:]
        b_on_a = (combination_b[0], ) + combination_a[1:]

        # Try removing a
        remove_a = self.simulate_remove(*combination_a, full=True)
        if (remove_a is None):
            return None
        else:
            self._update_remove(*combination_a)

        # Try removing b and revert -a if failed
        remove_b = self.simulate_remove(*combination_b, full=True)
        if (remove_b is None):
            self._update_add(*combination_a)
            return None
        else:
            self._update_remove(*combination_b)

        # Try adding a_on_b and revert -a-b if failed
        add_a_on_b = self.simulate_add(*a_on_b, full=True)
        if (add_a_on_b is None):
            self._update_add(*combination_b)
            self._update_add(*combination_a)
            return None
        else:
            self._update_add(*a_on_b)

        # Try adding b_on_a and revert -a-b+a_on_b if failed
        add_b_on_a = self.simulate_add(*b_on_a, full=True)
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
        penalties = {"U_sum": 0, "W_sum": 0, "A_sum": 0, "P_sum": 0, "V_sum": 0}
        self._add_penalties(penalties, remove_a)
        self._add_penalties(penalties, remove_b)
        self._add_penalties(penalties, add_a_on_b)
        self._add_penalties(penalties, add_b_on_a)

        return penalties if full else self._total_cost(**penalties)

    def mutate_swap(self, combination_a, combination_b, penalties=None):
        if penalties is None:
            penalties = self.simulate_swap(combination_a, combination_b, full=True)

        if (penalties is None):
            raise Exception('bad combination swap((%d, %d, %d, %d), (%d, %d, %d, %d))' % (
                combination_a + combination_b))

        # Create new combinations
        a_on_b = (combination_a[0], ) + combination_b[1:]
        b_on_a = (combination_b[0], ) + combination_a[1:]

        # Create combination and remove, this uses an custom __eq__ function
        self._update_remove(*combination_a)
        self._update_remove(*combination_b)
        self._update_add(*a_on_b)
        self._update_add(*b_on_a)

        # Update penalties and objective
        self.penalties['U_sum'] += penalties['U_sum']
        self.penalties['W_sum'] += penalties['W_sum']
        self.penalties['A_sum'] += penalties['A_sum']
        self.penalties['P_sum'] += penalties['P_sum']
        self.penalties['V_sum'] += penalties['V_sum']
        self.objective += self._total_cost(**penalties)

    def export(self):
        return [c.all for c in self.schedule]

    def copy(self):
        return Solution(self._database, schedule=self.schedule)

    def insert(self, combination):
        self.schedule.append(Combination(*combination))
        self._precalc_sums()

    def remove(self, combination):
        self.schedule = [c for c in self.schedule if c.all != combination]
        self._precalc_sums()

    def swap(self, time_room_a, time_room_b):
        new_schedule = []
        combination_a = None
        combination_b = None

        # Find the combination objects (aka associated course number)
        for combination in self.schedule:
            if time_room_a == combination.time_room:
                combination_a = combination
            elif time_room_b == combination.time_room:
                combination_b = combination
            else:
                new_schedule.append(combination)

        # Add new combination objects to schedule
        if (combination_a is None and combination_b is None):
            return

        if (combination_b is not None):
            new_schedule.append(Combination(
                course=combination_b.course,
                day=time_room_a[0],
                period=time_room_a[1],
                room=time_room_a[2]
            ))
        if (combination_a is not None):
            new_schedule.append(Combination(
                course=combination_a.course,
                day=time_room_b[0],
                period=time_room_b[1],
                room=time_room_b[2]
            ))

        # Update schedule and calculate sum
        self.schedule = new_schedule
        self._precalc_sums()

    def _precalc_sums(self):
        self._sum_time.clear()
        self._sum_room.clear()
        self._sum_course.clear()
        self._sum_time_room.clear()
        self._sum_period_room.clear()
        self._dict_time.clear()
        self._dict_course.clear()

        for combination in self.schedule:
            self._sum_time[combination.course_room] += 1
            self._sum_room[combination.course_time] += 1
            self._sum_course[combination.time_room] += 1
            self._sum_time_room[combination.course] += 1
            self._sum_period_room[combination.course_day] += 1
            self._dict_time[combination.time].append(combination)
            self._dict_course[combination.course].append(combination)

    def missing_courses(self):
        cursor = self._database.cursor()
        courses = []
        sql = '''SELECT course, number_of_lectures
                    FROM courses'''
        for course, num_lectures in cursor.execute(sql):
            if num_lectures - self._sum_time_room[course] > 0:
                courses.append(course)

        return courses

    def existing_combinations(self):
        return [combination.all for combination in self.schedule]

    def valid(self):
        cursor = self._database.cursor()

        # s.t. (1b)
        sql = '''SELECT count(*) FROM unavailability
                 WHERE course = ? AND day = ? AND period = ?'''
        for (course, day, period), count in self._sum_room.items():
            # TODO: count should never be zero
            if (count == 0): continue

            # If there are more than one course in the room
            if (count > 1): return False

            # Check that course is "available" at this time
            F_ct = cursor.execute(sql, (course, day, period)).fetchone()[0]
            if F_ct == 1: return False

        # s.t. (1c)
        for (day, period, room), count in self._sum_course.items():
            # Don't overbook a room
            if (count > 1): return False

        # s.t. (1d)
        sql = '''SELECT number_of_lectures FROM courses
                 WHERE course = ?'''
        for course, count in self._sum_time_room.items():
            # TODO: count should never be zero
            if (count == 0): continue

            # Check that course is isn't scheduled too many times
            L_c = cursor.execute(sql, (course, )).fetchone()[0]
            if count > L_c: return False

        # s.t. (1e)
        # SQL for finding conflicting courses
        sql = '''SELECT DISTINCT c1.course as c1, c2.course as c2
                 FROM courses AS c1
                 LEFT JOIN relation AS r1 ON c1.course = r1.course
                 INNER JOIN (
                    SELECT ct.course, ct.lecturer, rt.curriculum from courses AS ct
                    LEFT JOIN relation AS rt ON ct.course = rt.course
                 ) AS c2
                   ON c1.course > c2.course
                   AND (c1.lecturer = c2.lecturer OR r1.curriculum = c2.curriculum)'''
        for (course1, course2) in cursor.execute(sql):
            for day in range(0, self._database.days):
                for period in range(0, self._database.periods_per_day):
                    s = self._sum_room[(course1, day, period)] + \
                        self._sum_room[(course2, day, period)]
                    if (s > 1): return False

        return True

    def _room_capacity(self, cursor):
        # exceeded room capacity
        V_sum = 0
        sql = '''SELECT courses.number_of_student - rooms.capacity
                    FROM courses
                    INNER JOIN rooms ON rooms.room = ?
                    WHERE course = ?'''
        for combination in self.schedule:
            exceeded = cursor.execute(sql, combination.room_course).fetchone()[0]
            V_sum += max(0, exceeded)

        return V_sum

    def _unscheduled(self, cursor):
        # scheduled to few times
        U_sum = 0
        sql = '''SELECT course, number_of_lectures
                    FROM courses'''
        for course, num_lectures in cursor.execute(sql):
            U_sum += max(0, num_lectures - self._sum_time_room[course])

        return U_sum

    def _room_stability(self, cursor):
        # room stability
        P_sum = 0
        room_stability = collections.defaultdict(set)
        for (course, room), count in self._sum_time.items():
            # TODO: count should never be zero
            if (count == 0): continue
            room_stability[course].add(room)
        for rooms in room_stability.values():
            P_sum += max(0, len(rooms) - 1)

        return P_sum

    def _minimum_working_days(self, cursor):
        # to few working days
        W_sum = 0
        sql = '''SELECT course, minimum_working_days
                    FROM courses'''
        day_spread = collections.defaultdict(set)
        for (course, day), count in self._sum_period_room.items():
            # TODO: count should never be zero
            if (count == 0): continue
            day_spread[course].add(day)
        for course, min_spread in cursor.execute(sql):
            W_sum += max(0, min_spread - len(day_spread[course]))

        return W_sum

    def _curriculum_compactness(self, cursor):
        # curriculum continuity
        A_sum = 0
        sql = '''SELECT course
                    FROM relation
                    WHERE curriculum = ?'''
        for q in range(0, self._database.curricula):
            for day in range(0, self._database.days):
                # Given (c in q(i), d) count non adjacent courses
                prev_exist = False
                added_one = False
                for period in range(0, self._database.periods_per_day):
                    found_course = False
                    for (course, ) in cursor.execute(sql, (q, )):
                        if self._sum_room[(course, day, period)] > 0:
                            found_course = True

                            if prev_exist:
                                # Compenstate for [_, 1, 2] where the first
                                # course(1) would add one but actaully be
                                # adjacent
                                if added_one: A_sum -= 1
                                added_one = False
                            else:
                                A_sum += 1
                                added_one = True
                            break

                    prev_exist = found_course

        return A_sum

    def cost_seperated(self):
        cursor = self._database.cursor()
        U_sum = self._unscheduled(cursor)
        W_sum = self._minimum_working_days(cursor)
        A_sum = self._curriculum_compactness(cursor)
        P_sum = self._room_stability(cursor)
        V_sum = self._room_capacity(cursor)

        return {
            "U_sum": U_sum,
            "W_sum": W_sum,
            "A_sum": A_sum,
            "P_sum": P_sum,
            "V_sum": V_sum
        }

    def _total_cost(self, U_sum, W_sum, A_sum, P_sum, V_sum):
        return 10 * U_sum + 5 * W_sum + 2 * A_sum + P_sum + V_sum

    def cost(self):
        return self._total_cost(**self.cost_seperated())

    def __str__(self):
        seperated = self.cost_seperated()
        cost = self._total_cost(**seperated)

        header = textwrap.dedent("""\
        Unscheduled {U_sum}
        RoomCapacity {V_sum}
        MinimumWorkingDays {W_sum}
        CurriculumCompactness {A_sum}
        RoomStability {P_sum}
        Objective {cost}
        """.format(cost=cost, **seperated))

        body = ""
        for combination in self.schedule:
            body += str(combination) + "\n"

        return header + body
