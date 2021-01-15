# Validate Engine Test

This test verifies that the engine is capable of basic communication with an external engine.



### Step 1: Prepare basic requirements

In order to simplify the process of implementing, testing, and analyzing the capabilities of an MDI engine in a portable environment, this tutorial makes use of several tools.
These tools include Git, GitHub, MDI Mechanic, and Docker.
Please install each of these tools now:
- If you don't already have a GitHub account, create one now.
- If you have never used Git, you may wish to work through [a quick tutorial on Git](https://education.molssi.org/python_scripting_cms/09-version-control/index.html), first.
- Install MDI Mechanic.  This can be done using pip, (*i.e.* `pip install mdimechanic`).
- Install Docker and launch Docker Desktop, if applicable.  You don't need to create a DockerHub account.  You also don't need to know much about using Docker, as MDI Mechanic will handle those details for you.
Note that although the above are requirements of this tutorial, none of them are required of end-users running your code.



### Step 2: Initialize an MDI Report repository

In this step of the tutorial, we will create a new GitHub repository to assist in the process of implementing, testing, and maintaining MDI support in your code.
This new repository will be separate and independent from any repositories already associated with your code, and will henceforth be referred to as your **MDI-report repository**.

Create your MDI-report repository by making a new repository on GitHub.
This repository does **not** need to include the source code of your engine, so you can make this repository publically accessible even if your source code is maintained privately.
Don't initialize the repository with a `README` file or a `.gitignore` file.
You can select whatever license you prefer; since this repository is separate from the repository that holds your engine's source code, it does not need to be the same license governing your engine's code.

Clone the newly created repository onto your local machine:
```Bash
git clone git@github.com:<organization>/<repo_name>.git
cd <repo_name>
```

Now use MDI Mechanic to create the initial structure for this report repository:
```Bash
cd <repo_name>
mdimechanic startproject --enginereport
```
This will add several new files to your MDI-report repository, including one called `mdimechanic.yml`.



### Step 3: Configure the MDI Mechanic YAML file

The `mdimechanic.yml` file created in the previous step is used by MDI Mechanic to build your engine and to test and analyze its functionality as an MDI engine.
If you have used continuous integration (CI) testing services in the past, you will likely recognize many similarities between `mdimechanic.yml` and the YAML files that are often used by those services.
Open MDI Mechanic in your favorite text editor, and you will see that some fields are already filled out.

This tutorial will go over each field in `mdimechanic.yml` in detail, but the following is a quick summary:
- **code_name:** The name of your code, which is used when printing out information.
- **image_name:** MDI Mechanic will create an Docker image, which will contain a highly portable environment that can be used to reproducibly build your engine.  This field sets the name of the engine MDI Mechanic will create.
- **build_image**: This provides a script that is used to build the Docker image that MDI Mechanic builds.  It corresponds to the steps required to prepare an environment with all of your engine's dependencies, and is comparable to a `before_install` step in some CI services.
- **build_engine**: This provides a script to build your engine.  It is executed within the context of the Docker image built by MDI Mechanic, and is comparable to an `install` step in some CI services.
- **validate_engine**: This provides a script to verify that your engine has been built successfully.  It is comparable to a `script` step in some CI services.
- **engine_tests**: This provides scripts used to test MDI functionality in your engine.

For now, just replace the value of `code_name` with the name of your engine, and set the value of `image_name` to something appropriate.
The naming convention for Docker images is `<organization_name>/<image_name>`, and we recommend that you follow this convention when setting `image_name`.
If in doubt, you can set `image_name` to `<engine_name>/mdi_report`.



### Step 4: Define your engine's build environment using MDI Mechanic

This tutorial uses MDI Mechanic, which in turn runs your code within the context of a Docker image.
In crude terms, you can think of an image as being a simulated version of another computer, which has a different environment from yours (*i.e.* different installed libraries and system settings), and might be running an entirely different Operating System.
The image created by MDI Mechanic is based on the Ubunto Linux distribution.
Starting from the basic Linux environment, MDI Mechanic installs some basic compilers (gcc, g++, and gfortran), an MPI library (MPICH), Python 3, and a handful of other dependencies (make and openssh).
To finish building the image, MDI Mechanic executes whatever script you've provided in the `build_image` section of `mdimechanic.yml`.

You should now fill out `build_image` with an appropriate script that contains any dependencies necessary to compile your engine (if your engine is written in a compiled language) or to run your engine (if your engine is written in an interpreted language).
To do this, imagine that someone handed you a Linux computer that is completely new and unused, except that the compilers and libraries mentioned in the preceeding paragraph have been installed on it.
What would you need to do in order to install all the dependencies for your code?
The answer to this question corresponds to the script you need to provide to `build_image`.



### Step 5: Build your engine using MDI Mechanic

After you've finished with the `build_image` script, it is time to write the `build_engine` script.
This script will be executed within the context of the image you described in the `build_image` script, so it will have access to any dependencies you installed in that script (and *only* those dependencies).
To write the `build_engine` script, ask yourself "What would someone need to type into their terminal to acquire a copy of my code's source and compile it?"; the answer to this question corresponds to the script you need to provide to `build_engine`.
Here are a few important details to keep in mind as you write the `build_engine` script:
- The initial working directory for the `build_engine` script is the top-level directory of your MDI-report repository.
- The `build_engine` script can access and manipulate any files within your MDI-report repository, including creating new files and subdirectories.  It does not have access to any other files or directories on you filesystem (for Docker afficianados: the MDI-report repository's top-level directory is mounted within the image to `/repo`).
- It is recommended that your `build_engine` script should download your engine repository's source code to a `source` subdirectory within your MDI-report repository.
- It is recommended that your `build_engine` script should build/install your engine repository's source code to a `build` subdirectory within your MDI-report repository.
- If your engine is **not** open-source, it may not be possible to simply download the source code via a command like `git clone`.  In this case, you should write the `build_engine` script with the assumption that your engine's source code has been manually copied by the end-user into a `source` subdirectory within the MDI-report top-level directory.  Uponing cloning the MDI-report repository, it will be the responsibility of the user to copy your engine's source code into the correct location, assuming they have access to it.  Note that you **absolutely should not** include any private information (*i.e.* software keys, private ssh keys, private source code, *etc.*) in `mdimechanic.yml` or any other file that is commited to your MDI-report repository.  The `build` and `source` directories are included in the `.gitignore` file of the MDI-report; this prevents source code that is temporarily stored in those locations from being accidentally committed, unless `.gitignore` is overridden. Override `.gitignore` at your peril, and always be aware of anything you are committing to the repository.

At this point, you can execute `mdimechanic build` in the top-level directory of your MDI-report repository.
If this command executes successfully, great!
If not, work to correct any problems with the build process before continuing to the next step.


### Step 6: Validate the engine build

At this point, modify the `validate_engine` field in `mdimechanic.yml` so that it performs a simple test to confirm that the engine was actually built.
The script should return a non-zero exit code upon failure.
If your code is written in a compiled language, this can be as simple as a check to confirm the executable file exists:
```YAML
  validate_engine:
    - ENGINE_EXECUTABLE_PATH="build/<engine_exectuable_name>"
    - |
      if test -f "$ENGINE_EXECUTABLE_PATH"; then
	echo "$ENGINE_EXECUTABLE_PATH exists"
      else
        echo "Could not find engine executable: $ENGINE_EXECUTABLE_PATH"
        exit 1
      fi
```
If your code is written in Python, you might instead confim that your code can be imported (*i.e.* `python -c "import <engine_name>"`).

After providing a `validate_engine` script, run `mdimechanic report` in the top-level directory of your MPI-report repository.
This will perform a series of tests to confirm whether your engine supports MDI correctly.
The first of these tests simply runs the `validate_engine` script.
Since we haven't even started implementing MDI functionality in your engine yet, it is expected that MDI Mechanic will report errors shortly after starting.
After `mdimechanic report` stops (most likely throwing an error), you should find that there is a new `README.md` file in your MDI-report repository.
This file contains the full report from MDI Mechanic.
To properly view the file, you can either commit the file and push it to GitHub, where it can be viewed at your MDI-report repository's GitHub page, or you can install an offline markdown viewer (such as `grip`) to view it.
There isn't much to see now, but hopefully you can see that there is a green `working` badge next to the step labeled "The engine builds successfully".
If not, review the error messages from `mdimechanic report` to try to work out what when wrong, before moving on to the next step.


### Step 7: Provide an example input

When you run `mdimechanic report`, MDI Mechanic tries to run a series of tests to determine whether and to what extent your code supports MDI.
To do this, MDI Mechanic attempts to launch your code, establish a connection between it and numerous test drivers, and then reports the results.
At this point in the tutorial, MDI Mechanic has no information about how to launch your code, so it can't run these tests.

We will now supply MDI Mechanic with everything it needs to run a calculation with your code.
In `mdimechanic.yml` you will find an `engine_tests` field.
This field can contain a list of scripts, each of which is intended to launch a single calculation with your code.
For now, we only want to supply a single test script.
The relevant part of `mdimechanic.yml` reads:
```YAML
engine_tests:
  # Provide at least one example input that can be used to test your code's MDI functionality
  - script:
      - echo "Insert commands to run an example calculation here"
      - exit 1
```
Replace the script in the `script` field here so that, when executed, it will launch a calculation using your code.
This likely means that you will need to add one or more input files to your MDI-report repository, which we recommend placing in a `tests` subdirectory.
Your `mdimechanic.yml` is likely to end up looking something like this:
```YAML
engine_tests:
  - script:
      - cd tests/test1
      - ../../${ENGINE_EXECUTABLE_PATH} -in test.inp
```
