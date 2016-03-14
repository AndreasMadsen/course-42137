
import _setup
from nose.tools import *

import dataset

database = dataset.Database.from_id(1)
database.close()
