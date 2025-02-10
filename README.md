# Config Diff Tool

The **Config Diff Tool** is a Python-based application designed to compare two configuration files (e.g., Cisco configuration files) and generate a detailed diff output. The tool uses a graphical user interface (GUI) built with Tkinter that allows users to browse for the configuration files and view the resulting diff.

## Features

- **Hierarchical Comparison:**  
  The tool builds a nested dictionary from the configuration files based on indentation levels. It then recursively compares these trees to highlight differences.
  
- **Detailed Diff Output:**  
  The diff output marks removed lines with a `-` and added lines with a `+`, including all child commands.
  
- **User-Friendly GUI:**  
  A simple Tkinter-based interface provides file browse dialogs for selecting the old and new configuration files.
  
- **Automatic Output File Naming:**  
  The diff result is saved as a text file with a name that includes the current date (e.g., `diffConfig_20250208.txt`) in the same folder as the script.

## Prerequisites

- **Python Version:**  
  The application requires **Python 3.6** or later.  
  (Note: f-strings, which are used in the code, were introduced in Python 3.6.)

- **Tkinter:**  
  Tkinter is used for the GUI. It is included by default with most Python installations. If you encounter issues, check your Python installation or refer to your operating system’s instructions for installing Tkinter.

## Installation

1. **Clone or Download the Repository:**  
   Download or clone the repository to your local machine.
   
   ```bash
   git clone https://github.com/axay1234/DiffConfig.git
