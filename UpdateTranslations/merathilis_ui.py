from update_locales import *

addon_folder = "H:/Blizzard/World of Warcraft/Development/Addons/"
addon_path = addon_folder + "ElvUI_MerathilisUI/ElvUI_MerathilisUI/Core/"

locale_files = get_exist_locale_list(addon_path + "Locales")
exist_locales = {}
for lang_code, path in locale_files.items():
    exist_locales[lang_code] = get_exist_locales(path)

add_other_locales(addon_folder+"ElvUI/ElvUI/Core/Locales", exist_locales)
add_other_locales(addon_folder+"ElvUI/ElvUI_OptionsUI/Locales", exist_locales)
add_other_locales(addon_folder+"ElvUI_WindTools/Locales", exist_locales)
add_other_locales(addon_folder+"WindDungeonHelper/Locales", exist_locales)


for lang_code, database in exist_locales.items():
    with open(addon_path+"Locales/{}.lua".format(lang_code), "r", encoding='utf8') as f:
        lines = f.readlines()

    pattern = re.compile(r"L\[\s*[\"\']([\s\S]*?)[\"\']\s*\] = true")

    newlines = []
    for line in lines:
        results = pattern.findall(line)
        if len(results) != 0:
            if exist_locales[lang_code].__contains__(results[0]):
                line = 'L["{}"] = "{}"\n'.format(results[0], database[results[0]])
        
        newlines.append(line)

    with open(addon_path+"Locales/{}.lua".format(lang_code), "w", encoding='utf8') as f:
        f.writelines(newlines)


