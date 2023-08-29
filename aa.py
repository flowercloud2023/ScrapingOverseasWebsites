import instaloader


# https://github.com/instaloader/instaloader
# https://instaloader.github.io/
L = instaloader.Instaloader()

# Login or load session
username = ""
password = ""
L.login(username, password)  # (login)

# Obtain profile metadata
profile = instaloader.Profile.from_username(L.context, 'vi_hair_')

# 爬取所有评论
for p in profile.get_posts():
    print('文案', p.caption)
    for c in p.get_comments():
        # 评论
        print(c.text)
        print(c.created_at_utc)
        print(c.likes_count)
        print(c.likes_count)

# Print list of followees
follow_list = []
count = 0
for followee in profile.get_followers():
    follow_list.append(followee.username)
    file = open("followers.txt", "a+")
    file.write(follow_list[count])
    file.write("\n")
    file.close()
    print(follow_list[count])
    count = count + 1
