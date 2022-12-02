# Distribution System Protection Simulator

### Key objective:
The Distribution System Protection Simulator (DSPS) was originally developed as a capstone project for fulfilment of MS-EPSE requirements for core course ECE584: Electric Power Engineering Practicum II at NC State University, Raleigh with association and guidance from ABB US Research Centre. The objective of this project was to develop a standalone program that can model a standard distribution system such as IEEE 123 bus system and which can provide the users with the flexibility to interactively change the penetration levels for DERs such as PVs and show its effect on the protection elements present in the system. The vision for the current initiative is to provide a solid foundation and accelerate such studies in industry and academia. The current framework is made extensible following standard software engineering practices to make future updates to the current code base possible with minimum effort.


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
