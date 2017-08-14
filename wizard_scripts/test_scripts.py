# tests different barcode scripts with randomly generated data
import json, os, random, string, datetime

alphabet = string.ascii_uppercase.replace("Z","").replace("Y","")
path = os.path.dirname(os.path.realpath(__file__))

#json_data = json.dumps(data)

# does not create correct checksums!
def random_barcode(project = None):
  if project:
    return project+''.join(random.choice(alphabet + string.digits) for _ in range(5))
  else:
    return "Q"+''.join(random.choice(alphabet + string.digits) for _ in range(9))

def random_project_code():
  return "Q"+''.join(random.choice(alphabet + string.digits) for _ in range(4))

def random_info():
  length = random.randint(1,20)
  return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def test_tubes(amount):
  script = os.path.join(path, "tube_barcodes.py")
  for i in range(amount):
    code = random_barcode()
    name = str(i+1).zfill(4)+"_"+code
    info1 = random_info()
    info2 = random_info()
    cmd = "python "+script+" "+name+" "+code+" "+info1+" "+info2
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
    os.system("python "+script+" "+code)
  return codes

def test_sheet():
  script = os.path.join(path, "samp_sheet.py")
  project = random_project_code()
  codes = test_sheet_images(3, project)
  print project
  investigator = {"first" : "Andreas", "last" : "Friedrich", "phone" : "12345123123"}
  contact = {"first" : "Chris", "last" : "Mohr", "phone" : "98328472384"}
  samples = []
  for i in range(3):
    s = {"code" : codes[i], "info" : random_info(), "alt_info" : random_info()}
    samples.append(s)
  obj = {"project_code" : project, "project_name" : "A test project!", "samples" : samples, "cols" : ["first info", "second info"], "contact" : contact, "investigator" : investigator}
  jsonPath = 'test.json'
  with open(jsonPath, 'w') as outfile:
    json.dump(obj, outfile)
  os.system("python "+script+" "+jsonPath)

def set_test_paths():
  test_config_info = os.path.join(path, "test_path.txt")
  config_info = os.path.join(path, "properties_path.txt")
  testfolder = os.path.join(path, "tests")

  with open(os.path.join(path,"properties_path.txt")) as pp:
    config_path = pp.readline().strip()
  pp.close()
  config = open(config_path)
  settings = {}
  for line in config:
    if "=" in line:
      line = line.split("=")
      settings[line[0].strip()] = line[1].strip()
  config.close()
  os.system("cp "+config_info+" "+config_info+".backup")
  with open(os.path.join(testfolder,"barcode.properties"), 'w') as outfile:
    outfile.write("barcode.postscript = "+settings["barcode.postscript"]+"\n")
    outfile.write("barcode.results = "+testfolder+"\n")
    outfile.write("tmp.folder = "+os.path.join(testfolder,"tmp")+"\n")
  outfile.close()
  os.system("cp "+test_config_info+" "+config_info)

def reset_config_path():
  config = str(os.path.join(path, "properties_path.txt"))
  os.system("cp "+config+".backup "+config)

if __name__ == '__main__':
  day = datetime.datetime.today().weekday()
  if day == 2:
    print "It is Wednesday my dudes!" #sorry

  print "Setting test environment."
  set_test_paths()
  print "Testing"
  test_tubes(2)
  test_sheet()
  print "Resetting paths to previous configuration."
  reset_config_path()
