
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
    def time_room(self):
        return (self.day, self.period, self.room)
