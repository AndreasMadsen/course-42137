
class Combination:
    def __init__(self, course, day, period, room):
        self.course = course
        self.day = day
        self.period = period
        self.room = room

    @property
    def time(self):
        return (self.day, self.period)

    @property
    def course_time(self):
        return (self.course, self.day, self.period)

    @property
    def course_room(self):
        return (self.course, self.room)

    @property
    def room_course(self):
        return (self.room, self.course)

    @property
    def time_room(self):
        return (self.day, self.period, self.room)

    @property
    def course_day(self):
        return (self.course, self.day)

    def __str__(self):
        return "C%04d %1d %1d R%04d" % (
            self.course, self.day, self.period, self.room
        )
