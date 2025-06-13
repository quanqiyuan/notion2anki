import re
import sys
import genanki
import os
import platform
import notion2anki


if platform.system() == 'Windows':
    anki_path = os.path.join(os.environ.get('APPDATA'), 'Anki2')
    notion_path = f'C:\\Users\\DELL\\Downloads\\aaa'  # 替换为你的md文件目录
else:
    anki_path = f'/Users/quanqiyuan/Library/Application Support/Anki2/'
    notion_path = f'/Users/quanqiyuan/Downloads/aaa'  # 替换为你的md文件目录
media_path = os.path.join(anki_path, 'QQ/collection.media')
card_dict = notion2anki.notion2anki(notion_path, media_path)


deck_dict = notion2anki.deck_dict
for deck_name, note_set in card_dict.items():
    if deck_name not in deck_dict.keys():
        deck_dict[deck_name] = max(deck_dict.values()) + 1

    tmp_deck = genanki.Deck(deck_dict[deck_name], deck_name)
    for aa in note_set:
        note = genanki.Note(
            model=notion2anki.template_notion2anki,
            fields=aa[0:3],
            tags = aa[3]
        )
        tmp_deck.add_note(note)
    anki_package = genanki.Package(tmp_deck)
    output_file = os.path.join('output', f'{deck_name}.apkg')
    print(f"Create {len(note_set)} Cards in {output_file}")
    anki_package.write_to_file(output_file)


del sys.modules['notion2anki']
with open('notion2anki.py', 'rt', encoding='utf-8') as file_id:
    content = file_id.read()
    content = re.sub(r'deck_dict.*?}', f'deck_dict = {str(deck_dict)}', content, flags=re.DOTALL)

with open('notion2anki.py', 'wt', encoding='utf-8') as file_id:
    file_id.write(content)
