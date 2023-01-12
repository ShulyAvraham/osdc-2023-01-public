import json
import os
import pathlib
from jinja2 import Environment, FileSystemLoader
import requests
import forem
import time

def read_course_json():
    with pathlib.Path(__file__).parent.joinpath('course.json').open() as fh:
        return json.load(fh)

def update_devto_posts(people):
    for person in people:
        if 'posts' not in person:
            continue
        for page in person['posts']:
            #print(page['url'])
            page['details'] = forem.fetch(page['url'])
            time.sleep(0.2) # self imposed rate limit

def render(template, filename, **args):
    templates_dir = pathlib.Path(__file__).parent.joinpath('templates')
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    html_template = env.get_template(template)
    html_content = html_template.render(**args)
    with open(f'_site/{filename}', 'w') as fh:
        fh.write(html_content)


def main():
    if not os.path.exists("_site"):
        os.makedirs("_site")

    mentors = read_json_files('mentors')
    participants = read_json_files('participants')
    course = read_course_json()
    update_devto_posts(mentors)
    update_devto_posts(participants)

    posts = []
    for person in mentors + participants:
        if 'posts' in person:
            posts.extend(person['posts'])

    render('index.html', 'index.html',
        mentors = mentors,
        participants = participants,
        course = course,
        title = course['title'],
    )



def read_json_files(folder):
    people = []
    for filename in os.listdir(folder):
        if filename == '.gitkeep':
            continue
        if not filename.endswith('.json'):
           raise JsonError("file does not end with .json")
        if filename != filename.lower():
            raise Exception(f"filename {filename} should be all lower-case")
        with open(os.path.join(folder, filename)) as fh:
            person = json.load(fh)

        if 'github' not in person:
            raise Exception(f"github field is missing from {filename}")
        if person['github'].lower() != filename[:-5]:
            raise Exception(f"value of github fields '{person['github']}' is not the same as the filename '{filename}'")


        people.append(person)
    return people

def check_github_acc_for_participant(url: str) -> bool:
    print(url)
    # params: URL of the participant for github.
    headers = {'Accept-Encoding': 'gzip, deflate'}
    r = requests.head(url, headers=headers)
    return r.status_code == requests.codes.ok

if __name__ == "__main__":
    main()

class JsonError(Exception):
    pass
