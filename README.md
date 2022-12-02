# Distribution System Protection Simulator

### Requirements:
```
1) Python version: 3.10
2) Recommended IDE: Pycharm
3) Recommended environment: Conda 
```

### Installation Steps:
##### 1) Create conda environment using Anaconda command prompt: `conda create -n myenv python=3.10`
<br />

<p style="text-align: center;">OR</p>


##### 1) Open new project on PyCharm.
- Select new environment created using : **Conda**
- Select python version as : **3.10**


##### 2) Open terminal within the project environment and enter following commands.
```
git clone https://github.com/imsaumil/pyDSS_GUI_NCSU_ABB.git
cd .\pyDSS_GUI_NCSU_ABB
pip install -r .\requirements.txt
```

##### 3) Verify successful installation of required dependencies and launch application using following command.
```
python main.py
```

##### 4) Click on any of links to check the locally hosted GUI or open browser and add following address:
```
127.0.0.1:8070
```

### Voilà !

> User can now choose to play around with the developed GUI and interactively add protection element such as fuse with changeable rated fuse current and TCC curves, add DERs such as PV with different slider changeable penetration levels, introduce faults in the system to assess the relative fault contribution from each individual PVs and its effects on the  protection elements in the system.


### Sneak peek of developed GUI:
![Alt text](relative/path/to/img.jpg?raw=true "Title")
