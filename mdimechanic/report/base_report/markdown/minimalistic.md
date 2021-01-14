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
- **-Dlibtype**: Set this to `STATIC`.
- **-Dlanguage**: Set this to the language of the code you intend to link to the MDI library.  Valid options are `C`, `CXX` (for C++), and `Fortran`.
- **-DCMAKE_C_COMPILER**: Set this to the C compiler used to build your engine (if applicable).
- **-DCMAKE_Fortran_COMPILER**: Set this to the Fortran compiler used to build your engine (if applicable).
- **-DCMAKE_INSTALL_PREFIX**: If you intend to `make install` the MDI Library, set this to the destination directory for the installation.

Finally, during the link stage of your build process, you will need to ensure that your code is linked against the MDI Library.
In the case of the above example build process, the compiled static library file will be located at `${CMAKE_INSTALL_PREFIX}/lib/mdi`, and will typically be called `libmdi.a` on POSIX systems.

### Step 2: Support User Input of the MDI Options

Your code should allow users to set certain MDI parameters at runtime.
Typically, end-users should be able to set these parameters through the use of a `-mdi` command-line option when your engine is launched.
In this case, the user should be able to launch your code by doing something along the lines of:
```Bash
engine_exectable -mdi "-name engine -role ENGINE -method TCP -hostname localhost -port 8021"
```
The details of how you read this command-line option are beyond the scope of this tutorial, but should conform to whatever existing method you use to read command-line options.
The argument to the `-mdi` command-line option should be represented as a `char*` in C++, a `CHARACTER` array in Fortran, and a `String` in Python.
Subsequent steps in this tutorial will assume that you have named the corresponding variable `mdi_options`.

We understand that some codes prefer to eschew command-line options where possible.
If it is preferable not to introduce support for a `-mdi` command-line option, ensure that there is some other mechanism for the user to provide the MDI parameters at runtime.

### Step 3: Initialize the MDI Library

Your code must initialize the MDI Library by calling the `MDI_Init()` function.
This is a straightforward process, but there are a few a couple of important details to keep in mind if you are using both MDI and the Message Passing Interface (MPI):
- If your code uses MPI, you should call `MDI_Init()` after the call to `MPI_Init()` (or `MPI_Init_thread()`, if applicable).  Aside from the restriction, `MDI_Init()` should be called as early in your code as possible.  It is a best practice to call `MDI_Init()` immediately after calling `MPI_Init()`.  Calling MPI functions (other than `MPI_Init()` or `MPI_Init_thread()`) before calling `MDI_Init()` will lead to bugs.
- One of the required arguments to the `MDI_Init()` function is an MPI intra-communicator.  Upon calling `MDI_Init()`, this intra-communicator must correspond to the intra-communicator that includes all global ranks (*e.g.*, `MPI_COMM_WORLD`).  The `MDI_Init()` function will then perform an `MPI_Comm_split()` operation to obtain an inter-communicator that includes only ranks associated with your engine.  As an engine developer, you should **never** perform MPI operations involving `MPI_COMM_WORLD`.  Instead, use the intra-communicator that is provided by the MDI Library whenever you would have otherwise used `MPI_COMM_WORLD`.  You should replace any existing references to `MPI_COMM_WORLD` in your code with a reference to the intra-communicator obtained from calling `MDI_Init()`.

The following code snippets provide a guide to correctly initializing MDI and MPI together in C++, Fortran, and Python.

##### C++

```C++
#include <mpi.h>
#include "mdi.h"

/* User-selected options for the MDI Library
   This should be obtained at runtime from a "-mdi" command-line option */
char *mdi_options;

/* MPI intra-communicator for all processes running this code
   It should be set to MPI_COMM_WORLD prior to the call to MDI_Init(), as shown below
   Afterwards, you should ALWAYS use this variable instead of MPI_COMM_WORLD */
MPI_Comm world_comm;

/* Pointer to world_comm */
MPI_Comm *world_comm_ptr = &world_comm;

/* MDI communicator used to communicate with the driver */
MDI_Comm mdi_comm = MDI_COMM_NULL;

/* Rank of this process in the MDI-created intra-communicator */
int myrank = 0;

/* Function to initialize both MPI and MDI */
initialize(char *mdi_options, MPI_Comm *world_comm_ptr) {

  /* If using MPI, it should be initialized before MDI */
  MPI_Init();

  /* Set the value of world_comm
     Note: if you are not using MPI, set world_comm to MDI_COMM_NULL instead */
  *world_comm_ptr = MPI_COMM_WORLD;

  /* MDI should be initialized immediately after MPI */
  MDI_Init(mdi_options, world_comm_ptr);
  /* Following this point, world_comm should be used whenever you would otherwise have used MPI_COMM_WORLD */

  /* Get the rank of this process, within the MDI-created intra-communicator */
  MPI_Comm_rank(world_comm, my_rank);

  /* Accept a connection from an external driver */
  if ( my_rank == 0 ) {
    MDI_Accept_Communicator(&mdi_comm);
  }
}
```

