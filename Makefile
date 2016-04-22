
test-solver:
	python3 code/solver.py \
		code/dataset/TestDataUTT/Test01/basic.utt \
		code/dataset/TestDataUTT/Test01/courses.utt \
		code/dataset/TestDataUTT/Test01/lecturers.utt \
		code/dataset/TestDataUTT/Test01/rooms.utt \
		code/dataset/TestDataUTT/Test01/curricula.utt \
		code/dataset/TestDataUTT/Test01/relation.utt \
		code/dataset/TestDataUTT/Test01/unavailability.utt \
		300

test:
	nosetests code/test/*
