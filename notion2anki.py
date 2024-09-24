import shutil
import genanki
import markdown
import re
import os
import pathlib
import urllib.parse
import platform
import notion_template


if platform.system() == 'Windows':
    anki_path = os.path.join(os.environ.get('APPDATA'), 'Anki2')
    media_path = os.path.join(anki_path, 'QQ/collection.media')
else:
    # 定义要处理的Markdown文件路径和图片文件目录
    pass

card_directory = f'C:\\Users\\DELL\\Downloads\\aaa'  # 替换为你的md文件目录


# 正则表达式，用于识别Markdown中的图片标签
question_pattern = re.compile(r'^\s*#\s*(\S.*\S)+[\r\n]')
date_pattern = re.compile(r'[^\r\n]*Date:\s*(\S.*\S)\s*[\r\n]')
tag_pattern = re.compile(r'[^\r\n]*Tag:\s*(\S.*\S)\s*[\r\n]')
action_pattern = re.compile(r'[^\r\n]*Action:\s*(\S.*\S)\s+\((\S.*\S)\)\s*[\r\n]')
code_pattern = re.compile(r'```(.*?)\n(.*?)```', re.DOTALL)
image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')


# 列出Markdown文件，并为每个文件生成一张卡片
card_dict = {}
for filename in os.listdir(card_directory):
    if filename.endswith(".md"):
        file_path = os.path.join(card_directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            question_match = question_pattern.match(content)
            if question_match:
                question = question_match.group(1)
                content = question_pattern.sub('', content)
            else:
                question = ''

            date_match = date_pattern.search(content)
            if date_match:
                content = date_pattern.sub('', content)
            else:
                date = ''

            tag_match = tag_pattern.search(content)
            if tag_match:
                tag = tag_match.group(1)
                content = tag_pattern.sub('', content)
            else:
                tag = 'default'

            action_match = action_pattern.search(content)
            if action_match:
                action_name, action_link = action_match.group(1,2)
                content = action_pattern.sub('', content)
            else:
                action_name, action_link = '', ''
            notion = f'<a href="{action_link}">{action_name}</a>'

            code_match = code_pattern.search(content)
            if code_match:
                content = code_pattern.sub(r'<pre><code class="\1">\2</code></pre>', content)

            # 查找并替换Markdown中的图片路径
            image_paths = re.findall(image_pattern, content)
            for image_path in image_paths:
                image_abs_path = os.path.abspath(urllib.parse.unquote(os.path.join(card_directory, image_path)))
                if pathlib.Path(image_abs_path).is_file():
                    image_file_name = os.path.join(media_path, os.path.split(image_abs_path)[-1])
                    shutil.copy(image_abs_path, image_file_name)
                else:
                    print(f'File not found or invalid: {image_abs_path}')

            # 将Markdown内容转换为HTML
            answer = markdown.markdown(content, output_format='html')

            if tag not in card_dict:
                card_dict[tag] = set()
            card_dict[tag].add((question, answer, notion))


deck_dict = {
    'default': 100000000,
    'Python':  100000001,
    'DFT':     100000002,
    'SOC':     100000003,
    'STA':     100000004,
    'CPU':     100000005,
}


for deck_name, note_set in card_dict.items():
    if deck_name not in deck_dict.keys():
        deck_dict[deck_name] = max(deck_dict.values()) + 1

    tmp_deck = genanki.Deck(deck_dict[deck_name], deck_name)
    for aa in note_set:
        note = genanki.Note(
            model=notion_template.notion2anki,
            fields=aa,
            tags=[tag, ],
        )
        tmp_deck.add_note(note)
    anki_package = genanki.Package(tmp_deck)
    output_file = os.path.join('output', f'{deck_name}.apkg')
    print(f"Anki deck with images has been created and saved as {output_file}")
    anki_package.write_to_file(output_file)


print(f'deck_dict = {deck_dict}')

