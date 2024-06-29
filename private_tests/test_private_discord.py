# import time
# import os
# import sys
# from unichat.clients.discord_client.discord_web_client import DiscordClient
#
# USERNAME = "<SECRET>"
# PASSWORD = "<SECRET>"
#
# def test_login():
#     client = DiscordClient(headless=False)
#     login_result = client.login_to_discord(client.DRIVER, USERNAME, PASSWORD)
#     print(login_result)
#     time.sleep(13)
#     client.DRIVER.quit()
#
#     return client
#
# if __name__ == "__main__":
#     client = DiscordClient(headless=False)
#     chats = client.retrieve_all_active_chats(client.DRIVER)
#     messages = client.retrieve_message(client.DRIVER, chats[0])
#     print(messages)