After implementing the call to `MDI_Init()`, you should recompile the code to confirm that your executable is linked to the MPI Library.

##### Fortran

```Fortran
SUBROUTINE initialize ( mdi_options, world_comm, my_rank, mdi_comm )
    USE mpi,               ONLY : MPI_COMM_WORLD
    USE mdi,               ONLY : MDI_Init, MDI_COMM_NULL
    !
    ! User-selected options for the MDI Library
    ! This should be obtained at runtime from a "-mdi" command-line option
    !
    CHARACTER(len=1024), INTENT(IN), OPTIONAL :: mdi_options
    !
    ! MPI intra-communicator for all processes running this code
    ! It should be set to MPI_COMM_WORLD prior to the call to MDI_Init(), as shown below
    ! Afterwards, you should ALWAYS use this variable instead of MPI_COMM_WORLD
    !
    INTEGER, INTENT(INOUT) :: world_comm
    !
    ! Rank of this process within the MDI-created intra-communicator
    !
    INTEGER, INTENT(OUT) :: my_rank
    !
    ! MDI communicator, obtained from MDI_Accept_Communicator
    !
    INTEGER, INTENT(OUT) :: mdi_comm
    !
    ! Error flag used in MDI calls
    !
    INTEGER :: ierr
    !
    ! If using MPI, it should be initialized before MDI
    !
    CALL MPI_Init(ierr)
    !
    ! Set the value of world_comm
    ! Note: if you are not using MPI, set world_comm to MDI_COMM_NULL instead
    !
    world_comm = MPI_COMM_WORLD
    !
    ! MDI should be initialized immediately after MPI
    !
    IF ( PRESENT(mdi_options) ) THEN
        CALL MDI_Init(mdi_options, world_comm, ierr)
    END IF
    !
    ! Following this point, world_comm should be used whenever you would otherwise have used MPI_COMM_WORLD
    !
    !
    ! Get the rank of this process, within the MDI-created intra-communicator
    !
    CALL MPI_Comm_rank(world_comm, my_rank, ierr)
    !
    ! Accept a connection from an external driver
    !
    IF ( my_rank .eq. 0 ) THEN
        CALL MDI_Accept_Communicator( mdi_comm, ierr )
    END IF
END SUBROUTINE initialize
```

After implementing the call to `MDI_Init()`, you should recompile the code to confirm that your executable is linked to the MPI Library.

##### Python

```Python
# Import the MDI Library
import mdi

# Attempt to import mpi4py
try:
    from mpi4py import MPI
    use_mpi4py = True
except ImportError:
    use_mpi4py = False

# MPI intra-communicator for all processes running this code
# It should be set to MPI.COMM_WORLD prior to the call to MDI_Init(), as shown below
# Afterwards, you should ALWAYS use this variable instead of MPI.COMM_WORLD
if use_mpi4py:
    world_comm = MPI.COMM_WORLD
else:
    world_comm = None

# Get the command-line options for MDI
...

# Initialize MDI
mdi.MDI_Init(mdi_options, world_comm)

# Set world_comm to the correct intra-code MPI communicator
world_comm = MDI_Get_Intra_Code_MPI_Comm()
# Following this point, world_comm should be used whenever you would otherwise have used MPI.COMM_WORLD

# Get the MPI rank of this process
if world_comm is not None:
    my_rank = world_comm.Get_rank()
else:
    my_rank = 0

# Accept a connection from an external driver
if my_rank == 0:
    mdi_comm = MDI_Accept_Communicator()
```

### Step 4: Support Basic MDI Communication

