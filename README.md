# Library

Library is a simple tool to structure papers and their connections.

It is developed while my master thesis preparing, and was born by the urge to structure the papers I am currently reading.
An example image can be seen below. 


The titles of the articles were blurred out after taking the image.
![Example image](images/example.png)

## Requirements
Parts of it are based on the gravphiz software. 
It can be found at: https://graphviz.org/

## Notes
I am developing and improving this tool currently.
Furthermore, I am actively working with it and therefore 
I am a little pragmatic corresponding to the look of the tool.
Maybe it will be improved in the future.

`os.startfile()` is used within this program (as far as I know Windows only). 
It therefore may not be compatible with operating systems besides windows.
I have added a few lines of code which should make it possible for linux too but have not tested it.


If you have any ideas how to improve or find bugs please tell me.

## Updates
- BUGFIX: Graph of unconnected is no longer zoomed out
- BUGFIX: Moving the cursor out of graph is no longer a problem when moving the graph
- Added config file which preserves the current viewbox in the svg for the next loading


## Usage
### Setup
#### Install requirements
Install graphviz (software) and the required packages:
- flask
- gravphiz (python package)
- PyPDF2

#### Create folders
1. Start 'create_folder.py'
2. Control if all three checkmarks are set in the REQUIREMENTS-frame (cf. Image bellow)
3. Select a path and create the folders

![Setup image](images/setup.png)

#### Getting to the GUI (graphical user interface)
1. Start the main.py
2. Open the website at the link which is presented by python

#### If automatic setup does not work:
Create a "path.py" and insert the following line:
```PATH = "<your path were to add the working data>"```.

Create an "Article" folder within `PATH`.
Therefore, you should have such a structure (example):
```
...
 |-Library
      |- Article <add papers into this folder>
      <an article.db will be automatically created here>
      <an .config file will be automatically created here>
```
In this example is `PATH = "...\Library"`


### Working 
Place papers in the Articles directory at your path.
You can open this folder when pressing the >Articles< button in the navbar. 
The system will check all articles every start or if you press the >Library< button on the web page.

Zoom with the mouse wheel in/out at the connected graph.
Move the connected graph by pressing your left mouse button and move it around.

To read a paper click at it while the >Read< section in the navbar is chosen.
Similar for all the other actions (I think I made most relevant things accessible via a click).

Click on a Connection to configure its properties.
This can either be done in the >Dependencies< section or when clicking at a connection in the connected graph.
If the connection does not have a comment yet, press at the arrowhead otherwise the comment will do.



I think the other possibilities explain themselves.
Maybe I will write something to this... some day (sorry :)).

### Tipps:
Place a run_library.py file at your Desktop.
Insert:
```
import os

PATH = "<path to main.py>"

os.startfile(PATH)
os.startfile("<url to the website>")
```

When you double-click it, the library is started, and your default browser will open the website.


## TODO:
- Improve paper update form
- add non weight dependency
- add summery option to paper
- make paper green with a checkbox to indicate it is finished