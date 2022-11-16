# C++ build utils

Few utilities to help with making and building C/C++ projects.

- [C++ build utils](#c-build-utils)
	- [Installation / Usage](#installation--usage)
	- [cproxy](#cproxy)
	- [cmake_gen](#cmake_gen)
	- [TODO](#todo)

## Installation / Usage

The recommended way to install this is to add this directory to yout PATH :), then access all features through `cproxy.sh` or `cproxy.bat`.

## cproxy

It's a binding from one command to multiple tools. I tried to make it seem a bit like rust's cargo :) .

Since it's a python script, you need to run python and tell it the script path, which is annoying when you want to run it from some other directory, so I made batch and shell scripts which find the script from their directory and forward arguments to python - so you can just add this folder into your path and then use `cproxy.sh` or `cproxy.bat`.

cproxy command | description | effect
--- | --- | ---
`cproxy build` | builds the current cmake project, `--clean` can be used for clean build | runs `cmake --build build` (or `cmake --build build --clean-first` for clean build)
`cproxy clean` | cleans cmake files | runs `cmake --build build --target clean`
`cproxy cmgen` (or `cproxy gen`) | generates cmake files from `cmgen.json` (check out [cmake_gen](#cmake_gen)) and configures the project (options are equivalent to `cproxy configure`) | runs `cmake_gen` script and then configures the project in the same way as `cproxy configure`
`cproxy configure` (or `cproxy conf`) | configures current cmake project; options are `--debug`, `--release`, `--mgw` (uses mingw makefiles as generator), `--tests` (builds tests) | runs `cmake -S . -B build -DCMAKE_BUILD_TYPE={Debug/Release} -G"MinGW Makefiles" -DBUILD_TESTS=ON`; build type is determined by options (nothing by default), mingw makefiles generator is used only when `--mgw` is present, `-DBUILD_TESTS=ON` is used only when `--tests` is used
`cproxy doc` | runs doxygen | runs `doxygen doxygen.cfg`
`cproxy doc_g` | runs doxygen config generator | runs `doxygen -g doxygen.cfg`
`cproxy fetch <repo>` | fetches github repo using git | runs `git clone https://gitub.com/{repo}.git`
`cproxy help` | shows it's help | shows it's help
`cproxy install` | installs built project | runs `cmake --install build`
`cproxy install_git_cmake <repo> [options]` | fetches, configures (`-DCMAKE_BUILD_TYPE=Release` by default, `[options]` are redirectet to cmake in this step), builds and installs github repo | same as `git fetch <repo>`, `cd <repo.split('/')[1]>`, `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release [options]`, `cproxy build`, `cproxy install`
`cproxy new <name>` | generates new cmake project | copies files from `default_cmake_proj` into cwd, renames the folder to `<name>` and replaces all occurences of `%{PROJECT_NAME}` with `<name>` in all files
`cproxy new_cmg <name>` | same as `new`, but uses `default_cmgen_proj` instead | same as `new`, but uses `default_cmgen_proj` instead
`cproxy test [options]` | runs tests | same as `cd ./build`, `ctest [options]`, `cd ..`
`cproxy version` | shows version | shows version

## cmake_gen

A generator of cmake files from json, to make cmake more approachable to beginners.

Let's consider following example:

```json
{
	"project":"epic_project",
	"version":"0.69.420.0",
	"languages":"CXX",
	"standard":{
		"CXX":"20"
	},
	"output":"${CMAKE_SOURCE_DIR}/bin/",
	"targets":[
		{
			"name":"epic",
			"type":"executable",
			"source_dir":"src",
			"sources":[
				"main.cpp"
			],
			"depends":["httplib"],
			"features":["cxx_std_20"]
		}
	],
	"dependencies":[
		{
			"name":"httplib",
			"mode":"github",
			"repo":"yhirose/cpp-httplib",
			"tag":"v0.11.2"
		}
	],
	"global-cmgen-extensions":[ "debug-warn", "release-ipo" ],
	"tests":{
		"dir":"tests",
		"tests":[
			{
				"type":"executable",
				"name":"test-unit",
				"sources":[
					"test_unit1.cpp"
				],
				"include_dir":"${CMAKE_SOURCE_DIR}/src"
			}
		]
	}
}
```

The `project` field is the name of the project - it can't have whitespace in it unless it's surrounded by `"`s - which means `\"` in the json.
`version` field is version of the project - it can have up to 4 version levels - major, minor, patch and tweak.
`languages` is a space-separated list of languages used in the project in cmake's format - C CXX ....
`standard` is a "dictionary" with the number (in string!) of standard for each language (it's optional though).
`output` is the output directory - the path is relative to `build` subdirectory, which has also all cmake files - so I prefer something `bin` subdirectory in the project roor - the project root is stored in `${CMAKE_SOURCE_DIR}` (use it like this: `${CMAKE_SOURCE_DIR}/bin/`).
`targets` is a list of targets in the project - every target is "js object" with those fields:

field | effect | is optional (default)
--- | --- | ---
`name` | name of the target and the output file | no
`type` | what the target is - `executable`, `shared`, `module` or `static` | no
`source_dir` | directory with target's sources relative to project root (must be unique) | no
`sources` | list with source files for the | no
`depends` | list of targets the library depends on | yes
`includes` | list of directories from which files should be included | yes
`include_dir` | include directory - has the same effect as adding it to `includes` | yes
`links` | libraries against whose the target should be linked | yes
`link_dirs` | directories containing files for linking | yes
`features` | list of features to be passed into `target_compile_features` | yes
`cmake_pre` | cmake code added at the beginning of the cmakelists for the target | yes
`cmake_post` | cmake code added at the end of the cmakelists for the target | yes
`cmgen-extensions` | list of cmgen extensions used by this target | yes

## TODO

 - finish the documentation
 - add support for `configure_file` into cmgen
