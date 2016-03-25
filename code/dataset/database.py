import sys
import os.path as path

import sqlite3

thisdir = path.dirname(path.realpath(__file__))
datasetdir = path.join(thisdir, 'TestDataUTT')

class Database:
    def __init__(self,
                 basic, courses, lecturers, rooms, curricula, relation, unavailability,
                 directory=None):

        self.directory = directory
        self._database = sqlite3.connect(':memory:')
        self._setup_tables()

        # Load basic.utt attributes
        with open(basic, 'r') as f:
            data = f.readlines()[1].split()

            self.courses = int(data[0])
            self.rooms = int(data[1])
            self.days = int(data[2])
            self.periods_per_day = int(data[3])
            self.curricula = int(data[4])
            self.constraints = int(data[5])
            self.lecturers = int(data[6])

        # Load database content
        self._load_courses(courses)
        self._load_curricula(curricula)
        self._load_lecturers(lecturers)
        self._load_relation(relation)
        self._load_rooms(rooms)
        self._load_unavailability(unavailability)

        # Commit data
        self.commit()

    def __getattr__(self, attr):
        return getattr(self._database, attr)

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

    def _setup_tables(self):
        self.executescript('''
            CREATE TABLE lecturers (
                lecturer INTEGER PRIMARY KEY NOT NULL
            );

            CREATE TABLE courses (
                course               INTEGER PRIMARY KEY NOT NULL,
                lecturer             INTEGER NOT NULL,
                number_of_lectures   INTEGER NOT NULL,
                minimum_working_days INTEGER NOT NULL,
                number_of_student    INTEGER NOT NULL,
                FOREIGN KEY (lecturer) REFERENCES lecturers(lecturer)
            );

            CREATE TABLE curricula (
                curriculum        INTEGER PRIMARY KEY NOT NULL,
                number_of_courses INTEGER NOT NULL
            );

            CREATE TABLE relation (
                curriculum INTEGER NOT NULL,
                course     INTEGER NOT NULL,
                PRIMARY KEY (curriculum, course),
                FOREIGN KEY (curriculum) REFERENCES curricula(curriculum),
                FOREIGN KEY (course) REFERENCES courses(course)
            );

            CREATE TABLE rooms (
                room     INTEGER PRIMARY KEY NOT NULL,
                capacity INTEGER NOT NULL
            );

            CREATE TABLE unavailability (
                course INTEGER NOT NULL,
                day    INTEGER NOT NULL,
                period INTEGER NOT NULL,
                PRIMARY KEY (course, day, period),
                FOREIGN KEY (course) REFERENCES courses(course)
            );
        ''')

    def _load_courses(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO courses VALUES (?, ?, ?, ?, ?)',
                ((a[1:], b[1:], c, d, e) for (a, b, c, d, e) in _parse_file(f))
            )

    def _load_lecturers(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO lecturers VALUES (?)',
                ((a[1:], ) for (a, ) in _parse_file(f))
            )

    def _load_rooms(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO rooms VALUES (?, ?)',
                ((a[1:], b) for (a, b) in _parse_file(f))
            )

    def _load_curricula(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO curricula VALUES (?, ?)',
                ((a[1:], b) for (a, b) in _parse_file(f))
            )

    def _load_relation(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO relation VALUES (?, ?)',
                ((a[1:], b[1:]) for (a, b) in _parse_file(f))
            )

    def _load_unavailability(self, filepath):
        with open(filepath, 'r') as f:
            self.executemany(
                'INSERT INTO unavailability VALUES (?, ?, ?)',
                ((a[1:], b, c) for (a, b, c) in _parse_file(f))
            )

    def close(self):
        self.executescript('''
            DROP TABLE courses;
            DROP TABLE curricula;
            DROP TABLE lecturers;
            DROP TABLE relation;
            DROP TABLE rooms;
            DROP TABLE unavailability;
        ''')
        self._database.close()

def _parse_file(f):
    next(f)  # skip header
    data = (line.split() for line in f)  # split lines
    return data
