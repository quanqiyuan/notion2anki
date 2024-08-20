import shutil
import genanki
import markdown
import re
import os
import pathlib
import urllib.parse

# 定义要处理的Markdown文件路径和图片文件目录
card_directory = f'/Users/quanqiyuan/Downloads/8876b2e2-1a03-41e1-95d1-f71ab79c1064_Export-1f9d64db-f054-4436-a6e9-c2a2bffec50c'  # 替换为你的md文件目录
media_directory = f'/Users/quanqiyuan/Library/Application Support/Anki2/qy.quan/collection.media'

# 创建一个新的Anki牌组
deck_id = 2059400112
deck_name = "Notion2Anki"
my_deck = genanki.Deck(deck_id, deck_name)

# 定义一个包含图片的Anki卡片模型
my_model = genanki.Model(
    1607392322,
    'Notion2Anki',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Notion'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Notion}}',
        },
    ],
    css="""
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        a {
            color: blue;
        }  # 使链接以蓝色显示
        img {
            max-width: 100%;  # 确保图片不会超过卡片宽度
            height: auto;  # 保持图片原始宽高比
        }
    """
)

# 正则表达式，用于识别Markdown中的图片标签
image_pattern = r'!\[.*?\]\((.*?)\)'

# 列出Markdown文件，并为每个文件生成一张卡片
media_files = []
for filename in os.listdir(card_directory):
    if filename.endswith(".md"):
        file_path = os.path.join(card_directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            question_match = re.match(r'^\s*#\s*(\S.*\S)+[\r\n]', content)
            if question_match:
                question = question_match.group(1)
            else:
                question = os.path.splitext(filename)[0]

            tag_match = re.search(r'Tag:\s*(\S.*\S)\s', content)
            if tag_match:
                tag = tag_match.group(1)
            else:
                tag = ''

            notion_match = re.search(r'Action:\s*(\S.*\S)\s+\((\S+)\)\s', content)
            if notion_match:
                notion_name, notion_link = notion_match.group(1,2)
            else:
                notion_name, notion_link = '', ''
            notion = f'<a href="{notion_link}">{notion_name}</a>'

            image_name = re.sub(r'[^\w\u4e00-\u9fff]','', question)[:10]

            # 查找并替换Markdown中的图片路径
            image_paths = re.findall(image_pattern, content)
            for n, image_path in enumerate(image_paths):
                image_abs_path = os.path.abspath(urllib.parse.unquote(os.path.join(card_directory, image_path)))
                image_file_name = f'{image_name}_{n}'

                # 打印绝对路径以确认
                if pathlib.Path(image_abs_path).is_file():
                    shutil.copy(image_abs_path, os.path.join(media_directory, image_file_name))
                    media_files.append(image_file_name)
                else:
                    print(f"File not found or invalid: {image_abs_path}")

                # 更新内容中的图片路径为文件名
                content = content.replace(image_path, image_file_name)
            content = re.sub(r'^\s*#[\s\S]+Action:\s*(\S.*\S)\s+\(\S+\)\s+', '', content, re.DOTALL)

            # 将Markdown内容转换为HTML
            answer = markdown.markdown(content, output_format='html')

            # 创建一个包含图片的卡片
            note = genanki.Note(
                model=my_model,
                fields=[question, answer, notion],
                tags=[tag,],
            )
            my_deck.add_note(note)

# 创建一个牌组包，并添加媒体文件
my_package = genanki.Package(my_deck)
my_package.media_files = media_files  # 添加所有需要的图片

# 导出牌组
output_file = 'notion2anki.apkg'
my_package.write_to_file(output_file)

print(f"Anki deck with images has been created and saved as {output_file}")
