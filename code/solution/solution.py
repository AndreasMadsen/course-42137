
import collections
import textwrap

from solution.combination import Combination

class Solution:
    def __init__(self, database, schedule=None):
        self.schedule = []
        self._database = database

        self._sum_time = collections.Counter()
        self._sum_room = collections.Counter()
        self._sum_course = collections.Counter()
        self._sum_time_room = collections.Counter()
        self._sum_period_room = collections.Counter()

        # Add schedule list if provided
        if (schedule is not None and len(schedule) > 0):
            if isinstance(schedule[0], Combination):
                self.schedule = list(schedule)
            else:
                self.schedule = [Combination(*item) for item in schedule]
            self._precalc_sums()

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

        for combination in self.schedule:
            self._sum_time[combination.course_room] += 1
            self._sum_room[combination.course_time] += 1
            self._sum_course[combination.time_room] += 1
            self._sum_time_room[combination.course] += 1
            self._sum_period_room[combination.course_day] += 1

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
