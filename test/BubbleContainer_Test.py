bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body = BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='請選擇題目類型', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )

QAsort_bubble = BubbleContainer (
                header = BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text='請選擇題目類型', weight='bold', size='xl', color = '#000000')                   
                    ]
                ),
                body = BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action = PostbackAction(label = '詞彙練習', data = 'L', text = '詞彙練習'),
                            color = '#001774',
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '文法練習', data = 'M', text = '文法練習'),
                            color = '#FF595D',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '克漏字練習', data = 'H', text = '克漏字練習'),
                            color = '#FFB54A',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        )
                    ]
                )
            )   
            
            #line_bot_api.reply_message(event.reply_token, buttons_template)  
            message = FlexSendMessage(alt_text="QAsort_bubble", contents = QAsort_bubble)
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
#////////////
,
                    BubbleContainer (
                        direction='ltr',
                        header = BoxComponent(
                            layout='vertical',
                            contents=[
                                TextComponent(text='題目(1/20)', weight='bold', size='lg', align = 'center')                   
                            ]
                        ),
                        body = BoxComponent(
                            layout='vertical',
                            contents=[
                                TextComponent(text='選項(1)', size='xl', align = 'center')
                            ]
                        ),
                        footer = BoxComponent(
                            layout='horizontal',
                            contents=[
                                ButtonComponent(
                                    action = PostbackAction(label = '選項(1)', data = '1', text = '選項(1)'),
                                    color = '#46549B',
                                    style = 'primary'
                                )
                            ]
                        )
                    )





{
  "type": "flex",
  "altText": "Flex Message",
  "contents": {
    "type": "carousel",
    "contents": [
      {
        "type": "bubble",
        "direction": "ltr",
        "header": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "題目(1/20)",
              "size": "lg",
              "align": "center",
              "weight": "bold"
            }
          ]
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "uri",
                "label": "聽題目",
                "uri": "https://linecorp.com"
              },
              "color": "#3B9A9C",
              "margin": "lg",
              "style": "primary"
            },
            {
              "type": "text",
              "text": "選出聽到的答案",
              "size": "md",
              "align": "center"
            },
            {
              "type": "separator",
              "margin": "xxl",
              "color": "#A89F9F"
            },
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "前往下一題",
                "text": "前往下一題",
                "data": "前往下一題"
              },
              "color": "#F29C2B",
              "margin": "xxl",
              "style": "primary"
            }
          ]
        }
      },
      {
        "type": "bubble",
        "direction": "ltr",
        "header": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "選項(1)",
              "size": "xl",
              "align": "center"
            }
          ]
        },
        "hero": {
          "type": "image",
          "url": "https://sw.cool3c.com/article/2018/69de900a-b708-4a5d-8048-c1c89b6819e2.jpg?lossless=1&fm=webp&fit=max&w=1200&h=1200",
          "size": "full",
          "aspectRatio": "1.51:1",
          "aspectMode": "fit"
        },
        "footer": {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "uri",
                "label": "選項(1)",
                "uri": "https://linecorp.com"
              },
              "color": "#46549B",
              "style": "primary"
            }
          ]
        }
      },
      {
        "type": "bubble",
        "direction": "ltr",
        "header": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "選項(2)",
              "size": "xl",
              "align": "center"
            }
          ]
        },
        "hero": {
          "type": "image",
          "url": "https://www.planetorganic.com/images/products/large/1874.jpg",
          "size": "full",
          "aspectRatio": "1.51:1",
          "aspectMode": "fit"
        },
        "footer": {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "uri",
                "label": "選項(2)",
                "uri": "https://linecorp.com"
              },
              "color": "#7E318E",
              "style": "primary"
            }
          ]
        }
      },
      {
        "type": "bubble",
        "direction": "ltr",
        "header": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "選項(3)",
              "size": "xl",
              "align": "center"
            }
          ]
        },
        "hero": {
          "type": "image",
          "url": "https://s3.amazonaws.com/finecooking.s3.tauntonclud.com/app/uploads/2017/04/24172040/ING-grapes-2.jpg",
          "size": "full",
          "aspectRatio": "1.51:1",
          "aspectMode": "fit"
        },
        "footer": {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "uri",
                "label": "選項(3)",
                "uri": "https://linecorp.com"
              },
              "color": "#CD2774",
              "style": "primary"
            }
          ]
        }
      }
    ]
  }
}