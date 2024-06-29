# main window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# USER DATA CONFIG
# data directory
user_data_dir = 'unichat-user-data'
# log directory
log_dir = 'logs'
# database name
db_name = 'unichat.db'
telegram_sync_session = 'telethon_sync'
telegram_async_session = 'telethon_async'

# INSTAGRAM SELENIUM CONFIG
instagram_url = 'https://www.instagram.com/'
instagram_message_url = "https://www.instagram.com/direct"
instagram_me = "You sent"

instagram_element = dict(
    login_form="loginForm",
    login_fields="_aa4b._add6._ac4d._ap35",
    login_button="_acan._acap._acas._aj1-._ap30",
    decline_cookies="_a9--._ap36._a9_1",
    decline_notifications="_a9--._ap36._a9_1",
    contacts="x9f619.x1n2onr6.x1ja2u2z.x1qjc9v5.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k.xeuugli.xxsgkw5",
    name="x6s0dn4.x1bs97v6.x1q0q8m5.xso031l.x9f619.x78zum5.x1q0g3np.xr931m4.xat24cr.x4lt0of.x1swvt13.x1pi30zi.xh8yej3",
    input_box="xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x1iyjqo2.x1gh3ibb.xisnujt.xeuugli.x1odjw0f.notranslate",
    all_msgs="x1n2onr6",
    date="x186z157.xk50ysn",
    msg_blob="x78zum5.xdt5ytf",
    my_msgs="html-div.xe8uvvx.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a.xyk4ms5",
    other_msgs="html-div.xe8uvvx.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a.x18lvrbx",
    msg_blobs="x78zum5 xdt5ytf",
    own_msg="html-div xe8uvvx xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a xyk4ms5",
    other_msg="html-div xe8uvvx xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a x18lvrbx",
    msg_time="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1pg5gke xvq8zen xo1l8bm x12scifz",
    msg_sender="html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs xzpqnlu x1hyvwdk xjm9jq1 x6ikm8r x10wlt62 x10l6tqk x1i1rx1s",
    chat_window="x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt"
)

# WHATSAPP SELENIUM CONFIG
whatsapp_url = 'https://web.whatsapp.com/'

timeout_limit = 60
timeout_limit_short = 5

logged_in = "logged in"

driver_new_page = "chrome://new-tab-page/"

whatsapp_element = dict(
    static_element="wa-popovers-bucket",
    initial_startup="wa_web_initial_startup",
    qr_code="_akau",
    qr_code_data="data-ref",
    chat_search_box="x1hx0egp.x6ikm8r.x1odjw0f.x6prxxf.x1k6rcq7.x1whj5v",
    chat_search_box_cancel="_ah_y",
    chat_list="x1n2onr6._ak9y",
    chat_list_item="_ak8q",
    chat_container="_ajyl",
    chat_window="x3psx0u.xwib8y2.xkhd6sd.xrmvbpv",
    chat_window_oldmsg="_ajvp",
    chat_message_block="x9f619.x1hx0egp.x1yrsyyn",
    chat_message_content="copyable-text",
    chat_message_data="data-pre-plain-text",
    chat_message_text="_akbu",
    chat_message_box="_ak1l",
    chat_message_box_upload_window="x1hx0egp.x6ikm8r.x1odjw0f.x1k6rcq7.x1lkfr7t",
    chat_attachment_clip_button="x11xpdln.x1d8287x.x1h4ghdb",
    profile_element="x1n2onr6.x14yjl9h.xudhj91.x18nykt9.xww2gxu",
    username="_alcd"
)

discord_url = "https://discord.com/login"
message_url = "https://discord.com/channels/@me"

discord_element = dict(
    zustimmen="",
    login_form="mainLoginContainer_f58870",
    login_field_username_or_telnr="email",
    login_field_password="password",
    login_button="marginBottom8_ce1fb9.button__5573c.button__581d0.lookFilled__950dd.colorBrand__27d57.sizeLarge_b395a7.fullWidth_fdb23d.grow__4c8a4",
    avatar_container="container_debb33",
    pop_up_after_login="focusLock__28507",
    pop_up_close_button="closeButton_a24c51.close__1080c.button__581d0.lookBlank_a5b4ca.colorBrand__27d57.grow__4c8a4",
    message_box="markup_a7e664.editor__66464.slateTextArea_b19976.fontSize16Padding_bcbeae",
    qr_code_container="qrCodeOverlay_ae8574"
)
