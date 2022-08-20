import os
from jinja2 import Environment, FileSystemLoader


def clean_dir():
    current_path = os.path.abspath(os.getcwd())

def main(news_section):
    clean_dir()
    current_path = os.path.abspath(os.getcwd())
    minutes_by_hour = 40
    env = Environment(loader = FileSystemLoader(current_path), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('DAG_template.py')
    for count, element in enumerate(news_section, start = 1):
        values = {}
        if count % 5 == 0:
            minutes_by_hour += 2
        values['section_name'] = element
        values['minutes_by_hour'] = minutes_by_hour
        values['article_limit'] = 40
        # print(template.render(values))
        file=open(current_path + f"/dags/NYT_Scraping_{element}.py", "w")
        file.write(template.render(values))
        file.close()
        

if __name__ == "__main__":
    news_section = [ 'arts',
                'automobiles',
                'books',
                'business',
                'climate',
                'education',
                'fashion',
                'food',
                'health',
                # 'job+market',
                'science',
                'sports',
                'technology',
                'travel',
                # 'u.s.',
                'universal',
                'world'
            ]
    main(news_section)
