import argparse
import os
import sys

def shelp():
	print("No action specified!")
	print("help:")
	print("cproxy - a proxy between cpp_build_utils and CMake")
	print("Usage:")
	print("\tcproxy <action> ... [options]")
	print("Actions:")
	print("\tbuild - builds current cmake project")
	print("\tclean - do clean")
	print("\tcmgen/gen - generate cmake project from cmgen.json and configure it")
	print("\tconfigure/conf - configure current cmake project")
	print("\tdoc - run doxygen")
	print("\tdoc_g - generate doxygen config")
	print("\tfetch <repo> - fetch a github repo (`owner/name`) using git")
	print("\thelp - shows this")
	print("\tinstall - install built project")
	print("\tinstall_git_cmake - fetch (into current dir!) and install cmake project from github repo #NOT TESTED YET#")
	print("\tnew <name> - crates new cmake project")
	print("\tnew_cmg <name> - creates new cmgen project")
	print("\ttest - test current project; options are forwarded to ctest, so check ctest's help for this; but it runs all tests by default")
	print("\tversion - show version")
	print("Global options:")
	print("\t--verbose  -v   show ran commands (doesn't work with cproxy test)")
	print("Options:")
	print("\tbuild")
	print("\t\t--clean   do clean build")
	print("\tconfigure/cmgen - run cproxy build -h to see it's help")
	sys.exit(1)

for a in sys.argv[1:]:
	if not a.startswith("-"):
		action = a
		break
else:
	shelp()

if action in ["fetch", "install_git_cmake", "new", "new_cmg"]:
	aargs = [a for a in sys.argv[1:] if not a.startswith('-')]
	if len(aargs) < 2:
		print("cproxy " + action + "<name> needs a name argument")
	a2 = aargs[1]

verbose = "--verbose" in sys.argv or any(a.startswith('-') and 'v' in a for a in sys.argv)

def cmd(c):
	if verbose:
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
def configure(desc):
	parser = argparse.ArgumentParser(prog=f"cproxy {action}", description=desc)
	parser.add_argument("action", type=str, help="The action - conf/configure")
	parser.add_argument("--mgw", action="store_true", help="use MinGW Makefiles as generator")
	parser.add_argument("--debug", action="store_true", help="do debug build (for configure!)")
	parser.add_argument("--release", action="store_true", help="do release build (for configure!)")
	parser.add_argument("--tests", action="store_true", help="build tests (for configure!)")
	parser.add_argument("-v", "--verbose", action="store_true", help="show ran commands")
	args = parser.parse_args()
	cmake_args = ""
	if args.debug:
		cmake_args += " -DCMAKE_BUILD_TYPE=Debug"
	elif args.release:
		cmake_args += " -DCMAKE_BUILD_TYPE=Release"
	if args.mgw:
		cmake_args += " -G\"MinGW Makefiles\""
	if args.tests:
		cmake_args += " -DBUILD_TESTING=ON"
	cmd(f"cmake -S . -B build{cmake_args}")

if action == "build":
	cmd(f"cmake --build build{' --clean-first' if '--clean' in sys.argv else ''}")
elif action == "clean":
	cmd("cmake --build build --target clean")
elif action == "cmgen" or action == "gen":
	cmd(sys.executable + " " + os.path.dirname(os.path.realpath(__file__)) + "/cmake_gen.py ./cmgen.json ./")
	configure("Generate CMake project from cmgen.json and configure it")
elif action == "configure" or action == "conf":
	configure("Configure current cmake project")
elif action == "doc":
	cmd(f"doxygen doxygen.cfg")
elif action == "doc_g":
	cmd(f"doxygen -g doxygen.cfg")
elif action == "fetch":
	cmd(f"git clone https://github.com/{a2}.git")
elif action == "help":
	shelp()
elif action == "install":
	cmd("cmake --install build")
elif action == "install_git_cmake":
	cmd(f"git clone https://github.com/{a2}.git")
	os.chdir(a2.split('/')[1])
	cmd(f"cmake -S . -B build -DCMAKE_BUILD_TYPE=Release {' '.join(sys.argv[3:])}")
	cmd(f"cmake --build build")
	cmd(f"cmake --install build")
elif action == "new":
	gen_project(a2, "default_cmake_proj")
elif action == "new_cmg":
	gen_project(a2, "default_cmgen_proj")
elif action == "test":
	os.chdir("./build")
	cmd("ctest " + " ".join(sys.argv[2:]))
	os.chdir("../")
elif action == "version":
	print("cproxy.py v1.0.0")
