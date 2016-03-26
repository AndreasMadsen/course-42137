import sys
import os.path as path

import collections

thisdir = path.dirname(path.realpath(__file__))
datasetdir = path.join(thisdir, 'TestDataUTT')

class Database:
    def __init__(self,
                 basic, courses, lecturers, rooms, curricula, relation, unavailability,
                 directory=None):

        self.directory = directory

        # Load basic.utt attributes
        with open(basic, 'r') as f:
            data = f.readlines()[1].split()
            Meta = collections.namedtuple('Meta', [
                'courses', 'rooms', 'days',
                'periods_per_day', 'curricula',
                'constraints', 'lecturers'
            ])

            self.meta = Meta(
                courses=int(data[0]),
                rooms=int(data[1]),
                days=int(data[2]),
                periods_per_day=int(data[3]),
                curricula=int(data[4]),
                constraints=int(data[5]),
                lecturers=int(data[6])
            )

        # Load database content
        self.courses = self._load_courses(courses)
        self.curricula = self._load_relation(relation)
        self.rooms = self._load_rooms(rooms)
        self.unavailability = self._load_unavailability(unavailability)

        # Bind data to course objects
        self._bind_curricula()
        self._bind_conflicts()

    @classmethod
    def from_id(clc, id):
        database_files = path.join(datasetdir, "Test%02d" % id)
        return clc(
            basic=path.join(database_files, 'basic.utt'),
            courses=path.join(database_files, 'courses.utt'),
            curricula=path.join(database_files, 'curricula.utt'),
            lecturers=path.join(database_files, 'lecturers.utt'),
            relation=path.join(database_files, 'relation.utt'),
            rooms=path.join(database_files, 'rooms.utt'),
            unavailability=path.join(database_files, 'unavailability.utt'),
            directory=database_files
        )

    def _load_courses(self, filepath):
        Course = collections.namedtuple('Course', [
            'course', 'lecturer', 'number_of_lectures',
            'minimum_working_days', 'number_of_student',
            'curricula', 'conflicts'
        ])

        with open(filepath, 'r') as f:
            return {
                a: Course(a, b, c, d, e, [], []) for (a, b, c, d, e) in _parse_file(f)
            }

    def _load_rooms(self, filepath):
        Room = collections.namedtuple('Room', [
            'room', 'capacity'
        ])

        with open(filepath, 'r') as f:
            return {
                a: Room(a, b) for (a, b) in _parse_file(f)
            }

    def _load_relation(self, filepath):
        Curriculum = collections.namedtuple('Curriculum', [
            'curriculum', 'courses'
        ])

        table = dict()
        with open(filepath, 'r') as f:
            for (curriculum, course) in _parse_file(f):
                if curriculum in table:
                    table[curriculum].courses.append(course)
                else:
                    table[curriculum] = Curriculum(curriculum, [course])
        return table

    def _load_unavailability(self, filepath):
        Unavailability = collections.namedtuple('Unavailability', [
            'course', 'day', 'period'
        ])

        with open(filepath, 'r') as f:
            return {
                Unavailability(a, b, c) for (a, b, c) in _parse_file(f)
            }

    def _bind_curricula(self):
        for (curriculum, courses) in self.curricula.values():
            for course in courses:
                self.courses[course].curricula.append(curriculum)

    def _bind_conflicts(self):
        for course in self.courses.values():
            curricula = set(course.curricula)
            for other in self.courses.values():
                # Don't be conflict with itself
                if other.course == course.course:
                    continue

                # same lecturer
                if other.lecturer == course.lecturer:
                    course.conflicts.append(other.course)
                    continue

                # shared curriculum
                for other_curricula in other.curricula:
                    if other_curricula in curricula:
                        course.conflicts.append(other.course)
                        break

def _parse_file(f):
    next(f)  # skip header
    data = (
        [(int(token[1:]) if token[0].isalpha() else int(token)) for token in line.split()]
        for line in f
    )  # split lines
    return data
