# Minimalistic MDI Communication Test

This test verifies that the engine is capable of basic communication with an external engine.


## Failure Resolution

If this test fails, ensure that you have followed each of the steps outlined below.


### Step 1: Make the MDI Library Available to the Engine

In order to pass this test, the engine must be capable of calling the functions that are defined by the MDI Library, such as `MDI_Init()`.
The process for enabling this is fundamentally different depending on whether the engine is written in a compiled or interpreted language.

##### Interpreted Languages

The only interpreted language currently supported by MDI is Python.
If your engine is written in Python, you should first install the MDI Library during the `build_image` step in `mdimechanic.yml`.
This can be done trivially using `pip` (*e.g.* `pip install pymdi`).
Your engine can then import the MDI Library where needed (*e.g.* `import mdi`).

##### Compiled Languages

In the case of codes written in compiled languages, the code must be compiled and linked against the MDI Library.
The MDI Library is released under a highly permissive BSD-3 License, and developers of MDI-enabled codes are encouraged to copy the MDI Library directly into distributions of their software.
If your code uses Git for version control, you can include the MDI Library in your distribution as either a subtree (recommended) or a submodule.
To incorporate a distribution of the MDI Library into your engine as a subtree, you can execute the following command in the top directory of the *engine's* Git repository (**not** in the top directory of this *engine report* repository):
``` bash
git subtree add --prefix=lib/mdi https://github.com/MolSSI-MDI/MDI_Library master --squash
```
The argument to the `--prefix` option indicates the location where the MDI Library source code will reside, and can be changed to better fit your engine's directory structure.

You must then modify your engine's build process to build the MDI Library and link against it.
The MDI Library builds using CMake.
If your engine also builds using CMake, you can simply include the MDI Library as a CMake subpackage.
Otherwise, you can add a few lines to your engine's existing build scripts to execute CMake and build the MDI Library.
The following lines illustrate how the MDI Library could be built, assuming that the source code for the MDI Library is located in `lib/mdi`:
``` bash
mkdir -p lib/mdi/build
cd lib/mdi/build
cmake -Dlibtype=STATIC -Dlanguage=C -DCMAKE_INSTALL_PREFIX=../install ..
make
make install
```
The following CMake configuration options are likely to be useful:
-**-Dlibtype**: Set this to `STATIC`.
-**-Dlanguage**: Set this to the language of the code you intend to link to the MDI library.  Valid options are `C`, `CXX` (for C++), and `Fortran`.
-**-DCMAKE_C_COMPILER**: Set this to the C compiler used to build your engine (if applicable).
-**-DCMAKE_Fortran_COMPILER**: Set this to the Fortran compiler used to build your engine (if applicable).
-**-DCMAKE_INSTALL_PREFIX**: If you intend to `make install` the MDI Library, set this to the destination directory for the installation.

Finally, during the link stage of your build process, you will need to ensure that your code is linked against the MDI Library.
In the case of the above example build process, the compiled static library file will be located at `${CMAKE_INSTALL_PREFIX}/lib/mdi`, and will typically be called `libmdi.a` on POSIX systems.



### Step 2: Initialize the MDI Library

Your code must initialize the MDI Library by calling the `MDI_Init()` function.
If your code uses the Message Passing Interface (MPI), you should call `MDI_Init()` after the call to `MPI_Init()`.
Aside from this restriction, `MDI_Init()` should be called as early in your code as possible.


### Step 3: Support Basic MDI Communication

