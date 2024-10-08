from apkmirror import Version
from utils import move_merged_apk, rename_apk patch_revanced_apk, patch_xposed_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    integrations = "bins/integrations.apk"
    patches = "bins/patches.jar"
    cli = "bins/cli.jar"
    xposed = "bins/xposed.apk"
    lspatch = "bins/lspatch.jar"
    apkrenamer = "bins/apkrenamer/renamer.jar"
    output_list = []

    patch_revanced_apk(
        cli,
        integrations,
        patches,
        apk,
        includes=["Bring back twitter"],
        excludes=[],
        riparch=["armeabi-v7a", "x86", "x86_64"],
        out=f"twitter-piko-v{latest_version.version}.apk",
        files=output_list
    )

    patch_revanced_apk(
        cli,
        integrations,
        patches,
        apk,
        includes=["Bring back twitter"],
        exclusive=True,
        riparch=["armeabi-v7a", "x86", "x86_64"],
        out="bring-back-twitter.apk"
    )

    patch_xposed_apk(
        lspatch,
        xposed,
        apk="bring-back-twitter.apk",
        out_dir="twitter-hachidori",
        out=f"twitter-hachidori-v{latest_version.version}.apk",
        files=output_list
    )

    move_merged_apk(
        apk,
        out=f"twitter-merged-v{latest_version.version}.apk",
        files=output_list
    )
    
    return output_list
