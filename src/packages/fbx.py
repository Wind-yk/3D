import sys
import string
import os
import json
import math

# Project defined classes
from packages.mesh import Mesh
 
def fbx2json(input:str, output:str, force:bool=False):
    """
    Converts a FBX file to json, using external C++ package.
    """

    # Change working directory
    os.chdir("src/script")

    # If exit output.txt, we delete it
    if os.path.exists(output):
        if force:
            os.remove(output)
        else:
            raise FileExistsError(f"{output} already exists.")

    # Complete the command with input file name
    input = "readFbxInfo.exe " + input + " >> " + output

    # Execute the readFbxInfo.exe
    os.system(input)

def readFBX(fbx_path: str, json_path: str=None, overwrite: bool=False):
    """
    Return a list of Mesh from the FBX file.

    # Parameters:
      * `fbx_path` (str): path of the file.
      * `json_path` (str): output json file path. If None, then the name of FBX is used.
      * `overwrite` (bool): converts it to json even if the `json_path` file already exists.

    # Output:
        A list of Mesh that each of them represents a geometric body to display.
        The list can be empty.

    ⚠ In case that overwrite is set, then converts anyway.
    """
    # Check if the file exists, if it is already in json. If it is not,
    # then first use fbx2json to convert it to json and read it as so.

    # Create empty mesh list
    mesh_list = []

    # Convert fbx file to json
    fbx2json(fbx_path, json_path, overwrite)
    
    # Open the created json file for data
    with open("../"+json_path, 'r') as file:
        data = json.load(file)

    # For each "Geometry" create a Mesh with its respective "Model"
    counter = 0
    # Assign predetermined values for center, angle, scale
    center = [0, 0, 0]
    angle = [0, 0, 0]
    scale = []

    for i,v in enumerate(data['children'][8]['children']):
        if v['name']=="Geometry":
            vertices = v['children'][2]['properties'][0]['value']
            edges = v['children'][4]['properties'][0]['value']
            new_mesh = Mesh(vertices, edges, center, angle, scale)
            mesh_list.append(new_mesh)

        elif v['name']=="Model":
            
            for i2, v2 in enumerate(v['children'][1]['children']):
                if v2['properties'][0]['value'] == "Lcl Translation":
                    center = []
                    for idx in range(4, 7):
                        center.append(v2['properties'][idx]['value'])
                elif v2['properties'][0]['value'] == "Lcl Rotation":
                    angle = []
                    for idx in range(4, 7):
                        angle.append(math.radians(v2['properties'][idx]['value']))
                elif v2['properties'][0]['value'][0] == "Lcl Scaling":
                    for idx in range(4, 7):
                        scale.append(v2['properties'][idx]['value']/100)
            
            # assume there are getters and setters for vertices and edges
            mesh_list[counter] = Mesh(mesh_list[counter].vertices, mesh_list[counter].edges, center, angle, scale)
            center = [0, 0, 0]
            angle = [0, 0, 0]
            scale = []
            counter+=1

    return mesh_list

