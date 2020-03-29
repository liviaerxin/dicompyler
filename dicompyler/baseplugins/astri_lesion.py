import logging

logger = logging.getLogger("dicompyler.plugins.astri_leision")

from dicompyler import guiutil, util
from pubsub import pub
from typing import List
import json
import numpy as np
import os
import pydicom
import threading
import time
import wx
import subprocess
from typing import List
from pathlib import Path
import re


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props["name"] = "Lesion Analysis"
    props["description"] = "Lesion Analysis"
    props["author"] = "ASTRI"
    props["version"] = 0.1
    props["plugin_type"] = "main"
    props["plugin_version"] = 1
    props["min_dicom"] = ["images"]
    props["recommended_dicom"] = []

    return props


def pluginLoader(parent):
    """Function to load the plugin."""
    print("Lesion Analysis Plugin Loaded")
    panelTest = pluginTest(parent)
    return panelTest


def execute(cmd: List[str], cwd=None):
    """Constantly print Subprocess output while process is running

    Arguments:
        cmd {List[str]} -- [description]

    Keyword Arguments:
        cwd {[type]} -- [description] (default: {None})

    Raises:
        subprocess.CalledProcessError: [description]

    Yields:
        [type] -- [description]
    """
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, cwd=cwd
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


class pluginTest(wx.Panel):
    """Test plugin to demonstrate dicompyler plugin system."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # Initialize variables

        # Initialize the panel controls
        # self.patname = wx.StaticText(self, -1, "N/A", style=wx.ALIGN_CENTRE)
        self.patname = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        # Set up sizer for control placement
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.patname, 1, flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTRE, border=4)
        self.SetSizer(sizer)
        self.Layout()

        # Set up pubsub
        pub.subscribe(self.OnUpdatePatient, "patient.updated.raw_data")
        # pub.subscribe(self.OnUpdatePatient, "patient.updated.parsed_data")

    def OnUpdatePatient(self, msg):
        """Update and load the patient data."""
        # self.patname.AppendText(str(msg.keys()) + "\n")
        files: List[str] = []
        if "images" in msg:
            # raw_data
            images = msg["images"]
            for image in images:
                if isinstance(image, pydicom.dataset.FileDataset):
                    files.append(image.filename)
                else:
                    print(f"unable to process the image: {type(image)}")

            series_uid = image.SeriesInstanceUID

        self.RunAnalysis(files, series_uid)

        pub.unsubscribe(self.OnUpdatePatient, "patient.updated.raw_data")

    def RunAnalysis(self, files: List[str], series_uid: str = None):
        """Analyze the lesion with given DICOM files

        Arguments:
            files {List[str]} -- a list of DICOM files, each value is expected to be the filepath
        """

        # Initialize the progress dialog
        dlgProgress = guiutil.get_progress_dialog(
            wx.GetApp().GetTopWindow(), "Analyzing Lesion..."
        )
        # Set up the queue so that the thread knows which item was added
        # self.queue = queue.Queue()
        # Initialize and start the background analyzing thread
        self.t = threading.Thread(
            target=self.analyze_files_thread,
            args=(files, series_uid, dlgProgress.OnUpdateProgress),
        )
        self.t.start()
        # Show the progress dialog
        dlgProgress.ShowModal()
        dlgProgress.Destroy()

    def OnDestroy(self, evt):
        """Unbind to all events before the plugin is destroyed."""
        pub.unsubscribe(self.OnUpdatePatient, "patient.updated.raw_data")

    def mock_analyze_file(self, file: str):
        """mock analyze algorithm, process one file

        Arguments:
            file {str} -- [description]
        """
        time.sleep(0.001)

    def analyze_files_thread(self, files: List[str], series_uid, progressFunc):
        length = len(files)
        isMock = True

        # Analysis Start
        wx.CallAfter(progressFunc, 0, 100, "Analyzing Lesion...")

        # Analysis Process

        # all folders immediately under `resources` folder
        all_dirs = next(os.walk(util.GetResourcePath(".")))[1]
        algo_dirs = []
        for dir in all_dirs:
            if dir.startswith("lung_ct_analysis_v"):
                algo_dirs.append(dir)

        # auto detect the new version
        algo_dirs.sort(reverse=True)
        algorithm_dir = (
            util.GetResourcePath(algo_dirs[0]) if len(algo_dirs) > 0 else None
        )

        if algorithm_dir:
            isMock = False

        # DEV: force mock
        # isMock = True

        if not isMock:
            # Real algorithm
            print(f"Use algorithm dir f{algorithm_dir} to analyze")

            input_file = "./demo/input.json"
            output_file = "/temp/output.json"
            mask_file = "/temp/mask.npy"

            # prepare a folder to persist these files, so there's no need to re-generate these files again when running the same series
            if series_uid is None:
                # TODO: extract series uid from file
                series_uid = "unknown"

            series_analysis_dir = os.path.abspath(util.GetDataPath(series_uid))
            input_file = os.path.join(series_analysis_dir, "input.json")
            output_file = os.path.join(series_analysis_dir, "output.json")
            mask_file = os.path.join(series_analysis_dir, "mask.npy")

            if os.path.isfile(output_file) and os.path.isfile(mask_file):
                # Use previously generated files
                print(
                    f"series[{series_uid}] has already generate output_file: {output_file} and mask_file: {mask_file}"
                )
            else:
                # Generate new files
                try:
                    Path(series_analysis_dir).mkdir(parents=True, exist_ok=True)
                    with open(input_file, "w", encoding="utf-8") as f:
                        json.dump(files, f, ensure_ascii=False, indent=4)

                    print(
                        f"series[{series_uid}] is generating output_file: {output_file} and mask_file: {mask_file}"
                    )

                    for line in execute(
                        [
                            "python3.7",
                            "release/process.cpython-37.pyc",
                            input_file,
                            "-o1",
                            output_file,
                            "-o2",
                            mask_file,
                        ],
                        cwd=algorithm_dir,
                    ):
                        # TODO: extract more progress data
                        # for line in execute(["ls", "-la"]):
                        print(line)
                        match_obj = re.match(r"^progress\s(\d+)", line, re.M | re.I)
                        if match_obj:
                            progress = min(100, max(0, int(match_obj.group(1))))
                            wx.CallAfter(
                                progressFunc, progress, 100, "Analyzing Lesion..."
                            )
                except Exception as e:
                    print(e)
                    print(f"failed to generate analysis result!")
                    return
        else:
            # Mock algorithm
            print(f"Use mock algorithm to analyze")
            for i, file in enumerate(files):
                wx.CallAfter(progressFunc, int(i / length), 100, "Analyzing Lesion...")
                self.mock_analyze_file(file)

        # Analysis End
        wx.CallAfter(progressFunc, 100, 100, "Done")

        if isMock:
            # Mock analysis result
            print(f"Use mock result")
            result = None
            with open(util.GetResourcePath("PA373_ST1_SE2.json")) as f:
                result = json.load(f)
                pub.sendMessage("lesion.loaded.analysis", msg={"analysis": result})

            # Mock lesion mask
            if length == 307:
                maskpath = util.GetResourcePath("PA373_ST1_SE2_mask.npy")
            elif length == 59:
                maskpath = util.GetResourcePath("TCGA-17-Z019.npy")
            if os.path.isfile(maskpath):
                mask: np.ndarray = np.load(maskpath)
                print(f"Loaded mask[{maskpath}]: {mask.shape}")
                # mask.shape: (Z, X, Y)
                pub.sendMessage("lesion.loaded.mask", msg={"mask": mask})
        else:
            # Real result
            print(
                f"Use real result output_file: {output_file} and mask_file: {mask_file}"
            )

            # analysis result
            with open(output_file) as f:
                result = json.load(f)
                pub.sendMessage("lesion.loaded.analysis", msg={"analysis": result})

            # lesion mask
            mask: np.ndarray = np.load(mask_file)
            pub.sendMessage("lesion.loaded.mask", msg={"mask": mask})
