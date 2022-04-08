File can be launched using the .bat file in the project directory. It runs the following commands:

    @echo off
    cd "%~dp0"
    start "" "C:\ProgramData\Anaconda3\envs\pythonProject\pythonw.exe" "%~dp0\controller.pyw"

Which follows the syntax:

    @echo off
    cd "%~dp0"
    start "" "Path of Interpreter" "%~dp0\python_file.pyw"

If using PyCharm or a similar IDE, just get the path of the project interpreter and use for the .bat

It is recommended to create a shortcut of the .bat file after the paths have been added.

"%~dp0" will use the directory that the .bat resides in.

In addition, ensure that the python file you are running has extension .pyw and that you use a pythonw.exe as seen in the first example.