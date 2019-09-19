import uuid, subprocess, shlex, json, re  # nosec
import ipywidgets as widgets
from IPython import get_ipython  # pylint: disable=import-error
from IPython.display import HTML, clear_output, display  # pylint: disable=import-error
from google.colab import output, files  # pylint: disable=import-error
from glob import glob
from os import path as _p
from psutil import pids, Process
from sys import exit as exx, path as s_p

# Ultilities Methods ==========================================================


def createButton(name, *, func=None, style="", icon="check"):
    global widgets
    if not widgets in globals():
        import ipywidgets as widgets

    button = widgets.Button(
        description=name, button_style=style, icon=icon, disabled=not bool(func)
    )
    button.style.font_weight = "900"
    button.on_click(func)
    output = widgets.Output()
    display(button, output)


def generateRandomStr():
    return str(uuid.uuid4()).split("-")[0]


def checkAvailable(path_="", userPath=False):

    if path_ == "":
        return False
    else:
        return (
            _p.exists(path_)
            if not userPath
            else _p.exists(f"/usr/local/sessionSettings/{path_}")
        )


def findProcess(process, command="", isPid=False):
    if isinstance(process, int):
        if process in pids():
            return True
    else:
        for pid in pids():
            try:
                p = Process(pid)
                if process in p.name():
                    for arg in p.cmdline():
                        if command in str(arg):
                            return True if not isPid else str(pid)
                        else:
                            pass
                else:
                    pass
            except:  # nosec
                continue


