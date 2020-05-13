import os
import re
from pprint import pprint
from shutil import copyfile


def get_file_path(addon_path: str, ignore: [str] = ["git"]) -> str:
    g = os.walk(addon_path)
    files = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            need_pass = False
            file_path = os.path.join(path, file_name)
            for keyword in ignore:
                if keyword in file_path:
                    need_pass = True
                    break

            if not need_pass and ".lua" in file_path:
                files.append(file_path)

    return files


def generate_keys(files: [str]) -> [str]:
    dict_keys = []

    pattern = re.compile(r"L\[[\"\'](.+?)[\"\']\]")
    for file in files:
        for line in open(file, "r", encoding='utf8'):
            results = pattern.findall(line)
            for result in results:
                if not result in dict_keys:
                    dict_keys.append(result)

    return dict_keys


def get_exist_locale_list(locale_path: str) -> {str: str}:
    g = os.walk(locale_path)
    files = {}
    for path, dir_list, file_list in g:
        for file_name in file_list:
            need_pass = False
            file_path = os.path.join(path, file_name)
            if not need_pass and ".lua" in file_path:
                lang_code = file_name.replace(".lua", "")
                files[lang_code] = file_path

    return files


def get_exist_locales(file: str) -> {str: str}:
    locales = {}
    pattern = re.compile(r"L\[[\"\'](.+?)[\"\']\] = \"(.*)\"")
    for line in open(file, encoding='utf8'):
        results = pattern.findall(line)
        for result in results:
            key = result[0]
            value = result[1]
            locales[key] = value
    return locales


def update_locales(keys, old: {str: str}, del_no_use: bool = True) -> {str: str}:
    if del_no_use:
        new = {}
    else:
        new = old.copy()

    for key in keys:
        try:
            string = old[key]
            string = string.replace("，", ",").replace("。", ".")
            new[key] = string
        except KeyError:
            new[key] = ""

    return new


if __name__ == "__main__":
    addon_path = "F:\Blizzard\World of Warcraft\Development\Addons\ElvUI_WindUI\\"

    # 扫描全部代码，找出需要进行本地化的字符串
    files = get_file_path(addon_path, ignore=["git", "Locales", "Libraries"])
    keys = generate_keys(files)
    keys.sort()

    # 将已有的翻译进行存档
    locale_files = get_exist_locale_list(addon_path + "Locales")
    exist_locales = {}
    for lang_code, path in locale_files.items():
        exist_locales[lang_code] = get_exist_locales(path)

    # 根据最新的字符串列表进行整理，翻译
    new_locales = {}
    for lang_code in exist_locales:
        new_locales[lang_code] = update_locales(keys, exist_locales[lang_code])

    # 生成全新的字符串文件
    for lang_code, path in locale_files.items():
        #copyfile(path, path.replace(".lua", ".bak"))
        file = open(path, "w", encoding='utf8')
        file.write('-- 此本地化文件由项目内的自动脚本生成\n')
        file.write('local E = unpack(ElvUI)\n')
        file.write('local L = ElvUI[1].Libs.ACL:NewLocale("ElvUI", ')
        if lang_code == "enUS":
            file.write('"enUS", true, true)\n\n')
        else:
            file.write('"{}")\n\n'.format(lang_code))

        for key, value in new_locales[lang_code].items():
            if value != "":
                file.write('L["{}"] = "{}"\n'.format(key, value))
            else:
                file.write('L["{}"] = true\n'.format(key))

        file.close()

    # pprint(new_locales, width=1024)
