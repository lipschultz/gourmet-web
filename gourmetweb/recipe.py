from fractions import Fraction

from flask import (
    Blueprint, Markup, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gourmetweb.db import get_db

bp = Blueprint('recipe', __name__)


def pretty_time(seconds, terse_type='full'):
    assert terse_type in ('full', 'short'), f'Unrecognized value for `terse_type`: {terse_type}'
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    total_time = []
    if hours > 0:
        if terse_type == 'full':
            total_time.append(f'{hours} hour{"s" if hours > 1 else ""}')
        elif terse_type == 'short':
            total_time.append(f'{hours} hr')
    if minutes > 0:
        if terse_type == 'full':
            total_time.append(f'{minutes} minute{"s" if minutes > 1 else ""}')
        elif terse_type == 'short':
            total_time.append(f'{minutes} min')
    if seconds > 0:
        if terse_type == 'full':
            total_time.append(f'{seconds} second{"s" if seconds > 1 else ""}')
        elif terse_type == 'short':
            total_time.append(f'{seconds} sec')

    if terse_type in ('full', 'short'):
        return ' '.join(total_time)


def pretty_number(value):
    if value is None:
        return ''

    whole_number = int(value)
    fractional_number = value % 1
    if fractional_number == 0:
        return str(whole_number)
    else:
        pretty = str(whole_number) if whole_number != 0 else ''
        return  pretty + ' ' + str(Fraction(fractional_number).limit_denominator(8))


def get_pretty_ingredients(db, recipe_id):
    ingredients = db.execute(
        'SELECT position, amount, rangeamount, unit, item, optional, inggroup'
        ' FROM ingredients'
        ' WHERE recipe_id=?',
        (recipe_id, )
    ).fetchall()

    ingredients_sorted = []
    for ingr in ingredients:
        ingr_parts = []
        amount_pretty = pretty_number(ingr['amount'])
        if ingr['rangeamount'] is not None:
            amount_pretty += ' - ' + pretty_number(ingr['rangeamount'])
        if len(amount_pretty) > 0:
            ingr_parts.append(amount_pretty)

        if ingr['unit'] is not None:
            ingr_parts.append(ingr['unit'])
        
        ingr_parts.append(ingr['item'])
        ingredient = ' '.join(ingr_parts)

        ingredients_sorted.append((
            ingr['position'],
            ingr['inggroup'] if ingr['inggroup'] is not None else '',
            {'ingredient': ingredient,
             'optional': ingr['optional'] != 0
            }
        ))
    ingredients_sorted.sort()

    # Get order of ingredient groups
    group_order = []
    for i in ingredients_sorted:
        group = i[1]
        if group not in group_order:
            group_order.append(group)

    group_ingredients_pretty = []
    for group in group_order:
        group_ingredients = []
        for i in ingredients_sorted:
            if i[1] == group:
                group_ingredients.append(i[2])
        group_ingredients_pretty.append((group, group_ingredients))
    
    return group_ingredients_pretty


def get_pretty_instructions(instructions):
    return [Markup(i) for i in instructions.splitlines() if len(i.strip()) > 0]


def get_pretty_notes(notes):
    return [Markup(i) for i in notes.splitlines() if len(i.strip()) > 0]


def get_pretty_category(db, recipe_id):
    category = db.execute(
        'SELECT category'
        ' FROM categories'
        ' WHERE recipe_id=?',
        (recipe_id, )
    ).fetchone()
    return category['category'] if category is not None else ''


def get_pretty_rating(rating):
    if rating == 0:
        return ''

    pretty = '★' * int(rating / 2)
    pretty += '◐' if rating % 2 == 1 else ''
    pretty += '☆' * (5 - int(rating / 2 + 0.5))
    return pretty


@bp.route('/')
def index():
    db = get_db()
    recipes = db.execute(
        'SELECT id, title, rating, yields, yield_unit, preptime,'
        ' cooktime, cuisine'
        ' FROM recipe'
    ).fetchall()

    all_data = []
    for recipe in recipes:
        data = dict(**recipe)
        print(data)
        data['category'] = get_pretty_category(db, recipe['id'])
        data['total_time'] = pretty_time(
            (0 if data['preptime'] is None else data['preptime'])
            + (0 if data['cooktime'] is None else data['cooktime']),
            terse_type='short')
        data['rating_pretty'] = get_pretty_rating(0 if recipe['rating'] is None else recipe['rating'])
        all_data.append(data)

    return render_template('recipe/index.html', recipes=all_data)


@bp.route('/<int:recipe_id>/')
def recipe(recipe_id):
    db = get_db()

    recipe = db.execute(
        'SELECT title, rating, yields, yield_unit, preptime, cooktime,'
        ' instructions, modifications, cuisine, link'
        ' FROM recipe'
        ' WHERE id=?',
        (recipe_id, )
    ).fetchone()

    if recipe is None:
        abort(404, "Recipe id {0} doesn't exist.".format(recipe_id))

    data = dict(**recipe)

    data['yields_pretty'] = pretty_number(data['yields'])
    data['preptime_pretty'] = pretty_time(data['preptime'])
    data['cooktime_pretty'] = pretty_time(data['cooktime'])
    data['instructions_pretty'] = get_pretty_instructions(data['instructions'])
    data['notes_pretty'] = get_pretty_notes(data['modifications'])
    data['rating_pretty'] = get_pretty_rating(data['rating'])

    data['category'] = get_pretty_category(db, recipe_id)    
    data['ingredients_pretty'] = get_pretty_ingredients(db, recipe_id)
    
    return render_template('recipe/recipe.html', recipe=data)
