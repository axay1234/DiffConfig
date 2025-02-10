import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import os
from datetime import datetime

def build_tree(config_lines):
    """Parses a Cisco-like configuration and constructs a tree (nested dictionary)
    where hierarchy is determined by indentation levels.
    Args: config_lines (list): List of configuration lines.
    dict: A nested dictionary representing the configuration structure. Creates a dictionary that 
    automatically initializes missing keys as empty dictionaries."""
    root = defaultdict(dict)  # Root dictionary to store config hierarchy
    """The real indentation starts from 0, but we need a reference point before that.
        It acts as a starting point so that the first line (with indentation 0) is properly placed under root.
        If we started with (0, root), the first real command might not be placed correctly in the hierarchy"""
    stack = [(-1, root)]  # Stack to track indentation levels and hierarchy

    for line in config_lines:
        raw_line = line.rstrip()  # Remove any trailing whitespace or newline characters.
        # Skip lines that are completely blank or that contain only a "!" (even if preceded by spaces).
        if not raw_line.strip() or raw_line.lstrip() == '!':
            continue  
        #indent = Total length - Trimmed length → Number of leading spaces.
        indent = len(line) - len(line.lstrip())
        cmd = raw_line.strip()  # Remove any leading/trailing spaces

        # Remove items from the stack until we find the correct parent level
        while stack and stack[-1][0] >= indent:
            stack.pop()
        cmd = raw_line.strip()  # Remove any leading/trailing whitespace to get the command.
        # Pop from the stack until we find a parent whose indentation is less than the current line.
        while stack and stack[-1][0] >= indent:
            stack.pop()
        # The current parent dictionary is the second item in the last tuple on the stack.
        parent = stack[-1][1]
        # Add the current command as a new key in the parent dictionary, initializing its value as a new dictionary.
        parent[cmd] = defaultdict(dict)
        # Push the current command with its indent level onto the stack.
        stack.append((indent, parent[cmd]))

    return root  # Return the full hierarchical configuration tree.

def diff_trees(old_tree, new_tree, indent=0):
    """Recursively compares two configuration trees and generates a diff output.
    If a key exists only in the old configuration, it and all its children are marked as removed.
    If it exists only in the new configuration, it and its children are marked as added.
    If a key exists in both, its children are compared recursively.
    indent (int): Current indentation level (for formatting output).
    list: A list of strings representing differences, formatted with indentation.
    """
    diff_lines = []  # List to store the resulting diff lines.

    # Iterate over every unique key (command) from both trees.
    for key in set(old_tree) | set(new_tree):  # The union of keys.
        # Case 1: Key exists in the old tree but not in the new tree.
        if key in old_tree and key not in new_tree:
            diff_lines.append("  " * indent + f"- {key}") # Mark as removed
            # Recursively mark all children as removed. where we compare an empty dictionary {} 
            # (since no children exist in the new tree for this key) with old_tree[key] (the children in the old tree).
            diff_lines.extend(diff_trees(old_tree[key], {}, indent + 1))
        # Case 2: Key exists in the new tree but not in the old tree.
        elif key in new_tree and key not in old_tree:
            diff_lines.append("  " * indent + f"+ {key}")
            # Also include any child commands of the newly added key. where we compare an empty dictionary {} 
            # (since no children exist in the old tree for this key) with new_tree[key] (the children in the new tree).
            diff_lines.extend(diff_trees({}, new_tree[key], indent + 1))
        # Case 3: Key exists in both trees.
        else:
            # Recursively compare the child dictionaries.
            child_diff = diff_trees(old_tree[key], new_tree[key], indent + 1)
            if child_diff:  # If there are differences in the subtree...
                diff_lines.append("  " * indent + key)  # Print the parent as a header.
                diff_lines.extend(child_diff)  # Then append the child differences.
    return diff_lines


def generate_diff(old_file, new_file, output_file):
    # Open and read both config files.
    with open(old_file, 'r') as f1, open(new_file, 'r') as f2:
        old_tree = build_tree(f1.readlines())
        new_tree = build_tree(f2.readlines())

    differences = diff_trees(old_tree, new_tree)

    # Write the differences to the output file.
    with open(output_file, 'w') as f:
        f.write("\n".join(differences) + "\n")
    
    return output_file

#############################################
# GUI FUNCTIONS
#############################################
def browse_old():
    """Opens a file dialog to select the old configuration file."""
    filename = filedialog.askopenfilename(
        title="Select Old Config File",
        filetypes=[("Config files", "*.txt *.cfg"), ("All Files", "*.*")]
    )
    if filename:
        old_file_entry.delete(0, tk.END)
        old_file_entry.insert(0, filename)

def browse_new():
    """Opens a file dialog to select the new configuration file."""
    filename = filedialog.askopenfilename(
        title="Select New Config File",
        filetypes=[("Config files", "*.txt *.cfg"), ("All Files", "*.*")]
    )
    if filename:
        new_file_entry.delete(0, tk.END)
        new_file_entry.insert(0, filename)

def run_diff():
    """Retrieves file paths from the GUI, runs the diff process, and notifies the user."""
    old_file = old_file_entry.get()
    new_file = new_file_entry.get()
    if not old_file or not new_file:
        messagebox.showerror("Error", "Please select both old and new configuration files.")
        return

    # Build the output file name using the current date and time.
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    # The output file will be saved in the same folder as the .py script.
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"diffConfig_{date_str}.txt")
    
    try:
        generate_diff(old_file, new_file, output_file)
        messagebox.showinfo("Success", f"Differences written to:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

#############################################
# GUI SETUP
#############################################
# Create the main window.
root_window = tk.Tk()
root_window.title("Config Diff Tool")

# Create and place the widgets.
# Old configuration file field.
old_label = tk.Label(root_window, text="Old Config File:")
old_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
old_file_entry = tk.Entry(root_window, width=50)
old_file_entry.grid(row=0, column=1, padx=5, pady=5)
browse_old_button = tk.Button(root_window, text="Browse", command=browse_old)
browse_old_button.grid(row=0, column=2, padx=5, pady=5)

# New configuration file field.
new_label = tk.Label(root_window, text="New Config File:")
new_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
new_file_entry = tk.Entry(root_window, width=50)
new_file_entry.grid(row=1, column=1, padx=5, pady=5)
browse_new_button = tk.Button(root_window, text="Browse", command=browse_new)
browse_new_button.grid(row=1, column=2, padx=5, pady=5)

# Button to start the diff process.
diff_button = tk.Button(root_window, text="Find Differences", command=run_diff)
diff_button.grid(row=2, column=1, padx=5, pady=20)

# Start the Tkinter event loop.
root_window.mainloop()

# # Example usage: Run the script with file paths
# if __name__ == "__generate_diff__":
#     generate_diff("old_config.txt", "new_config.txt", "config_diff.txt")