"""
This script exports all flat surfaces to a folder as dxf files.
The script will look for objects of which the two largest faces are equally large, these are usually flat surfaces intended for laser cutting.
It will export the files with names on the format componentName_bodyName_Nx.dxf where N is the number of times that object is used in the design.
You will need to modify the output directory before using the script.
"""

import math
from pathlib import Path

import adsk.cam
import adsk.core
import adsk.fusion

from export_dxf_to_laser.debounced import debounced


def get_save_folder() -> Path | None:
    app = adsk.core.Application.get()
    ui = app.userInterface
    folder_dialog = ui.createFolderDialog()
    folder_dialog.title = "Select where to save .dxf files"
    dlg_res = folder_dialog.showDialog()
    if dlg_res == adsk.core.DialogResults.DialogOK:
        return Path(folder_dialog.folder)
    return None


def run(_):
    print("Running...")
    app = adsk.core.Application.get()

    idle_task = debounced(adsk.doEvents)

    save_folder = get_save_folder()
    if save_folder is None:
        print("Cancelling since no folder was selected")
        return

    des = adsk.fusion.Design.cast(app.activeProduct)
    for comp in des.allComponents:
        for body in comp.bRepBodies:
            body_path = f"{comp.name}/{body.name}"
            print(body_path)
            faceList = [
                x for x in body.faces if isinstance(x.geometry, adsk.core.Plane)
            ]
            faceList.sort(key=lambda face: face.area, reverse=True)
            if len(faceList) < 2:
                print(f"Weird body with less than 2 planar faces ({body_path})")
                continue

            a, b = faceList[0], faceList[1]
            if not math.isclose(a.area, b.area):
                print(
                    "Two largest faces don't seem to be of the same size."
                    " Probably not a part intended for laser cutting"
                    f" ({a.area} {b.area}) ({body_path})"
                )
                continue

            sketch = comp.sketches.add(a)
            occurances = len(des.rootComponent.allOccurrencesByComponent(comp))
            output_path = save_folder / f"{comp.name}_{body.name}_{occurances}.dxf"
            sketch.saveAsDXF(str(output_path))
            sketch.deleteMe()
            idle_task()

    print("Done.")
