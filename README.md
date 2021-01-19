# Corona_defense

This package provides an implementation of defense arcade game with pygame and python. 
The story of the game is defending corona virus pendamic of 2020 in Korea. 

## Overview

This project is based on the final project of Digital Computer Concept and Practice course of Seoul National University CSE.

The tree structure of this project is given as follows:

``` Unicode
Speech_Analysis
  ├── data
  │    └── audioclips.wav 
  ├── Transcripts
  │    └── transcript.txt  
  ├── Timelines
  │    └── timeline.csv 
  ├── Beep_Recognition.ipynb
  ├── SpeechRecognitionProject.ipynb
  └── run_glue_benchmark.py: comprehensive prediction file for teacher and student models
```

#### Data description
- audio clips

* Note that: 
    * You can use your own audio clips.
    * Sample audio clips are not provided because of copyright issue.
   
#### Output
* The transcripts will be saved in `Transcripts/{transripts.txt}` after the audio clips are transcribed.
* The timelines will be saved in `Timeline/{timeline.csv}` after the audio clips are analyzed.

## Install

#### Environment 
* Python 3.8
* pygame

## How to Run

### Clone the repository

```
git clone https://github.com/bjpark0805/Speech_Analysis.git
cd Speech_Analysis
python game.py
```

## Contact

- Bumjoon Park (qkrskaqja@snu.ac.kr)
