"""
$ mkvirtualenv tlbhit
$ pip3 install -r requirements.txt
$ python3 render.py
"""

import os

import mistune


EPISODE_NOTES_DIR = 'episode_notes'


def main():
    with open('episode_header.tmpl') as header:
        header_contents = header.read()
    with open('episode_footer.tmpl') as footer:
        footer_contents = footer.read()

    for filename in os.listdir(EPISODE_NOTES_DIR):
        base, ext = os.path.splitext(filename)
        if ext != '.md':
            continue

        audio = None
        with open(os.path.join(EPISODE_NOTES_DIR, filename)) as f:
            lines = f.readlines()
            title = lines[0]
            lines = lines[1:]   # Slice off the title.
            # Don't escape the <audio> tag.
            for line in lines:
                if line.startswith('<audio '):
                    audio = line
            lines = [line for line in lines if not line.startswith('<audio ')]
            contents = ''.join(lines)

        title = mistune.markdown(title)
        guts = mistune.markdown(contents)

        with open(base + '.html', 'w') as file:
            file.write("<!-- DO NOT EDIT -- episode notes autogenerated by TLBHit's render.py -->\n")
            file.write(header_contents)
            file.write(title)
            if audio is not None:
                file.write(audio)
            file.write(guts)
            file.write(footer_contents)


if __name__ == '__main__':
    main()