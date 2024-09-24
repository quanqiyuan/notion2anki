import shutil
import genanki
import markdown
import re
import os
import pathlib
import urllib.parse


# 定义一个包含图片的Anki卡片模型
notion2anki = genanki.Model(
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
            'afmt': '''{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Notion}}
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-material.css" />
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
            ''',
        },
    ],
    css='''
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
        pre {
            background: #282c34;
            color: #abb2bf;
            padding: 10px;
            border-radius: 5px;
            overflow: auto;
            font-family: 'Courier New', Courier, monospace; /* 等宽字体 */
        }
        code {
            color: #61afef;
            font-family: 'Courier New', Courier, monospace; /* 等宽字体 */ 
        }
    '''
)


# 列出Markdown文件，并为每个文件生成一张卡片
def notion2anki_windows(notion_directory, media_directory):
    # 正则表达式，用于识别Markdown中的图片标签
    question_pattern = re.compile(r'^\s*#\s*(\S.*\S)+[\r\n]')
    date_pattern = re.compile(r'[^\r\n]*Date:\s*(\S.*\S)\s*[\r\n]')
    tag_pattern = re.compile(r'[^\r\n]*Tag:\s*(\S.*\S)\s*[\r\n]')
    action_pattern = re.compile(r'[^\r\n]*Action:\s*(\S.*\S)\s+\((\S.*\S)\)\s*[\r\n]')
    code_pattern = re.compile(r'```(.*?)\n(.*?)```', re.DOTALL)
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    cards = {}
    for filename in os.listdir(notion_directory):
        if filename.endswith(".md"):
            file_path = os.path.join(notion_directory, filename)
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

                tag_match = tag_pattern.search(content)
                if tag_match:
                    tag = tag_match.group(1)
                    content = tag_pattern.sub('', content)
                else:
                    print(f'!!! {filename} is not tagged.')

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
                    content = re.sub(image_path, urllib.parse.unquote(image_path), content)
                    image_abs_path = os.path.abspath(urllib.parse.unquote(os.path.join(notion_directory, image_path)))
                    if pathlib.Path(image_abs_path).is_file():
                        image_file_name = os.path.join(media_directory, os.path.split(image_abs_path)[-1])
                        shutil.copy(image_abs_path, image_file_name)
                    else:
                        print(f'File not found or invalid: {image_abs_path}')

                # 将Markdown内容转换为HTML
                answer = markdown.markdown(content, output_format='html')

                if tag not in cards:
                    cards[tag] = set()
                cards[tag].add((question, answer, notion))
    return cards


deck_dict = {'default': 100000000, 'Python': 100000001, 'DFT': 100000002, 'SOC': 100000003, 'STA': 100000004, 'CPU': 100000005}
