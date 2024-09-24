import genanki

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
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Notion}}',
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
    '''
)


deck_dict = {
    'default': 100000000,
    'Python':  100000001,
    'DFT':     100000002,
    'SOC':     100000003,
    'STA':     100000004,
    'CPU':     100000005,
}