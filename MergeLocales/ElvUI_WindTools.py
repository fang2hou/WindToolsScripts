from update_locales import *

addon_folder = "C:/Games/Blizzard/World of Warcraft/Development/Addons/"
addon_path = addon_folder + "ElvUI_WindTools/"

# 扫描全部代码，找出需要进行本地化的字符串
files = get_files(addon_path, ignore=["git", "Locales", "Libraries"])
keys = generate_keys(files)
keys.sort()

# 将已有的翻译进行存档
locale_files = get_exist_locale_list(addon_path + "Locales")
exist_locales = {}
for lang_code, path in locale_files.items():
  exist_locales[lang_code] = get_exist_locales(path)

# 导入 ElvUI 翻译及旧插件的翻译
add_other_locales(addon_folder+"ElvUI/ElvUI/Locales", exist_locales)
add_other_locales(addon_folder+"ElvUI/ElvUI_OptionsUI/Locales", exist_locales)
add_other_locales(addon_folder+"ElvUI_WindTools_BfA/Locales", exist_locales)
add_other_locales(addon_folder+"WindDungeonHelper/", exist_locales)
add_other_locales(addon_folder+"ElvUI_MerathilisUI/ElvUI_MerathilisUI/Locales/", exist_locales)
add_other_locales(addon_folder+"ElvUI_MerathilisUI/ElvUI_MerathilisUI/Locales/", exist_locales)
add_other_locales(addon_folder+"ElvUI_MerathilisUI/ElvUI_MerathilisUI/Locales/", exist_locales)
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
