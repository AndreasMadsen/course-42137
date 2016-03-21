
import collections

from solution.combination import Combination

class Solution:
    def __init__(self, database, schedule=None):
        self.schedule = []
        self._database = database

        self._sum_room = collections.Counter()
        self._sum_course = collections.Counter()
        self._sum_time_room = collections.Counter()

        # Add schedule list if provided
        if (schedule is not None):
            self.schedule = [Combination(*item) for item in schedule]
            self._precalc_sums()

    def _precalc_sums(self):
        for combination in self.schedule:
            self._sum_room[combination.course_time] += 1
            self._sum_course[combination.time_room] += 1
            self._sum_time_room[combination.course] += 1

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

            # Check that course is "available" at this time
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
