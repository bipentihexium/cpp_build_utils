import argparse
import os
import sys

parser = argparse.ArgumentParser(prog="cproxy", description="a proxy between cpp_build_utils and CMake")
parser.add_argument("action", choices=["build", "configure", "gen", "install", "new", "new_json", "test"], type=str, help="Action to perform")
parser.add_argument("action_args", type=str, help="Action arguments", nargs='*')
parser.add_argument("--version", action="version", version="%(prog)s v1.0.0.0", help="Show version")
parser.add_argument("-v", "--verbose", action="store_true", help="show ran commands")
parser.add_argument("--mgw", action="store_true", help="use MinGW Makefiles as generator")
parser.add_argument("--debug", action="store_true", help="do debug build (for configure!)")
parser.add_argument("--release", action="store_true", help="do release build (for configure!)")
parser.add_argument("--tests", action="store_true", help="build tests (for configure!)")
args = parser.parse_args()

def cmd(c):
	if args.verbose:
		print(f"cproxy> {c}")
	os.system(c)

def wfile(file, data):
	with open(file, "w") as f:
		f.write(data)

def copy_proj_template(src, dest, project):
	if os.path.isdir(src):
		if not os.path.isdir(dest):
			os.makedirs(dest)
		files = os.listdir(src)
		for f in files:
			copy_proj_template(os.path.join(src, f), os.path.join(dest, f), project)
	else:
		with open(src, "rb") as f:
			contents = f.read()
		if 0 not in contents:
			contents = contents.replace(b"%{PROJECT_NAME}", project.encode("utf-8"))
		with open(dest, "wb") as f:
			f.write(contents)
def gen_project(project, template_dir):
	ppath = os.getcwd() + "/" + project
	tpath = os.path.dirname(os.path.realpath(__file__)) + "/" + template_dir
	copy_proj_template(tpath, ppath, project)

bt = ""
if args.debug:
	bt = " -DCMAKE_BUILD_TYPE=Debug"
elif args.release:
	bt = " -DCMAKE_BUILD_TYPE=Release"
g = ""
if args.mgw:
	g = " -G\"MinGW Makefiles\""
bo = ""
if args.tests:
	bo = " -DBUILD_TESTING=ON"


if args.action == "build":
	cmd("cmake --build build")
elif args.action == "configure":
	cmd(f"cmake -S . -B build{g}{bt}{bo}")
elif args.action == "gen":
	cmd(sys.executable + " " + os.path.dirname(os.path.realpath(__file__)) + "/cmake_gen.py ./cmgen.json ./")
	cmd(f"cmake -S . -B build{g}{bt}{bo}")
elif args.action == "install":
	cmd("cmake --install build")
elif args.action == "new":
	if not args.action_args:
		parser.error("'new' needs an argument (cproxy new <project_name>)")
	project = args.action_args[0]
	gen_project(project, "default_cmake_proj")
elif args.action == "new_json":
	if not args.action_args:
		parser.error("'new' needs an argument (cproxy new <project_name>)")
	project = args.action_args[0]
	gen_project(project, "default_cmgen_proj")
elif args.action == "test":
	os.chdir("./build")
	cmd("ctest")
	os.chdir("../")
