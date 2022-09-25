import re


def song_to_url(authors, name):
    PRE = "https://api.soundloaders.com/files/"
    REPLACE_SPACE = "%20"

    main_authors = [author for author in authors if author not in name]
    authors_joined = ", ".join(main_authors) if len(
        main_authors) > 1 else main_authors[0]

    formatted_name = re.sub(r":", "%20-%20", name)
    joined = f"{PRE}{authors_joined} - {formatted_name}.mp3"
    formatted_joined = re.sub(r"\"", "", joined)
    return formatted_joined.replace(" ", REPLACE_SPACE)
