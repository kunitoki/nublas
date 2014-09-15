from django.template.base import add_to_builtins

# import models
from .db.models.agenda import *
from .db.models.association import *
from .db.models.contact import *
from .db.models.types import *

# register tags
add_to_builtins("nublas.templatetags.nublas_extends")
add_to_builtins("nublas.templatetags.nublas_include")