In this step, we are going to introduce some basic code that will finally allow external drivers to connect to your code and ask it to do useful things for them.
First, identify a point in your code when it would be appropriate for the code to accept instructions (in the form of MDI commands) from an external driver.
The chosen point should occur after your code has completed basic initialization operations (reading input files, doing basic system setup, calling `MDI_Init()`, *etc.*).
It should also be practical to implement support for a reasonable number of MDI commands at whatever point you select.
The [MDI Standard](https://molssi-mdi.github.io/MDI_Library/html/mdi_standard.html) defines numerous commands that driver developers might want to send to your code.
You won't need to support all of the available commands, but it is advisable to support some of the more common commands, such as commands that request or change the nuclear coordinates (`<COORDS` and `>COORDS`, respectively), as well as commands that request the energy (`<ENERGY`) number of atoms (`<NATOMS`), or (`<FORCES`).
Try to select a point where it will be possible to fulfill some of these requests.
When in doubt, select a point that is reached early in your code's execution.
This tutorial will subsequently refer to the point you have selected as the **MDI node**.

At the MDI node, you will need to insert some code (probably in the form of a called function) that handles the process of establishing communication with the external driver, accepting MDI commands from the driver, and responding to the commands appropriately.
For the purpose of this tutorial, we will implement all of this functionality in a function called `run_mdi()`.
Examples of a minimalistic `run_mdi()` function are provided below, in C++, Fortran, and Python.
You can simply copy the function into your codebase and call `run_mdi()` at your MDI node.

##### C++

Call this function as `run_mdi("@DEFAULT", my_rank, world_comm, mdi_comm)`.

```C++
#include <mpi>
#include "mdi.h"

run_mdi(char *node_name, int my_rank, MPI_Comm world_comm, MDI_Comm mdi_comm)

  /* Exit flag for the main MDI loop */
  bool exit_flag = false;

  /* MDI command from the driver */
  command = new char[MDI_COMMAND_LENGTH];

  /* Main MDI loop */
  while (not exit_flag) {
    /* Receive a command from the driver */
    if ( my_rank == 0 ) {
      MDI_Recv_Command(command, mdi_comm);
    }
    MPI_Bcast(command, MDI_COMMAND_LENGTH, MPI_CHAR, 0, world_comm);

    /* Confirm that this command is actually supported at this node */
    int command_supported = 0;
    MDI_Check_Command_Exists(node_name, command, MDI_COMM_NULL, &command_supported);
    if ( command_supported != 1 ) {
      /* Note: Replace this with whatever error handling method your code uses */
      MPI_Abort(world_comm, 1);
    }

    /* Respond to the received command */
    if ( strcmp(command, "EXIT") == 0 ) {
      exit_flag = true;
    }
    else {
      /* The received command is not recognized by this engine, so exit
         Note: Replace this with whatever error handling method your code uses */
      MPI_Abort(world_comm, 1);
    }

  // Free any memory allocations
  delete [] command;
}
```

##### Fortran

Call this function as `CALL run_mdi("@DEFAULT", my_rank, world_comm, mdi_comm)`.

```Fortran
SUBROUTINE run_mdi( node_name, my_rank, world_comm, mdi_comm )
    USE mdi,              ONLY : MDI_Send, MDI_Recv, MDI_Recv_Command, &
                                 MDI_Accept_Communicator, &
				 MDI_CHAR, MDI_DOUBLE, MDI_INT, &
				 MDI_COMMAND_LENGTH, MDI_NAME_LENGTH, &
				 MDI_COMM_NULL
    !
    ! MDI command from the driver
    !
    CHARACTER :: node_name(MDI_NAME_LENGTH)
    !
    ! Rank of this process in world_comm
    ! If you are not using MPI, you can set my_rank = 0
    !
    INTEGER, INTENT(IN) :: my_rank
    !
    ! MDI-created intra-communicator
    !
    INTEGER, INTENT(IN) :: world_comm
    !
    ! MDI communicator, obtained from MDI_Accept_Communicator
    !
    INTEGER, INTENT(IN) :: mdi_comm
    !
    ! MDI command from the driver
    !
    CHARACTER, ALLOCATABLE :: command(:)
    !
    ! Error flag for MDI functions
    !
    INTEGER :: ierr
    !
    ! Flag to indicate whether a received command is supported
    !
    INTEGER :: command_supported
    !
    ! Allocate the command array
    !
    ALLOCATE( command(MDI_COMMAND_LENGTH) )
    !
    ! Main MDI loop
    !
    mdi_loop: DO
        !
        ! Receive a command from the driver
        !
        IF ( my_rank .eq. 0 ) THEN
            CALL MDI_Recv_Command( command, mdi_comm, ierr )
            WRITE(*,*) "MDI Engine received a command: ",trim(command)
        END IF
        !
        ! Broadcast the command to all ranks
        ! Note: Remove this line if not using MPI
        !
        CALL MPI_Bcast( header, MDI_COMMAND_LENGTH, MPI_CHAR, 0, world_comm )
        !
        ! Confirm that this command is actually supported at this node
        !
        command_supported = 0;
        CALL MDI_Check_Command_Exists(node_name, command, MDI_COMM_NULL, command_supported, ierr);
        IF ( command_supported .ne. 1 ) THEN
            ! Note: Replace this with whatever error handling method your code uses
            CALL MPI_Abort(world_comm, 1);
        END IF
        !
        ! Respond to the received command
        !
        SELECT CASE ( trim( command ) )
	CASE( "EXIT" )
	    RETURN
        CASE DEFAULT
            !
            ! The received command is not recognized by this engine, so exit
            ! Note: Replace this with whatever error handling method your code uses
            !
            WRITE(*,*) "MDI Engine received unrecognized command: ",trim(command)
            CALL MPI_Abort(world_comm, 1);
        END SELECT
    END DO mdi_loop
END SUBROUTINE run_mdi
```

##### Python

```Python
import mdi

def run_mdi(node_name, my_rank, world_comm, mdi_comm):

    exit_flag = False

    # Main MDI loop
    while not exit_flag:
        # Receive a command from the driver
        if self.my_rank == 0:
            command = mdi.MDI_Recv_Command(self.comm)
        else:
            command = None

        # Broadcast the command to all ranks, if using MPI
        if world_comm is not None:
            command = world_comm.bcast(command, root=0)

        # Confirm that this command is actually supported at this node
        if not mdi.MDI_Check_Node_Exists(node_name, command):
            raise Exception('MDI Engine received unsupported command: ' + str(command))

        # Respond to the received command
        if command == "EXIT":
            exit_flag = True
        else:
            # The received command is not recognized by this engine, so exit
            # Note: Replace this with whatever error handling method your code uses
            raise Exception('MDI Engine received unrecognized command: ' + str(command))
```


### Step 5: Register the Node and Commands

MDI requires you to "register" a list of all nodes and commands your engine supports.
This allows you, as an engine developer, to inform any drivers of what your code can do.
MDI provides two functions that allow you to do this: `MDI_Register_Node()` and `MDI_Register_Command()`.
The engine we have developed thus far in the tutorial only supports a single node, and that node only supports a single command.
As a result, we need to call `MDI_Register_Node()` once to register the `@DEFAULT` node and call `MDI_Register_Command()` once to register the `EXIT` command.

Fortunately, this is a very simple process.
The only argument to the `MDI_Register_Node()` function is the name of the node, `@DEFAULT`.
The `MDI_Register_Command()` function accepts two arguments: the name of the node, and the name of the command that we are registering at that node, `EXIT`.
In time, you may add support for additional commands at the default node, making additional calls to `MDI_Register_Command()` for each newly supported command.
If you add additional nodes, each node will have its own list of registered commands, which may be different from the list of commands supported at the `@DEFAULT` node.

For now, place the following code immediately after your engine's call to `MDI_Init()`.
It is important that it be called prior to the call to `MDI_Accept_Communicator()`.

##### C++

```C++
  /* Register all supported commands and nodes */
  MDI_Register_Node("@DEFAULT");
  MDI_Register_Command("@DEFAULT", "EXIT");
```

##### Fortran

```Fortran
    ! Register all supported commands and nodes
    CALL MDI_Register_Node("@DEFAULT", ierr);
    CALL MDI_Register_Command("@DEFAULT", "EXIT", ierr);
```

##### Python

```Python
    # Register all supported commands and nodes
    mdi.MDI_Register_Node("@DEFAULT")
    mdi.MDI_Register_Command("@DEFAULT", "EXIT")
```

### Step 6: Add Support for Additional Commands

It may not look like much yet, but you have now established an basic MDI interface!
If you generate a new report by typing `mdimechanic report` at the command line, MDI Mechanic should confirm that your engine passes all of the "Basic Functionality Tests".
If your engine is still failing that test, you should return to the previous steps of this tutorial to determine what went wrong.

Assuming that your MDI interface is functioning as expected, you can now begin the process of implementing support for more commands.
Whenever you want to add support for a new command, you will need to do the following:
-# Add code to the "Main MDI loop" in `run_mdi()` that will respond appropriately to the new command.
-# Add a call to `MDI_Register_Command()` to register support for that command.

Examine the commands specified by the [MDI Standard](https://molssi-mdi.github.io/MDI_Library/html/mdi_standard.html), and implement support for the ones that seem relevant for your engine.
Each command in the MDI Standard describes exactly how the engine is expected to respond.
Often, the engine is expected to either send or receive information to/from the driver.
This is accomplished using the `MDI_Send()` and `MDI_Recv()` functions, respectively.

If you are using MPI, you should be aware that all MDI-based communication must take place through `rank 0`.
Only `rank 0` should call `MPI_Send()`, `MPI_Recv()`, and `MPI_Recv_Command()`.
Depending on how you have distributed data structures across ranks, you may need to do `MPI_Gather()` or similar operations to collect the data onto `rank 0` before calling `MDI_Send()`.
Likewise, you may need to do `MPI_Scatter()` or similar operations to correctly distribute data after calling `MDI_Recv()`.

### Step 7: Add Support for Additional Nodes

Whenever you add a new node, you must also add a call to `MDI_Register_Node()` to register support for that node.
Commands are registered separately for each node, so any commands that are supported at the new node must be registered for it.
For example, if you implement five nodes, and each of them supports the `EXIT` command, you will need to call the `MDI_Register_Command()` function five times, each time with a different node as the first argument and with `EXIT` as the second argument.
