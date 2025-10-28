import os

def build_index(paths):
    index = []
    for path in paths:  
        expanded = os.path.expanduser(path)
        for root, dirs, files in os.walk(expanded):
            for f in files:
                full_path = os.path.join(root, f)
                index.append({
                    "name": f,         
                    "path": full_path  
                })
    return index
