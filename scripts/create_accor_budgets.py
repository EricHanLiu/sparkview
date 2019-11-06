import os
import django
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from budget.models import Budget, Client


def main():
    accor = Client.objects.get(id=98)

    data = {
        'london': [
            {
                'loc': 'na',
                'budget': 6000
            }, {
                'loc': 'aus/nz',
                'budget': 3000
            }, {
                'loc': 'me',
                'budget': 4000
            }, {
                'loc': 'asia',
                'budget': 3000
            }, {
                'loc': 'france',
                'budget': 3000
            }, {
                'loc': 'euro',
                'budget': 2000
            }, {
                'loc': 'sa',
                'budget': 1500
            }],
        'nyc': [
            {
                'loc': 'uk',
                'budget': 2000
            }, {
                'loc': 'na',
                'budget': 3500
            }, {
                'loc': 'aus/nz',
                'budget': 2500
            }, {
                'loc': 'me',
                'budget': 1500
            }, {
                'loc': 'asia',
                'budget': 1000
            }, {
                'loc': 'france',
                'budget': 500
            }, {
                'loc': 'euro',
                'budget': 2500
            }, {
                'loc': 'sa',
                'budget': 1500
            }
        ],
        'paris': [
            {
                'loc': 'uk',
                'budget': 1000
            }, {
                'loc': 'na',
                'budget': 2000
            }, {
                'loc': 'aus/nz',
                'budget': 1500
            }, {
                'loc': 'me',
                'budget': 1000
            }, {
                'loc': 'asia',
                'budget': 1000
            }, {
                'loc': 'france',
                'budget': 1500
            }, {
                'loc': 'euro',
                'budget': 2000
            }, {
                'loc': 'sa',
                'budget': 2000
            }
        ],
        'la': [
            {
                'loc': 'uk',
                'budget': 500
            },
            {
                'loc': 'na',
                'budget': 1000
            }, {
                'loc': 'aus/nz',
                'budget': 1000
            }, {
                'loc': 'me',
                'budget': 500
            }, {
                'loc': 'asia',
                'budget': 500
            }, {
                'loc': 'france',
                'budget': 500
            }, {
                'loc': 'euro',
                'budget': 500
            }, {
                'loc': 'sa',
                'budget': 500
            }
        ]
    }

    for key in data:
        current_city = key
        for region_dict in data[key]:
            loc = region_dict['loc']
            budget = region_dict['budget']
            include_strings = current_city + '&' + loc
            exclude_strings = 'brand,rm,b_ho'
            if len(current_city) < 4:
                name = 'OFS - ' + current_city.upper() + ' - ' + loc.title() + ' - Google ONLY'
            else:
                name = 'OFS - ' + current_city.title() + ' - ' + loc.title() + ' - Google ONLY'
            Budget.objects.create(account=accor, has_adwords=True, grouping_type=1, text_includes=include_strings,
                                  text_excludes=exclude_strings, is_monthly=True, name=name, budget=budget)
            print('Making budget ' + name)


main()
