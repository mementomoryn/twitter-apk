from apkmirror import Version
from utils import patch_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    integrations = "bins/integrations.apk"
    patches = "bins/patches.jar"
    cli = "bins/cli.jar"

    patch_apk(
        cli,
        integrations,
        patches,
        apk,
        includes=["Bring back twitter"],
        excludes=["Dynamic color", "Enable PiP mode automatically"],
        riparch=["armeabi-v7a", "x86", "x86_64"],
        out=f"twitter-piko-v{latest_version.version}.apk",
    )
