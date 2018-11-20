import inspect 
import argparse
import pickle
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()

from django.contrib.auth.models import User
from client_area import models as cl_models
from user_management import models as u_models
from budget import models as b_models
from facebook_dashboard import models as fd_models
from bing_dashboard import models as bi_models
from adwords_dashboard import models as ad_models



all_modules = [
  [("User", User)],
  inspect.getmembers(cl_models, inspect.isclass),
  inspect.getmembers(u_models, inspect.isclass),
  inspect.getmembers(b_models, inspect.isclass),
  inspect.getmembers(fd_models, inspect.isclass),
  inspect.getmembers(ad_models, inspect.isclass),
  inspect.getmembers(bi_models, inspect.isclass),
]


def save(data):
  for module, models in data.items():
    print("Saving models from module {}".format(module))
    for m in models:
      m.save()

  return

def dump(fname):
  data = {}
  for module in all_modules:
    for m in module:
      if hasattr(m[1], "objects"):
        print("Dumping models from  {}".format(m[0]))
        data[m[0]] = list(m[1].objects.all())

  with open(fname, "wb") as handle:
    pickle.dump(data, handle)
  return


def load(fname):
  with open(fname, "rb") as handle:
    data = pickle.load(handle)
  
  save(data)



def main():
  commands = {
    "load": load,
    "dump": dump
  }
  parser = argparse.ArgumentParser(description="Export or load data")
  parser.add_argument("filename", help="The file where to dump or load")
  parser.add_argument("command", choices=["load", "dump"], help="command to execute")
  args = vars(parser.parse_args())
  commands[args["command"]](args["filename"])


if __name__ == '__main__':
  main()