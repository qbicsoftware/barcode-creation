# -*- coding: utf-8 -*-
# tests different barcode scripts with randomly generated data
import json, os, random, string, datetime

python = "python2.7"
ALPH = string.ascii_uppercase.replace("Z","").replace("Y","")
path = os.path.dirname(os.path.realpath(__file__))

#json_data = json.dumps(data)

def random_string(length, alphabet):
  return ''.join(random.choice(alphabet) for _ in range(length))

# does not create correct checksums!
def random_barcode(project = None):
  digits = random_string(3, string.digits)
  end = random_string(1, ALPH) + random_string(1, ALPH + string.digits)
  if project:
    return project+digits+end
  else:
    return random_project_code() + digits + end

def random_project_code():
  return "Q" + random_string(4, ALPH + string.digits)

def random_info():
  length = random.randint(1,20)
  return random_string(length, ALPH + string.digits)

def test_tubes(amount):
  script = os.path.join(path, "tube_barcodes.py")
  for i in range(amount):
    code = random_barcode()
    name = str(i+1).zfill(4)+"_"+code
    info1 = random_info()
    info2 = random_info()
    cmd = python+" "+script+" "+name+" "+code+" "+info1+" "+info2+" testmode"
    os.system(cmd)

def test_sheet_images(amount, project = None):
  script = os.path.join(path, "sheet_barcodes.py")
  codes = []
  for i in range(amount):
    if project:
      code = random_barcode(project)
    else:
      code = random_barcode()
    codes.append(code)
    os.system(python+" "+script+" "+code+" testmode")
  return codes

def test_sheet():
  script = os.path.join(path, "samp_sheet.py")
  project = random_project_code()
  codes = test_sheet_images(3, project)
  print (project)
  investigator = {"first" : "Ändreas", "last" : "Friedrüfch", "phone" : "12345123123"}
  contact = {"first" : "Chriß", "last" : "Möhr", "phone" : "98328472384"}
  samples = []
  for i in range(3):
    s = {"code" : codes[i], "info" : random_info(), "alt_info" : random_info()}
    samples.append(s)
  obj = {"project_code" : project, "project_name" : "A test project!", "samples" : samples, "cols" : ["first info", "second info"], "contact" : contact, "investigator" : investigator}
  jsonPath = 'test.json'
  with open(jsonPath, 'w') as outfile:
    json.dump(obj, outfile)
  os.system(python+" "+script+" "+jsonPath+" testmode")
  os.remove(jsonPath)

#def reset_config_path():
#  config = str(os.path.join(path, "properties_path.txt"))
#  os.system("cp "+config+".backup "+config)

if __name__ == '__main__':
  print ("Testing")
  #test_tubes(2)
  test_sheet()
