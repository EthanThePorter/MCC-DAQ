File can be launched using the .bat file in the project directory. It runs the following commands:

    @echo off
    cd "C:\Users\labuser\PycharmProjects\pythonProject"
    start "" "C:\ProgramData\Anaconda3\envs\pythonProject\pythonw.exe" "C:\Users\labuser\PycharmProjects\pythonProject\controller.pyw"

Which follows the syntax:

    @echo off
    cd "Path of project Folder"
    start "" "Path of Interpreter" "Path of .pyw file to be executed"

It is recommended to create a shortcut of the .bat file after the paths have been added.

In addition, ensure that the python file you are running has extension .pyw and that you use a pythonw.exe as seen in the first example.