def runSh(args, *, output=False, shell=False):
    if not shell:
        if output:
            proc = subprocess.Popen(  # nosec
                shlex.split(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            while True:
                output = proc.stdout.readline()
                if output == b"" and proc.poll() is not None:
                    return
                if output:
                    print(output.decode("utf-8").strip())
        return subprocess.run(shlex.split(args)).returncode  # nosec
    else:
        if output:
            return (
                subprocess.run(
                    args,
                    shell=True,  # nosec
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                .stdout.decode("utf-8")
                .strip()
            )
        return subprocess.run(args, shell=True).returncode  # nosec


def accessSettingFile(file="", setting={}):
    if not isinstance(setting, dict):
        print("Only accept Dictionary object.")
        exx()
    fullPath = f"/usr/local/sessionSettings/{file}"
    try:
        if not len(setting):
            if not checkAvailable(fullPath):
                print(f"File unavailable: {fullPath}.")
                exx()
            with open(fullPath) as jsonObj:
                return json.load(jsonObj)
        else:
            with open(fullPath, "w+") as outfile:
                json.dump(setting, outfile)
    except:
        print(f"Error accessing the file: {fullPath}.")


# Prepare prerequisites =======================================================


def installQBittorrent():
    if checkAvailable("/usr/bin/qbittorrent-nox"):
        return
    else:
        try:
            runSh("add-apt-repository ppa:qbittorrent-team/qbittorrent-stable -y")
            runSh("apt install qbittorrent-nox -qq -y")
        except:
            print("Error installing qBittorrent.")
            exx()


def installNgrok():
    if checkAvailable("/usr/local/bin/ngrok"):
        return
    else:
        runSh(
            "wget -qq -c -nc https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
        )
        runSh("unzip -qq -n ngrok-stable-linux-amd64.zip")
        runSh("mv ngrok /usr/local/bin/ngrok")
        runSh("rm -f /content/ngrok-stable-linux-amd64.zip")


def installAutoSSH():
    if checkAvailable("/usr/bin/autossh"):
        return
    else:
        runSh("apt install autossh -qq -y")


def installJDownloader():
    if checkAvailable("/root/.JDownloader/JDownloader.jar"):
        return
    else:
        runSh("mkdir -p -m 666 /root/.JDownloader/libs")
        runSh("apt install openjdk-8-jre-headless -qq -y")
        runSh(
            "wget -q http://installer.jdownloader.org/JDownloader.jar -O /root/.JDownloader/JDownloader.jar"
        )
        runSh("java -jar /root/.JDownloader/JDownloader.jar -norestart -h")
        runSh(
            "wget -q https://geart891.github.io/RLabClone/res/jdownloader/sevenzipjbinding1509.jar -O /root/.JDownloader/libs/sevenzipjbinding1509.jar"
        )
        runSh(
            "wget -q https://geart891.github.io/RLabClone/res/jdownloader/sevenzipjbinding1509Linux.jar -O /root/.JDownloader/libs/sevenzipjbinding1509Linux.jar"
        )


def addUtils():
    if checkAvailable("/content/sample_data"):
        runSh("rm -rf /content/sample_data")
    if not checkAvailable("/usr/local/sessionSettings"):
        runSh("mkdir -p -m 666 /usr/local/sessionSettings")
    if not checkAvailable("/root/.ipython/rlab_utils"):
        runSh(
            "wget -qq https://geart891.github.io/RLabClone/res/rlab_utils.py \
                -O /root/.ipython/rlab_utils.py"
        )
    if not checkAvailable("checkAptUpdate.txt", True):
        runSh("apt update -qq -y")
        runSh("apt-get install -y iputils-ping")
        data = {"apt": "updated", "ping": "installed"}
        accessSettingFile("checkAptUpdate.txt", data)

    if not checkAvailable("/usr/bin/rclone"):
        try:
            runSh(
                "curl -s https://rclone.org/install.sh | sudo bash -s beta",
                shell=True,  # nosec
            )
        except:
            print("Error installing rClone.")


def checkServer(hostname):
    return True if runSh(f"ping -c 1 {hostname}", shell=True) == 0 else False  # nosec


def configTimezone(auto=True):
    if checkAvailable("timezone.txt", True):
        return
    if not auto:
        runSh("sudo dpkg-reconfigure tzdata")
    else:
        runSh("sudo ln -fs /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime")
        runSh("sudo dpkg-reconfigure -f noninteractive tzdata")
    data = {"timezone": "Asia/Ho_Chi_Minh"}
    accessSettingFile("timezone.txt", data)


def uploadRcloneConfig(localUpload=False):
    if not localUpload and checkAvailable("rclone.conf", True):
        return
    elif not localUpload:
        runSh(
            "wget -qq https://geart891.github.io/RLabClone/res/rclonelab/rclone.conf \
                -O /usr/local/sessionSettings/rclone.conf"
        )
    else:
        try:
            print("Select config file (rclone.conf) from your computer.")
            uploadedFileName = files.upload().keys()
            if len(uploadedFileName) > 1:
                for fn in uploadedFileName:
                    runSh(f'rm -f "/content/{fn}"')
                return print("Please only upload a single config file.")
            elif len(uploadedFileName) == 0:
                return print("File upload cancelled.")
            else:
                for fn in uploadedFileName:
                    if checkAvailable(f"/content/{fn}"):
                        runSh(
                            f'mv -f "/content/{fn}" /usr/local/sessionSettings/rclone.conf'
                        )
                        runSh("chmod 666 /usr/local/sessionSettings/rclone.conf")
                        runSh('rm -f "/content/{fn}"')
                        print("Uploaded file successfully.")

        except:
            return print("Upload process Error.")


def uploadQBittorrentConfig():
    if checkAvailable("updatedQBSettings.txt", True):
        return

    runSh(
        "mkdir -p -m 666 /content/qBittorrent /root/.qBittorrent_temp /root/.config/qBittorrent"
    )
    runSh(
        "wget -qq https://geart891.github.io/RLabClone/res/qbittorrent/qBittorrent.conf \
            -O /root/.config/qBittorrent/qBittorrent.conf"
    )
    data = {"uploaded": "True"}
    accessSettingFile("updatedQBSettings.txt", data)


def prepareSession():
    if checkAvailable("ready.txt", True):
        return
    else:
        try:
            addUtils()
            configTimezone()
            uploadRcloneConfig()
            uploadQBittorrentConfig()
            accessSettingFile("ready.txt", {"prepared": "True"})
        except:
            print("Error preparing Remote.")


# rClone ======================================================================

PATH_RClone_Config = "/usr/local/sessionSettings"
PATH_RClone_Log = "/usr/local/sessionSettings/rclone_log"


def displayOutput(operationName="", color="#ce2121"):
    if color == "success":
        hColor = "#28a745"
        displayTxt = f"👍 Operation {operationName} has been successfully completed."
    elif color == "danger":
        hColor = "#dc3545"
        displayTxt = f"❌ Operation {operationName} has been errored."
    elif color == "info":
        hColor = "#17a2b8"
        displayTxt = f"👋 Operation {operationName} has some info."
    elif color == "warning":
        hColor = "#ffc107"
        displayTxt = f"⚠ Operation {operationName} has been warning."
    else:
        hColor = "#ffc107"
        displayTxt = f"{operationName} works."
    display(
        HTML(
            f"""
            <center>
                <h2 style="font-family:monospace;color:{hColor};">
                    {displayTxt}
                </h2>
                <br>
            </center>
            """
        )
    )


# qBittorrent =================================================================
QB_Port = 10001

tokens = {
    "ddn": "6qGnEsrCL4GqZ7hMfqpyz_7ejAThUCjVnU9gD5pbP5u",
    "tdn": "1Q4i7F6isO7zZRrrjBKZzZhwsMu_74yJqoEs1HrJh1zYyxNo1",
    "mnc": "1QPZGQMEBBI1O3L8G1GtWUiphvF_2d3C6kux93P6p4Zy7SSib",
    "api001": "1Q3zMbZhIunjp92RvrZpnyuJxZL_3V3JUziX5Dp1sQbTMAPrr",
    "api002": "1Q45NXgsx6oyusN3GiNAYvkNJPS_AveYUDBcPHsvRvf21WZv",
    "api003": "1Q6smHt4Bzz9VEXTwj3a7p5Gdx2_5mp6ivT6N6nB3YmRHUEM3",
}


def displayUrl(data, buRemotem, reset):
    clear_output(wait=True)
    print(f'Web UI: {data["url"]} : {data["port"]}')
    if "surl" in data.keys():
        print(f'Web UI (S): {data["surl"]} : {data["port"]}')
    createButton("Start Backup Remote", func=buRemotem)
    if "token" in data.keys():
        createButton("Reset", func=reset)


# JDownloader =================================================================

Email = widgets.Text(placeholder="*Required", description="Email:")
Password = widgets.Text(placeholder="*Required", description="Password:")
Device = widgets.Text(placeholder="Optional", description="Name:")
SavePath = widgets.Dropdown(
    value="/content/Downloads",
    options=["/content", "/content/Downloads"],
    description="Save Path:",
)


def RefreshPath():
    if checkAvailable("/content/drive/"):
        if checkAvailable("/content/drive/Shared drives/"):
            SavePath.options = (
                ["/content", "/content/Downloads", "/content/drive/My Drive"]
                + glob("/content/drive/My Drive/*/")
                + glob("/content/drive/Shared drives/*/")
            )
        else:
            SavePath.options = [
                "/content",
                "/content/Downloads",
                "/content/drive/My Drive",
            ] + glob("/content/drive/My Drive/*/")
    else:
        SavePath.options = ["/content", "/content/Downloads"]


def jDLoginForm():
    clear_output(wait=True)
    Email.value = "daniel.dungngo@gmail.com"
    Password.value = "ZjPNiqjL4e6ckwM"
    Device.value = ""
    RefreshPath()
    display(
        HTML(
            """
            <h3 style="font-family:Trebuchet MS;color:#4f8bd6;">
                If you don't have an account yet, please register 
                    <a href="https://my.jdownloader.org/login.html#register" target="_blank">
                        here
                    </a>.
            </h3>"""
        ),
        HTML("<br>"),
        Email,
        Password,
        Device,
        SavePath,
    )
    createButton("Refresh", func=RefreshPath)
    createButton("Login", func=checkJDLogin, style="info")
    if checkAvailable(
        "/root/.JDownloader/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json"
    ):
        createButton("Cancel", func=displayJDControl, style="danger")


def jDRestartForm():
    clear_output(wait=True)
    createButton("Restart Confirm?")
    createButton("Confirm", func=jDStartService, style="danger")
    createButton("Cancel", func=displayJDControl, style="warning")


def jDExitForm():
    clear_output(wait=True)
    createButton("Exit Confirm?")
    createButton("Confirm", func=exitJDWeb, style="danger")
    createButton("Cancel", func=displayJDControl, style="warning")


def checkJDLogin():
    try:
        if not Email.value.strip():
            ERROR = "Email field is empty."
            THROW_ERROR
        if not "@" in Email.value and not "." in Email.value:
            ERROR = "Email is an incorrect format."
            THROW_ERROR
        if not Password.value.strip():
            ERROR = "Password field is empty."
            THROW_ERROR
        if not bool(re.match("^[a-zA-Z0-9]+$", Device.value)) and Device.value.strip():
            ERROR = "Only alphanumeric are allowed for the device name."
            THROW_ERROR
        jDStartLogin()
    except:
        print(ERROR)


def jDStartService():
    runSh("pkill -9 -e -f java")
    runSh(
        "java -jar /root/.JDownloader/JDownloader.jar -norestart -noerr -r &",
        shell=True,  # nosec
    )
    displayJDControl()


def jDStartLogin():
    clear_output(wait=True)
    if SavePath.value == "/content":
        savePath = {"defaultdownloadfolder": "/content/Downloads"}
    elif SavePath.value == "/content/Downloads":
        runSh("mkdir -p -m 666 /content/Downloads")
        savePath = {"defaultdownloadfolder": "/content/Downloads"}
    else:
        savePath = {"defaultdownloadfolder": SavePath.value}

    runSh(
        f"echo '{savePath}' > /root/.JDownloader/cfg/org.jdownloader.settings.GeneralSettings.json",
        shell=True,  # nosec
    )
    if Device.value.strip() == "":
        Device.value = Email.value
    runSh("pkill -9 -e -f java")
    data = {
        "email": Email.value,
        "password": Password.value,
        "devicename": Device.value,
        "directconnectmode": "LAN",
    }
    runSh(
        f"echo '{data}' > /root/.JDownloader/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json",
        shell=True,  # nosec
    )
    jDStartService()


def exitJDWeb():
    runSh("pkill -9 -e -f java")
    clear_output(wait=True)
    createButton("Start", func=jDStartService, style="info")


def displayJDControl():
    clear_output(wait=True)
    createButton("Control Panel")
    display(
        HTML(
            """
            <h3 style="font-family:Trebuchet MS;color:#4f8bd6;">
                You can login to the WebUI by clicking 
                    <a href="https://my.jdownloader.org/" target="_blank">
                        here
                    </a>.
            </h3>
            """
        ),
        HTML(
            """
            <h4 style="font-family:Trebuchet MS;color:#4f8bd6;">
                If the server didn't showup in 30 sec. please re-login.
            </h4>
            """
        ),
    )
    createButton("Re-Login", func=jDLoginForm, style="info")
    createButton("Restart", func=jDRestartForm, style="warning")
    createButton("Exit", func=jDExitForm, style="danger")


def handleJDLogin(newAccount):
    installJDownloader()
    if newAccount:
        jDLoginForm()
    else:
        data = {
            "email": "daniel.dungngo@gmail.com",
            "password": "ZjPNiqjL4e6ckwM",
            "devicename": "daniel.dungngo@gmail.com",
            "directconnectmode": "LAN",
        }
        runSh(
            f"echo {data} > /root/.JDownloader/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json",
            shell=True,  # nosec
        )
        jDStartService()


# TO DO ===
# Update MAKE BUTTON FUNCTIONS
# FINISH MAKING ICONS
#

