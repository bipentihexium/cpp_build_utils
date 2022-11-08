# C++ build utils

Few utilities to help with making and building C/C++ projects.

- [C++ build utils](#c-build-utils)
	- [Installation / Usage](#installation--usage)
	- [cproxy](#cproxy)
	- [cmake_gen](#cmake_gen)

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
