import json
import os
import sys

extdir = os.path.dirname(os.path.realpath(__file__)) + "/extensions/"
def get_or(d:dict, index, default):
	return d[index] if index in d else default
def gen_trg(p:dict, trg:dict, ext_trgs:dict):
	for ext in [*get_or(trg, 'cmgen-extensions', []), *get_or(p, 'global-cmgen-extensions', [])]:
		extd = ext_trgs[ext]
		if 'cmake_pre' in extd: trg['cmake_pre'] = get_or(trg, 'cmake_pre', "") + (extd['cmake_pre'] % trg['name'])
		if 'cmake_post' in extd: trg['cmake_post'] = get_or(trg, 'cmake_post', "") + (extd['cmake_post'] % trg['name'])
	out_src = f"{get_or(trg, 'cmake_pre', '')}" +\
		f"add_{'executable' if trg['type'] == 'executable' else 'library'}({trg['name']}" +\
		f"{trg['type'].upper() if trg['type'] != 'executable' else ''} {' '.join(trg['sources'])})\n"
	includes = [trg['include_dir']] if 'include_dir' in trg else []
	link_dirs = []
	links = []
	if 'depends' in trg:
		links.extend(trg['depends'])
	if 'includes' in trg:
		includes.extend(trg['includes'])
	if 'links' in trg:
		links.extend(trg['links'])
	if 'link_dirs' in trg:
		link_dirs.extend(trg['link_dirs'])
	if includes:
		out_src += f"target_include_directories({trg['name']} PUBLIC {' '.join(includes)})\n"
	if link_dirs:
		out_src += f"target_link_directories({trg['name']} PUBLIC {' '.join(link_dirs)})\n"
	if links:
		out_src += f"target_link_libraries({trg['name']} PUBLIC {' '.join(links)})\n"
	if 'features' in trg:
		out_src += f"target_compile_features({trg['name']} PUBLIC {''.join(trg['features'])})\n"
	if 'cmake_post' in trg:
		out_src += f"{trg['cmake_post']}\n"
	return out_src
def generate(p:dict, outdir):
	ext_trgs = {}
	for ext in [*get_or(p, 'cmgen-extensions', []), *get_or(p, 'global-cmgen-extensions', [])]:
		with open(extdir + ext + ".json", "rb") as f:
			extd = json.load(f)
		if 'cmake_pre' in extd: p['cmake_pre'] = get_or(p, 'cmake_pre', "") + extd['cmake_pre']
		if 'cmake_post' in extd: p['cmake_post'] = get_or(p, 'cmake_post', "") + extd['cmake_post']
		ext_trgs[ext] = get_or(extd, 'target', {})
	out = "cmake_minimum_required(VERSION 3.14)\n" +\
		f"project({p['project']} VERSION {p['version']} LANGUAGES {get_or(p, 'languages', 'C CXX')})\n"
	if 'default_build_type' in p:
		out += "if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)\n" +\
			f"\tset(CMAKE_BUILD_TYPE \"{p['default_build_type']}\")\n" +\
			f"\tmessage(STATUS \"Build type set to {p['default_build_type']} because build type wasn't specified.\")\n" +\
			"endif()\n"
	if 'standard' in p:
		out += "if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)\n"
		for lang, std in p['standard'].items():
			out += f"\tset(CMAKE_{lang}_STANDARD {std})\n" +\
				f"\tset(CMAKE_{lang}_STANDARD_REQUIRED ON)\n"
		out += "endif()\n"
	if 'output' in p:
		out += f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY {p['output']})\n" +\
			f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY {p['output']})\n" +\
			f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY {p['output']})\n"
	if 'cmake_pre' in p:
		out += f"{p['cmake_pre']}\n"
	depn = []
	if 'dependencies' in p:
		out += "\ninclude(FetchContent)\n"
		fetch_deps = []
		for dep in p['dependencies']:
			if dep['mode'] == "github":
				out += "FetchContent_Declare(\n" +\
					f"\t{dep['name']}\n" +\
					f"\tGIT_REPOSITORY https://github.com/{dep['repo']}.git\n" +\
					f"\tGIT_TAG {dep['tag']}\n" +\
					f"\tFIND_PACKAGE_ARGS {get_or(dep, 'find_package_args', '')}\n" +\
					")\n"
				fetch_deps.append(dep['name'])
			elif dep['mode'] == "git":
				out += "FetchContent_Declare(\n" +\
					f"\t{dep['name']}\n" +\
					f"\tGIT_REPOSITORY {dep['repo']}\n" +\
					f"\tGIT_TAG {dep['tag']}\n" +\
					f"\tFIND_PACKAGE_ARGS {get_or(dep, 'find_package_args', '')}\n" +\
					")\n"
				fetch_deps.append(dep['name'])
			elif dep['mode'] == "fetchfile":
				out += "FetchContent_Declare(\n" +\
					f"\t{dep['name']}\n" +\
					f"\tURL {dep['url']}\n"
				if 'url_hash' in dep:
					out += f"\tURL_HASH {dep['url_hash']}\n"
				out += ")\n"
				fetch_deps.append(dep['name'])
			elif dep['mode'] == "fetch":
				out += "FetchContent_Declare(\n" +\
					f"\t{dep['name']}\n" +\
					f"\t{dep['fetch_method']}\n" +\
					")\n"
				fetch_deps.append(dep['name'])
			elif dep['mode'] == "package":
				if 'options' in dep:
					out += f"find_package({dep['name']} {dep['options']})\n"
				else:
					out += f"find_package({dep['name']})\n"
			depn.append(dep['name'])
		if fetch_deps:
			out += f"FetchContent_MakeAvailable({' '.join(fetch_deps)})\n"

	out += "\n"
	targets = []
	for trg in p['targets']:
		out += f"add_subdirectory({trg['source_dir']})\n"
		out_src = gen_trg(p, trg, ext_trgs)
		with open(outdir + "/" + trg['source_dir'] + "/CMakeLists.txt", "w") as f:
			f.write(out_src)
		targets.append(trg['name'])
	if 'tests' in p:
		tests = p['tests']
		out += f"\nif((CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME OR {p['project'].upper()}_BUILD_TESTING) AND BUILD_TESTING)\n" +\
			"\tenable_testing()\n" +\
			"\tinclude(CTest)\n" +\
			f"\tadd_subdirectory({tests['dir']})\n" +\
			"endif()\n"
		out_test = f"{get_or(tests, 'cmake_pre', '')}\n"
		for t in tests['tests']:
			if t['type'] == "executable":
				out_test += gen_trg(p, t, ext_trgs)
				out_test += f"add_test(NAME {get_or(t, 'tname', t['name'])} COMMAND $<TARGET_FILE:{t['name']}>)\n"
			elif t['type'] == "command":
				out_test += f"add_test(NAME {t['name']} COMMAND {t['command']})\n"
		out_test += f"{get_or(tests, 'cmake_post', '')}\n"
		with open(outdir + "/" + tests['dir'] + "/CMakeLists.txt", "w") as f:
			f.write(out_test)
	if 'cmake_post' in p:
		out += f"{p['cmake_post']}\n"
	with open(outdir + "/CMakeLists.txt", "w") as f:
		f.write(out)
	print("c++ build utils - cmake gen finished")

if __name__ == "__main__":
	with open(sys.argv[1], "rb") as f:
		p = json.load(f)
	generate(p, sys.argv[2])
